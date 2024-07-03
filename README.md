# soft-iot-tatu-python

TATU protocol in Python

Request GET for a specific sensor: 
{"method":"GET", "sensor":"sensorName"}

Request GET for all sensors at a device: 
{"method":"GET", "sensor":"deviceName"}

Response GET sensorName:
{"header":{"method":"GET", "device":"deviceName", "sensor":"sensorName"}, "payload":{"sensors":{"sensorName":listValues}}}

Response GET deviceName:
{"header":{"method":"GET", "device":"deviceName", "sensor":"deviceName"}, "payload":{"sensors":{"sensorName1":listValues,"sensorName2":listValues,"sensorName3":listValues}}}



Request FLOW for a specific sensor:
{"method":"FLOW", "sensor":"sensorName", "time":{"collect":collectTime,"publish":publishTime}}

Request FLOW for all sensors at a device:
{"method":"FLOW", "sensor":"sensorName", "time":{"collect":collectTime,"publish":publishTime}}

Response FLOW sensorName:
{"header":{"method":"FLOW", "device":"deviceName", "sensor":"sensorName", "time":{"collect":collectTime,"publish":publishTime}}, "payload":{"sensors":{"sensorName":listValues}}}

Response FLOW deviceName:
{"header":{"method":"FLOW", "device":"deviceName", "sensor":"deviceName","time":{"collect":collectTime,"publish":collectTime}},"payload":{"sensors":{"sensorName1":listValues,"sensorName2":listValues,"sensorName3":listValues}}}



Request EVENT for a specific sensor:
{"method":"EVENT", "name":"sensorName", "time":{"collect":collectTime,"publish":publishTime}}

Request EVENT for all sensors at a device: 
- There's no EVENT for all sensors

Response EVENT sensor:
{"header":{"method":"EVENT", "device":"deviceName", "sensor":"sensorName", "time":{"collect":collectTime,"publish":publishTime}}, "payload":{"sensors":{"sensorName":listValues}}}


Request POST sensor:
{"method":"POST", "sensor":"sensorName", "value":value}

Response POST sensor (change in progress):
{"header":{"method":"POST", "device":"deviceName", "sensor":"sensorName", "value":value}, "payload":{"value":value}}



sensorName examples:
- humiditySensor
- temperatureSensor
- soundSensor
- humanPresenceSensor


deviceName examples:
- pizerosensor01
- pisensor01
- galileo01
