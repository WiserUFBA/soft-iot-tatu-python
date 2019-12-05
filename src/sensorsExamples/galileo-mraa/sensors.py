import mraa

sensorValueLum = 0
sensorValueGas = 0
onboard_led = mraa.Gpio(13)

# The name of sensors functions should be the same as in config.json
def luminositySensor():
	sensorValueLum = mraa.Aio(0) #A0 pin from galileo Gen 2
	return sensorValueLum.read()

def gasSensor():
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

#def ledActuator():
	#onboard_led.dir(mraa.DIR_IN)
#	if onboard_led.read():
#		return True
#	else:
#		return False

