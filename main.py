# TODO: build in more resilience, comm_based host
from adafruit_rplidar import RPLidarException
from utilities import pi
from utilities.comms import Server
from utilities.utils import animate_and_save
from utilities.collision import check_surroundings, check_collision
from socket import gethostbyname
from atexit import register
from time import process_time
from threading import Thread
from _thread import interrupt_main
from math import floor

# Parameters
collision_space = 19  # Range of angles to check for obstacles in front of car
collision_threshold = 1.5  # Minimum distance for the code to consider as obstacle.
max_speed = 100
scan_error_tolerance = 10
scan_error_point = 0
battery_dead_threshold = 11.3  # 7.4
battery_low_threshold = 11.5
trash_lvl_threshold = 1
spin_intensity = 4  # Divides max_speed by this to spin robot in setCourse()
save = True
scan_save_dir = "/home/gg/PycharmProjects/SojiSim/saves/scans_test"  # Last word is filename
arm_tolerance = 5

# Program variables
collision_bounds = (180 - (collision_space // 2), 180 + (collision_space // 2))
scans = []
wait_id = {}
arm_position = []


scan = [0]*360
serv = Server(gethostbyname("soji.local"), 9160)
print("Connecting...")
conn, addr = serv.connect()
print("Connected to", addr)

# Control Systems
motors = pi.Drive(21, 20, 16, 12)  # Motor A = Left, Motor B = Right, P1 = Direction, P2 = Speed. Change to BCM numbering.
battery = pi.Battery()
motors.brake()
lidar = pi.Lidar("/dev/ttyUSB0")
trash_lvl = pi.Ultrasonic(11, 9)
arm_distance = pi.Ultrasonic(8, 7)
arm = pi.Arm(8)

# TODO: Insert Encoders, Insert Comms, Insert Arm, Insert AI
# On testing controller, here goes camera

# Class instantiations.

def wait(time, do_something=lambda x=5: None, args=None):
    # Wait for a certain amount of time.
    # You can set multiple waits, as long as they have different times.
    try:

        time_stamp = wait_id[str(time)]
    except KeyError:
        time_stamp = wait_id[str(time)] = process_time()

    if process_time() - time_stamp >= time:
        wait_id.pop(str(time))
        do_something(args) if args else do_something()
        del time_stamp
        return 1
    else:
        return 0

def set_course(lidar_data):
    if check_collision(lidar_data, collision_bounds, collision_threshold):  # Check for obstacles ahead

        # If there is an obstacle...
        direction, angles = check_surroundings(lidar_data, collision_threshold)  # Find out the clearest side
        if direction == "Left":
            motors.setLeftSpeed(max_speed/spin_intensity)
            motors.setRightSpeed(max_speed)
        else:
            motors.setLeftSpeed(max_speed)
            motors.setRightSpeed(max_speed/spin_intensity)
        return direction, angles  # Return the direction and the angles of the obstacle for future optional odometry.

    else:
        motors.setLeftSpeed(max_speed)
        motors.setRightSpeed(max_speed)
        return "Forward", collision_bounds

def exit_handle():
    motors.exit()
    lidar.clean_up()
    async_thread.join()  # TODO: Fix this!
    if save:
        animate_and_save(scans, filename=scan_save_dir, bounds=collision_bounds)
    print("Clean exit. Robot stopped.")

def async_ops(check_period=30):
    from time import sleep
    trash_lvl_check = 0
    while True:
        current_trash_lvl = trash_lvl.read()
        bat_lvl = battery.read()

        if current_trash_lvl<=trash_lvl_threshold and trash_lvl_check >= 10:
            print("Trash LVL Threshold Reached.")
            break
        else:
            trash_lvl_check += 1

        if bat_lvl <= battery_dead_threshold:
            break
        elif bat_lvl <= battery_low_threshold:
            print("WARNING: BATTERY LOW")
        sleep(check_period)
    interrupt_main()

def grab():
    # TODO: Check for comms integrity
    # while arm is not centered enough

    # PHASE 1: CAR ALIGNMENT
    c2c = serv.rx(conn)  # Get initial center-to-center distance.
    serv.tx("received", conn)  # TODO: move arm to 90 degrees, aka center.
    try:
        while abs(c2c) > arm_tolerance:  # TODO: if the arm leaves center of image in detection, spin until a C2C is obtained.
            spin = "left" if c2c < 25 else "right" if c2c > 25 else "center"
            if spin == "left":
                # Move cart to left until its in center
                motors.setLeftSpeed(max_speed/spin_intensity)
                motors.setRightSpeed(max_speed/(spin_intensity/2))
                pass
            elif spin == "right":
                # Move cart to right until its in center
                motors.setLeftSpeed(max_speed/(spin_intensity/2))
                motors.setRightSpeed(max_speed/spin_intensity)
                pass

            c2c = serv.rx(conn)  # Get new C2C
            serv.tx("received", conn)

        # PHASE 2: CLOSE-IN
        motors.setLeftSpeed(max_speed / spin_intensity)
        motors.setRightSpeed(max_speed / spin_intensity)
        while arm_distance.read() > 10:
            center_arm()  # TODO: Implement center_arm.
        motors.brake()
        # When while loop is completed, grab item

        # PHASE 3: COLLECTION
        _grab_item()
        serv.rx(conn)
        serv.tx("grabbed", conn)
        # and continue
    except Exception as e:
        print(e)
        pass

def _grab_item():
    # Remember to include the return-to-home code.
    arm.move([0, 0, 0, 0])

def grabV2():
    c2c = serv.rx(conn)  # Get initial center-to-center distance.
    while 80<=arm_position[0]<=100:  # Phase 1: Car Alignment
        if abs(c2c) < 25:
            motors.setLeftSpeed(max_speed/spin_intensity)
            motors.setRightSpeed(max_speed/(spin_intensity/2))
        elif abs(c2c) > 25:
            motors.setLeftSpeed(max_speed/(spin_intensity/2))
            motors.setRightSpeed(max_speed/spin_intensity)
        c2c = serv.rx(conn)
        serv.tx("received", conn)
    motors.brake()

    while 80<=arm_position[1]<=100:
        motors.setLeftSpeed(max_speed/spin_intensity)
        motors.setRightSpeed(max_speed/spin_intensity)
    _grab_item()

def on_timer(info):
    print(info)

def center_arm():
    pass

# Preloop preparations.
register(exit_handle)  # Register exit handler
async_thread = Thread(target=async_ops)
async_thread.start()
# Main Loop
while True:
    try:
        for frame in lidar.lidar.iter_scans():
        # TODO: add arm control
            for _, angle, distance in frame:
                scan[min(359, floor(angle))] = distance
            # Data Fetching
            position, center = serv.rx(conn)
            if center:
                serv.tx("received", conn)
                motors.brake()
                grab()
            else:
                arm.move(position)
                serv.tx(scan, conn)  # Here, you can send any relevant cart data. [scans, battery, trash, etc.]

            # Data Processing
            if scan.count(scan_error_point) < scan_error_tolerance:  # Check for bad scans (how many 0-scans are there)
                scans.append(scan)
            else:  # If there is a bad scan, skip the rest of the loop
                continue

            # Robot Control
            direction, angles = set_course(scan)

            # Cleanup
            wait(1, print, process_time())

    except KeyboardInterrupt as e:
        print(f"{e}. Exiting now.")
        break
    except RPLidarException as e:
        print(e)
        continue