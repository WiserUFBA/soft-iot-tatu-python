from upm import pyupm_yg1006 as flame
from time import sleep

import mraa

sensor = flame.YG1006(4)

x = mraa.Gpio(4)
x.dir(mraa.DIR_IN)

while True:
    print(sensor.flameDetected())
    print(x.read())
    sleep(2)


