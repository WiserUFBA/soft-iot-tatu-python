import Adafruit_DHT

sensor = Adafruit_DHT.DHT11

# The name of sensors functions should be the same as in config.json



def humiditySensor():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, 16)
    return humidity

def temperatureSensor():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, 16)
    return temperature


