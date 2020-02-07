import mraa

sensor = mraa.Aio(0)
print(sensor.read())
