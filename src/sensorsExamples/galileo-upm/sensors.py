#import mraa 
#we cant use mraa together with upm (we got a problem with ultrasonic sensor)

from upm import pyupm_light as lightObj
from upm import pyupm_gas as gasObj
from upm import pyupm_yg1006 as flameObj
from upm import pyupm_ultrasonic as ultrasonicObj
from upm import pyupm_temperature as tempObj

#analog
lumi = lightObj.Light(0)
gas = gasObj.MQ2(1)
temp = tempObj.Temperature(2)

#digital
flame = flameObj.YG1006(6)
ultrasonic = ultrasonicObj.UltraSonic(4)

# The name of sensors functions should be the same as in config.json


def luminositySensor():
    return lumi.value()

def gasSensor(): #we need to improve this
    return gas.getSample()

def flameSensor():
    return flame.flameDetected()

def distanceSensor():
    value = (ultrasonic.getDistance()/58) #cm or /148 for inches
    return value

def temperatureSensor():
    return temp.value()
