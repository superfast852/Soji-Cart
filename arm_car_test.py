from adafruit_servokit import ServoKit
from utilities.pi import Drive, Arm
from utilities.comms import Server
from socket import gethostbyname

arm = Arm(8)
drive = Drive(20, 21, 16, 12)
# Set the arm to the home position
home = [90, 45, 180, 45, 0, 125]
s = Server(gethostbyname("soji.local"), 9160)

def get_speeds(speed, direction):
    if -0.1<direction<0.1:
        return speed, speed
    elif direction>0:
        return speed, min(100, 25+(speed*(1 - direction)))
    elif direction<0:
        return min(100, 25+(speed*(1 + direction))), speed

while True:
    try:
        conn, addr = s.connect()
        print(f"CONNECTED: {addr}")
        while conn:
            try:
                info = conn.recv(1024).split(" ")
                if info[0][-1] == ",":  # Arm mode
                    drive.brake()
                    pose = list(map(lambda x: int(x.replace(",", "")), info))
                    arm.move(pose)
                else:  # Cart mode
                    speed, heading = info
                    left, right = get_speeds(int(speed), float(heading))
                    drive.set(left, right)
                conn.send("received".encode())
            except Exception as e:
                print(f"[ERROR] {addr}: {e}")
    except Exception as e:
        print(f"[ERROR]: {e}")
        continue