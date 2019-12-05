import random

# This shows two examples of simulated sensors which can be used to test
# the TATU protocol on SOFT-IoT or with a standalone MQTT broker
#
# There are samples of real sensors implementations in the src/sensorsExamples
# folder. You can adapt those examples to your needs.


# The name of sensors functions should be exactly the same as in config.json

def humiditySensor():
    return random.randint(10, 70)

def temperatureSensor():
    return random.randint(25, 38)

def ledActuator():
	print("post 2")
	return random.randint(0, 1)

def __ledActuator__(s):
	print("post 1")
	# Configure GPIO pin #13 to be an output pin
	if s:
		print("1")
	else:
		print("0")
	return s