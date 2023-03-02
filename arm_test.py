from adafruit_servokit import ServoKit


kit = ServoKit(channels=8)
arm = [kit.servo[i] for i in range(6)]

# Set the arm to the home position
home = [90, 45, 180, 45, 0, 125]

for i, angle in enumerate(home):
    arm[i].angle = angle

def round_list(x, num=5):
    return list(map(lambda y: round(y, num), x))

print(round_list([15.5, 16.5, 17.5]))
