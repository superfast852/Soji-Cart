# idk chief, this seems sus. Please check.

from utilities.comms import Server
# from socket import gethostbyname
from random import random

ip = "localhost"  # "172.6.0.116"  # gethostbyname("soji.local")
s = Server(ip, 9160)

def grab_routine():
    c2c = s.rx(conn)
    s.tx("received", conn)
    # Zero out Arm
    # arm.move([90, 20, 0, 50])
    print(f"Initial C2C: {c2c}")
    while abs(c2c) > 25:
        print(f"{addr}: C2C = {c2c}")
        spin = "left" if c2c < 25 else "right" if c2c > 25 else "center"
        print(spin)
        c2c = s.rx(conn)
        s.tx("received", conn)
    s.rx(conn)

    s.tx("grabbed", conn)
    print("Grab Routine Success.")


addr = None
while True:
    try:
        print("Connecting...")
        conn, addr = s.connect()
        addr = addr[0]
        print(f"CONNECTED: {addr}")
        while conn:
            position, center = s.rx(conn)
            print(f"{addr}: Position = {position}, Center = {center}")
            if center:
                print("center active")
                s.tx("received", conn)
                try:
                    grab_routine()
                except Exception as e:
                    print(e)
                    continue
            else:
                s.tx(random(), conn)
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
        continue