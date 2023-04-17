# TODO: Add Start/Stop Variable/Function (if start:)

from rplidar import RPLidar
from utilities.pi import Drive, Arm
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
data = [0, 0]
mode = 0

drive = Drive(16, 12, 21, 20)
arm = Arm()
lidar = RPLidar('/dev/ttyUSB0', timeout=10)
drive.brake()


def set_course(lidar_data):
    if check_collision(lidar_data, collision_bounds, collision_threshold):  # Check for obstacles ahead

        # If there is an obstacle...
        direction, angles = check_surroundings(lidar_data, collision_threshold)  # Find out the clearest side
        if direction == "Right":
            drive.setLeftSpeed(-max_speed/spin_intensity)
            drive.setRightSpeed(max_speed)
        else:
            drive.setLeftSpeed(max_speed)
            drive.setRightSpeed(-max_speed/spin_intensity)
        return direction, angles  # Return the direction and the angles of the obstacle for future optional odometry.

    else:
        drive.setLeftSpeed(max_speed)
        drive.setRightSpeed(max_speed)
        return "Forward", collision_bounds


def async_comms():
    global mode, data, outwards
    server = Server("192.168.0.104", 9160)
    client = server.connect()
    try:
        while True:
            mode, data = server.rx(client)
            if data == "close":
                raise ConnectionError("Client Disconnected.")
            print(data)
            server.tx(outwards, client)
    except Exception as e:
        print(e)
        interrupt_main()


async_thread = Thread(target=async_comms)
async_thread.start()
scan = [0]*360

while True:
    for scan in lidar.iter_scans():
        for _, angle, distance in scan:
            scan[min(359, int(angle))] = distance
        
        if mode == 0:  # Autonomous
            outwards = set_course(scan)
        elif mode == 1:  # Manual/Sentinel Mode
            if len(data) == 2:
                drive.set(data[0], data[1])
            elif len(data) == 6:
                if data[0] == "grab":
                    if data[1] == 1:
                        arm.grab_item(side=1)
                    else:
                        arm.grab_item()
                    outwards = "grabbed"
                    continue
                else:
                    arm.move(data)
            outwards = "received"
        elif mode == 2:  # Grabbing. Optionally, use Manual mode as control for arm.
            pass
