import sensors
from time import sleep

#print(sensors.flameSensor())
while True:
    print("Lumi: " )
    print(sensors.luminositySensor())
    print("Flame: ")
    print(sensors.flameSensor())
    print("Gas: ")
    print(sensors.gasSensor())
    print("Sound: ")
    print(sensors.soundSensor())
    print("Temperature: ")
    print(sensors.temperatureSensor())
    
    sleep(4)

