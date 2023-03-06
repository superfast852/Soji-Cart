from utilities.comms import Server
from utilities.pi import Drive
from socket import gethostbyname

ip = gethostbyname("soji.local")
s = Server(ip, 9160)
drive = Drive(20, 21, 16, 12)

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
                speed, heading = s.rx(conn)
                left, right = get_speeds(speed, heading)
                drive.set(left, right)
                conn.send("received".encode())
            except Exception as e:
                print(f"[ERROR] {addr}: {e}")
    except Exception as e:
        print(f"[ERROR]: {e}")
        continue