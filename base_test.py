from utilities.comms import Client
from utilities.controller import XboxController

controller = XboxController()
s = Client("soji.local", 9160)

mode = 0
auto = 0
start_ls = 0
home_ls = 0
grab_ls = 0

def change_mode():
    global mode
    mode = not mode


def change_auto():
    global auto
    auto = not auto


def tank(self, x, power=1):
    if power != 0:
        lf = round((power + ((power / abs(power)) * min(0, x))), 3)
        rf = round((power - ((power / abs(power)) * max(0, x))), 3)
    else:
        lf = 0
        rf = 0
    return lf, rf


def joy2arm(inputs):
    for i, val in enumerate(inputs):
        pose[i] += val


pose = [0]*6  # Implement servo home positions

while True:
    joy = controller.read()
    ljoy = joy[0:2]
    rjoy = joy[2:4]
    rtrig = joy[4]
    start_pulse, start_ls = controller.edge(controller.Start, start_ls)
    home_pulse, home_ls = controller.edge(controller.Back, home_ls)
    grab_pulse, grab_ls = controller.edge(controller.A, grab_ls)
    if start_pulse:
        change_mode()
    if home_pulse:
        change_auto()
        s.tx(auto, s.s)
        s.rx(s.s)
        continue

    # Drive mode
    if not auto:
        if mode:
            s.tx(tank(ljoy[0], rtrig), s.s)
        else:  # Arm mode
            if grab_pulse:  # send grab command
                s.tx("grab", s.s)
            else:  # Send joystick changes
                pose[0] += round(ljoy[0])
                pose[1] += round(ljoy[1])
                pose[2] += round(rjoy[0])
                pose[3] += round(rjoy[1])

                if round(rtrig):
                    pose[5] = 180
                else:
                    pose[5] = 0
                for i in pose:
                    if i<0:
                        i = 0
                    elif i>180:
                        i = 180
                s.tx(pose, s.s)
        s.rx(s.s)
    else:
        s.tx(auto, s.s)
        s.rx(s.s)
