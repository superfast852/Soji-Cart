from utilities.pi import Arm, time
arm = Arm(smoothness=5)
time.sleep(1)
arm.grab_item()