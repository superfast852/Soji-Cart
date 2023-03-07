from adafruit_servokit import ServoKit
from utilities.comms import Server
from utilities.pi import Arm
from socket import gethostbyname

arm = Arm(8)

# Set the arm to the home position
home = [90, 45, 180, 45, 0, 125]

s = Server(gethostbyname("soji.local"), 9160)

while True:
    try:
        conn, addr = s.connect()
        print(f"CONNECTED: {addr}")
        while conn:
            try:
                pose = [int(i) for i in conn.recv(1024).split(", ")]
                arm.move(pose)
                conn.send("received".encode())
            except Exception as e:
                print(f"[ERROR] {addr}: {e}")
    except Exception as e:
        print(f"[ERROR]: {e}")
        continue
