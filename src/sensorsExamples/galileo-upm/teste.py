import sensors
from time import sleep

#print(sensors.flameSensor())
while True:
    print("Lumi: " )
    print(sensors.luminositySensor())
    print("Gas: ")
    print(sensors.gasSensor())
    #print("Sound: ")
    #print(sensors.soundSensor())
    print("Flame: ")
    print(sensors.flameSensor())
    print("Distance: ")
    print(sensors.distanceSensor())
    
    sleep(3)

