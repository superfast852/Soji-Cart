'''
Motor Driver Logic:
    Pins: Direction, Speed

    PWM/DIR = Outputs (MxA/B)
    0/x = 0-0 (Brake)
    1/0 = 1-0 (Forward)
    1/1 = 0-1 (Reverse)
'''

# TODO: Integrate battery sensor, Integrate ultrasonic sensor, Integrate comms.
try:
    from RPi import GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
except ImportError:
    pass
import time

#from threading import Thread


def smoothSpeed(current, target, speed_lim=1, min_speed=0.1, smoothing_spread=10):
    distance = current-target
    try:
        direction = -distance/abs(distance)
        speed = min(9, (distance/10)**2/smoothing_spread)
        output = (1+speed)*direction/10*speed_lim
        return output if abs(output) > min_speed else min_speed*direction
    except ZeroDivisionError:
        return 0


class Drive:
    def __init__(self, left_dir_pin=16, left_speed_pin=12, right_dir_pin=21, right_speed_pin=20):
        GPIO.setup(left_speed_pin, GPIO.OUT)
        self._l_pwm = GPIO.PWM(left_speed_pin, 1000)
        self._l_pwm.start(0)
        GPIO.setup(right_speed_pin, GPIO.OUT)
        self._r_pwm = GPIO.PWM(right_speed_pin, 1000)
        self._r_pwm.start(0)
        print("PWM Started.")
        GPIO.setup(left_dir_pin, GPIO.OUT)
        GPIO.setup(right_dir_pin, GPIO.OUT)
        GPIO.output(left_dir_pin, 0)
        GPIO.output(right_dir_pin, 0)

        self.left_dir = lambda x: GPIO.output(left_dir_pin, x)
        self.left_speed = lambda x: self._l_pwm.ChangeDutyCycle(x)
        self.right_dir = lambda x: GPIO.output(right_dir_pin, x)
        self.right_speed = lambda x: self._r_pwm.ChangeDutyCycle(x)
        print("INIT Done.")

    def setLeftSpeed(self, speed):
        if speed > 0:
            self.left_dir(1)
            self.left_speed(speed)
        elif speed < 0:
            self.left_dir(0)
            self.left_speed(-speed)
        else:
            self.left_dir(0)
            self.left_speed(0)

    def setRightSpeed(self, speed):
        if speed > 0:
            self.right_dir(1)
            self.right_speed(speed)
        elif speed < 0:
            self.right_dir(0)
            self.right_speed(-speed)
        else:
            self.right_dir(0)
            self.right_speed(0)

    def brake(self):
        self.left_dir(0)
        self.left_speed(0)
        self.right_dir(0)
        self.right_speed(0)

    def exit(self):
        self.brake()
        GPIO.cleanup()

    def set(self, leftSpeed, rightSpeed):
        self.setLeftSpeed(leftSpeed)
        self.setRightSpeed(rightSpeed)

    def test(self):
        for i in range(1000):
            self.set(100, 100)
        self.brake()
        for i in range(1000):
            self.set(-100, -100)
        self.brake()
        return 1


class Arm:
    def __init__(self, num_servos=6, smoothness=10):
        from adafruit_servokit import ServoKit
        self.kit = ServoKit(channels=8 if num_servos >= 8 else 16)
        self.pose = [0] * num_servos
        self.smoothness = smoothness
        self.arm = [self.kit.servo[i] for i in range(num_servos)]
        self.home = [90, 75, 130, 90, 0, 0]
        self.grabbing = [90, 10, 90, 120, 150, 180]
        self.dropping = [90, 90, 50, 0, 150, 0]
        self.test(self.home)

    def grab(self):
        self.pose[-1] = 0
        self.arm[-1].angle = 0

    def drop(self):
        self.pose[-1] = 180
        self.arm[-1].angle = 180

    def grab_item(self, side=0, period=0.5):
        if side == 1:
            self.arm[4].angle = 90
            time.sleep(0.1)
            self.grabbing[4] = 90
        self.move(self.grabbing)
        self.grab()
        time.sleep(period)
        self.move(self.dropping)
        self.drop()
        time.sleep(period)
        self.move(self.home)
        self.grabbing[4] = 150

    def test(self, pose=None, timestep=0.1):
        if pose == None:
            pose = self.pose
        # TODO: Add smoothSpeed
        for i, angle in enumerate(pose):
            try:
                # step = smoothSpeed(self.pose[i], angle, 1, 0.1)
                self.arm[i].angle = angle
                time.sleep(timestep)
                self.pose[i] = angle
            except IndexError:
                print(f"Servo {i} does not exist.")
                return None

    def move(self, pose):
        while self.pose != pose:
            for i, joint in enumerate(self.arm):
                position = int(smoothSpeed(self.pose[i], pose[i], 10, 1, self.smoothness))
                self.pose[i] += position
                joint.angle = self.pose[i]
                time.sleep(0.005)



