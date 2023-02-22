from utilities.comms import Server
from socket import gethostbyname
from random import random

s = Server(gethostbyname("soji.local"), 9160)

def grab_routine():
    c2c = s.rx(conn)
    s.tx("received", conn)
    while abs(c2c) > 25:
        print(f"{addr}: C2C = {s.rx}")
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
        conn, addr = s.connect()
        while conn:
            position, center = s.rx(conn)
            print(f"{addr}: Position = {position}, Center = {center}")
            if center:
                s.tx("received", conn)
                try:
                    grab_routine()
                except Exception as e:
                    print(e)
                    continue
            else:
                s.tx(random, conn)
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
        continue