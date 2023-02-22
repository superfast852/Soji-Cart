'''
Motor Driver Logic:
    Pins: Direction, Speed

    PWM/DIR = Outputs (MxA/B)
    0/x = 0-0 (Brake)
    1/0 = 1-0 (Forward)
    1/1 = 0-1 (Reverse)
'''

# TODO: Integrate battery sensor, Integrate ultrasonic sensor, Integrate comms.
from RPi import GPIO
from adafruit_servokit import ServoKit
from math import floor
import time
from adafruit_ina219 import INA219
import board
import busio

GPIO.setmode(GPIO.BCM)

class Drive:
    def __init__(self, left_dir_pin, left_speed_pin, right_dir_pin, right_speed_pin):
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

class Arm:
    def __init__(self, num_servos):
        self.kit = ServoKit(channels=8 if num_servos >= 8 else 16)
        self.pose = [0] * num_servos
        self.arm = [self.kit.servo[i] for i in range(num_servos)]
        self.move(self.pose)

    def move(self, pose):
        for i, angle in enumerate(pose):
            try:
                self.arm[i].angle = angle
                self.pose[i] = angle
            except IndexError:
                print(f"Servo {i} does not exist.")
                return None

class Lidar:
    def __init__(self, lidar, baudrate=115200, timeout=1):
        from adafruit_rplidar import RPLidar
        self.sim_ctr = -1
        self.lidar = RPLidar(None, lidar, baudrate, timeout)
        self.scan_data = [0] * 360

    def get_scan(self):
        for scan in self.lidar.iter_scans():
            for _, angle, distance in scan:
                self.scan_data[min(359, floor(angle))] = distance
            return self.scan_data

    def clean_up(self):
        self.lidar.stop()
        self.lidar.disconnect()

class Battery:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ina = INA219(self.i2c)

    def read(self):
        return self.ina.bus_voltage+self.ina.shunt_voltage, self.ina.current

class Ultrasonic:
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

class Encoders:
    def __init__(self, pins):
        self.encoders = [GPIO.setup(i, GPIO.IN) for i in pins]
        self.counter_thread = None
        self.count = None

    def get(self):
        pass

    def calc_tics(self):
        pass
