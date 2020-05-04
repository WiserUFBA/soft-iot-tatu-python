from upm import pyupm_ultrasonic as ul
from time import sleep

sensor = ul.UltraSonic(4)
value = 0.0

while True:
    if not sensor.working():
        value = float(sensor.getDistance()/58)
        print (value)
    
    sleep(3)


