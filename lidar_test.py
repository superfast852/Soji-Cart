from math import floor

import rplidar

from utilities.pyvec import *
from matplotlib import pyplot as plt
from threading import Thread
from adafruit_rplidar import RPLidar, RPLidarException

fig, ax = plt.subplots(1,1)

# Setup the RPLidar
PORT_NAME = "/dev/ttyUSB0"

# used to scale data to fit on the screen
max_distance = 0

def update_rtp(scan):
    ax.clear()
    vectors = [Vector([distance, angle]) for angle, distance in enumerate(scan)]

    x = [vector.x for vector in vectors]
    y = [vector.y for vector in vectors]

    plot_cartesian(x, y, ax, 0, 0, 0, 0, color="b")
    plt.pause(1e-16)
    plt.draw()

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

