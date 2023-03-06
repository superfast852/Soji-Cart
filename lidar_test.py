from math import floor
from adafruit_rplidar import RPLidar

# Setup the RPLidar
PORT_NAME = "/dev/ttyUSB0"

# used to scale data to fit on the screen
max_distance = 0

scan_data = [0] * 360

def process_data(data):
    for (_, angle, distance) in data:
        scan_data[min(359, floor(angle))] = distance

lidar = RPLidar(None, PORT_NAME, timeout=3)

for i in lidar.iter_scans():
    process_data(i)
    print(scan_data)

lidar.stop()
lidar.disconnect()

