import sensors
from time import sleep

#print(sensors.flameSensor())
while True:
    print("Humidity: ")
    print(sensors.humiditySensor())
    print("Temperature: ")
    print(sensors.temperatureSensor())
    
    sleep(4)