class Battery:
    # TODO: check if this works.
    def __init__(self):
        from adafruit_ina219 import INA219
        import board
        import busio
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ina = INA219(self.i2c)

    def read(self):
        return self.ina.bus_voltage+self.ina.shunt_voltage, self.ina.current

    def test(self, threshold=(11.1, 12.6)):
        for i in range(5):
            if threshold[0]<self.read()[0]<=threshold[1]:
                return 0
        return 1


class Ultrasonic:
    # TODO: Check if it works.
    def __init__(self, echo, trig):  # 11, 8
        self.echo = echo
        self.trig = trig
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.setup(self.trig, GPIO.OUT)

    def _get_val(self):
        # set Trigger to HIGH
        GPIO.output(self.trig, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

        StartTime = time.time()
        StopTime = time.time()

        # save StartTime
        while GPIO.input(self.echo) == 0:
            StartTime = time.time()

        # save time of arrival
        while GPIO.input(self.echo) == 1:
            StopTime = time.time()

        distance = ((StopTime-StartTime) * 34300) / 2

        return distance

    def read(self, measures=5):
        return sum([self._get_val() for i in range(measures)])/measures

    def test(self):
        cache = []
        for i in range(5):
            cache.append(self.read())
        return 1 if (cache[0]-5) < (sum(cache)/len(cache)) < (cache[0]+5) else 0


class Encoder:
    def __init__(self, pins):  # Pins : [[Upper Left, Upper Right], [Lower Left, Lower Right]]
        self.t2d = lambda x: x * 0.213713786  # 2*pi*40mm/1176 = distance per tick in MM. Distance from ticks
        self.d2t = lambda x: round(x*4.679155326)  # 4.679155 = 2*pi*40mm. Ticks from distance
        self.encoders = {str(pin): 0 for half in pins for pin in half}
        self.pins = [[str(pin) for pin in half] for half in pins]
        for half in pins:
            for encoder in half:
                GPIO.setup(encoder, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.add_event_detect(encoder, GPIO.RISING, callback=self.update_encoder)

    def update_encoder(self, pin):
        self.encoders[str(pin)] += 1

    def test(self, motor, encoder=(0, 0), distance=150):
        while self.t2d(self.encoders[self.pins[encoder[0]][encoder[1]]]) < distance:
            motor.setLeftSpeed(100)
            motor.setRightSpeed(100)
        motor.brake()
        return 1


class Magnetometer:

    def __init__(self):
        from qmc5883l import QMC5883L
        self.mag = QMC5883L()

    def read(self):
        return self.mag.get_magnet()

    def read_temp(self):
        return self.mag.get_temp()

    def test(self):
        self.read_temp()
        self.read()
        return 1


class GPS:
    # TODO: Integrate reading, parsing, and async fetching.
    def __init__(self, freq=500):
        from adafruit_gps import GPS
        import serial
        self.uart = serial.Serial("/dev/ttyUSB1", baudrate=9600, timeout=10)
        self.gps = GPS(self.uart, debug=False)
        self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        freq_cmd = f"PMTK220,{1/freq}"
        self.gps.send_command(bytes(freq_cmd))
        self.pos = [None, None]
        self.extra_data = None

    def get_data(self, extra=False):
        if extra:
            return self.pos, self.extra_data
        else:
            return self.pos

    def _update(self):
        while True:
            pass