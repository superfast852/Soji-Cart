from math import floor
from adafruit_rplidar import RPLidar
from utilities.pyvec import *
from matplotlib import pyplot as plt

fig, ax = plt.subplots(1,1)

# Setup the RPLidar
PORT_NAME = "/dev/ttyUSB0"
lidar = RPLidar(None, PORT_NAME, timeout=3)

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


def process_data(data):
    print(data)

scan_data = [0] * 360
try:
    # print(lidar.get_info())
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            scan_data[min([359, floor(angle)])] = distance
        update_rtp(scan_data)

except KeyboardInterrupt:
    print("Stopping.")
lidar.stop()

lidar.disconnect()