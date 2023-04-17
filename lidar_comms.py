from utilities.comms import Client
from utilities.controller import XboxController
client = Client("192.168.0.104", 9160)
controller = XboxController()
state = 0
mode = 0
a_ls = 0


def tank(x, power=1):
    if power != 0:
        lf = round((power + ((power / abs(power)) * min(0, x))), 3)
        rf = round((power - ((power / abs(power)) * max(0, x))), 3)
    else:
        lf, rf = 0, 0
    return lf, rf


try:
    while True:
        joy = controller.read()
        pulse, a_ls = controller.edge(controller.A, a_ls)
        if pulse:
            mode = not mode
        if mode:
            client.tx(10, client.s)
            state = 1
            print(client.rx(client.s))
            state = 0
        else:
            client.tx(tank(joy[0], joy[4]), client.s)
            state = 1
            print(client.rx(client.s))
            state = 0
        print(f"Mode: {mode}")
except KeyboardInterrupt:
    pass

if state:
    client.rx(client.s)
client.tx("close", client.s)
