from utilities.pi import Encoder, Drive

# TODO: FIX THIS!!!


drive = Drive(20, 21, 16, 12)
encoders = Encoder([[26, 19], [13, 6]])
drive.set(100, 100)

try:
    while True:
        print(encoders.encoders)
except Exception as e:
    print(e)
    drive.exit()