import mraa

sensorValueTemp = 0
sensorValueHumi = 0
sensorValueSound = 0

# The name of sensors functions should be the same as in config.json
def humiditySensor():
	sensorValueLum = mraa.Aio(0) #A0 pin from galileo Gen 2
	return sensorValueLum.read()

def temperatureSensor():
	sensorValueGas = mraa.Aio(1) #A1 pin from galileo Gen 2
	return sensorValueGas.read()

def temperatureSensor():
	sensorValueGas = mraa.Aio(1) #A1 pin from galileo Gen 2
	return sensorValueGas.read()

def ledActuator(s = None):
	# Configure GPIO pin #13 to be an output pin
	if s==None:
		if onboard_led.read():
			return True
		else:
			return False
	else:
		onboard_led.dir(mraa.DIR_OUT)
		if s:
			onboard_led.write(1)
		else:
			onboard_led.write(0)
		return s

