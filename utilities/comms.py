import socket
# import _pickle as pickle
# import struct
# Old Comms were moved to utils.py


class Comms:
    def tx(self, data, conn):
        msg = str(data)
        conn.sendall(msg.encode("utf-8"))

    def rx(self, conn):
        return eval(conn.recv(1024).decode("utf-8"))


class Server(Comms):
    def __init__(self, ip, port, conn_wait=30):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((ip, port))
        self.s.settimeout(conn_wait)
        self.s.listen(1)

    def connect(self, comm_timeout=5):
        s, addr = self.s.accept()
        s.settimeout(comm_timeout)
        return s

    def close(self):
        pass


class Client(Comms):
    def __init__(self, ip, port, timeout=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.connect((ip, port))
        self.s.settimeout(timeout)

    def send(self, data):
        self.tx(data, self.s)
        returnal = self.rx(self.s)
        if returnal == "Closing":
            self.close()
        return returnal

    def close(self):
        self.s.close()


if __name__ == "__main__":
    import multiprocessing
    server = Server("localhost", 5000)
    multiprocessing.Process(target=server.handle).start()
    client = Client("localhost", 5000)
    print(f"Client: {client.send({'servo': 0, 'angle': 90})}")
    print(f"Client: {client.send('World')}")
    print(f"Client: {client.send('send')}")
    print(f"Client: {client.send('exit')}")