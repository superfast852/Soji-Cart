from utilities.pi import Lidar
from utilities import collision
from utilities.utils import animate_and_save
import time
scans = []
lidar = Lidar()
try:
    while len(scans) < 100:
        scan = lidar.read()
        scans.append(scan)
        print(f"{len(scans)}: {scans[-1]}")
        print(collision.check_surroundings(scans[-1], 50))
        time.sleep(0.1)
except Exception as e:
    print(e)
lidar.exit()
animate_and_save(scans)
print("Exiting...")