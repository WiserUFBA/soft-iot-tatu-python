import mraa

# The name of sensors functions should be the same as in config.json


def luminositySensor():
    sensor = None
    sensor = mraa.Aio(0) #A0 pin from galileo Gen 2
    return sensor.read()

def gasSensor():
    sensor = None
    sensor = mraa.Aio(1)
    return sensor.read()

def flameSensor():
    sensor = None
    sensor = mraa.Gpio(4)
    sensor.dir(mraa.DIR_IN)
    return sensor.read()
