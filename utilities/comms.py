import socket
import _pickle as pickle
import struct


class Comms:
    def tx(self, data, conn):
        msg = pickle.dumps(data)
        conn.sendall(struct.pack(">I", len(msg)))
        conn.sendall(msg)

    def rx(self, conn):
        packet_size = struct.unpack('>I', conn.recv(4))[0]
        payload = b""
        remaining = packet_size
        while remaining != 0:
            payload += conn.recv(packet_size)
            remaining = packet_size - len(payload)
        return pickle.loads(payload)


class Server(Comms):
    def __init__(self, ip, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((ip, port))
        self.s.listen(1)

    def connect(self):
        return self.s.accept()

    def close(self):
        pass

class Client(Comms):
    def __init__(self, ip, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.connect((ip, port))

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