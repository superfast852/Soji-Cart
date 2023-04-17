from rplidar import RPLidar
from utilities.pi import Drive
from utilities.collision import check_surroundings, check_collision
from utilities.comms import Server
from threading import Thread
from _thread import interrupt_main

collision_space = 20  # Range of angles to check for obstacles in front of car
collision_threshold = 100  # Minimum distance for the code to consider as obstacle.
spin_intensity = 4  # Divides max_speed by this to spin robot in setCourse()
max_speed = 100
collision_bounds = (250, 290)

outwards = 0
inwards = (0, 0)
start = 0

motors = Drive(16, 12, 21, 20)
lidar = RPLidar('/dev/ttyUSB0', timeout=10)
motors.brake()


def set_course(lidar_data):
    if check_collision(lidar_data, collision_bounds, collision_threshold):  # Check for obstacles ahead

        # If there is an obstacle...
        direction, angles = check_surroundings(lidar_data, collision_threshold)  # Find out the clearest side
        if direction == "Right":
            motors.setLeftSpeed(-max_speed/spin_intensity)
            motors.setRightSpeed(max_speed)
        else:
            motors.setLeftSpeed(max_speed)
            motors.setRightSpeed(-max_speed/spin_intensity)
        return direction, angles  # Return the direction and the angles of the obstacle for future optional odometry.

    else:
        motors.setLeftSpeed(max_speed)
        motors.setRightSpeed(max_speed)
        return "Forward", collision_bounds


def async_comms():
    global inwards, outwards, start
    server = Server("192.168.0.104", 9160)
    client = server.connect()
    start = 1
    while True:
        inwards = server.rx(client)
        if inwards == "close":
            interrupt_main()
            break
        print(inwards)
        server.tx(outwards, client)


async_thread = Thread(target=async_comms)
async_thread.start()
scan = [0]*360
try:
    while True:
        if start:
            for data in lidar.iter_scans():
                try:
                    for _, angle, distance in data:
                        scan[min(359, int(angle))] = distance/10
                        if isinstance(inwards, int):
                            outwards = set_course(scan)
                        else:
                            motors.setLeftSpeed(round(inwards[1]*100))
                            motors.setRightSpeed(round(inwards[0]*100))
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(e)
                    lidar.clean_input()
except Exception as e:
    print(e)
    exit(1)
