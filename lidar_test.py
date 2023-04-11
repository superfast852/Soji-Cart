from rplidar import RPLidar
from utilities.pi import Drive
from utilities.collision import check_surroundings, check_collision
from utilities.utils import plot, plt

collision_space = 20  # Range of angles to check for obstacles in front of car
collision_threshold = 250  # Minimum distance for the code to consider as obstacle.
spin_intensity = 4  # Divides max_speed by this to spin robot in setCourse()
max_speed = 100
collision_bounds = (200, 300)
motors = Drive(16, 12, 21, 20)
lidar = RPLidar('/dev/ttyUSB0', timeout=3)
motors.brake()


def set_course(lidar_data):
    if check_collision(lidar_data, collision_bounds, collision_threshold):  # Check for obstacles ahead

        # If there is an obstacle...
        direction, angles = check_surroundings(lidar_data, collision_threshold)  # Find out the clearest side
        if direction == "Right":
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


scan = [0]*360
for data in lidar.iter_scans():
    for _, angle, distance in data:
        scan[min(359, int(angle))] = distance/10
    print(min(scan), set_course(scan))
    #plot(scan)
