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



deviceName examples:
- pizerosensor01
- pisensor01
- galileo01



# IoT Sensor Taxonomy (camelCase Naming Convention for sensorName)

This document presents a functional taxonomy of common IoT sensors using a consistent `camelCase` naming convention. It can be used in data models, APIs, semantic vocabularies, or general documentation of IoT systems.

## 🌡️ Environmental Sensors
- `temperatureSensor`
- `humiditySensor`
- `pressureSensor`
- `lightSensor`
- `uvSensor`
- `windSpeedSensor`
- `rainfallSensor`
- `soilMoistureSensor`

## 🌫️ Gas and Air Quality Sensors
- `co2Sensor`
- `coSensor`
- `methaneSensor`
- `smokeSensor`
- `airQualitySensor`
- `ozoneSensor`
- `vocSensor` *(Volatile Organic Compounds)*

## 🧭 Motion and Position Sensors
- `motionSensor`
- `accelerometerSensor`
- `gyroscopeSensor`
- `magnetometerSensor`
- `tiltSensor`
- `pirSensor` *(Passive Infrared)*
- `ultrasonicSensor`
- `proximitySensor`
- `vibrationSensor`

## 🔊 Audio and Imaging Sensors
- `soundSensor`
- `microphoneSensor`
- `cameraSensor`
- `thermalCameraSensor`

## ⚡ Electrical Sensors
- `voltageSensor`
- `currentSensor`
- `powerSensor`
- `energyConsumptionSensor`

## ❤️ Biometric and Health Sensors
- `heartRateSensor`
- `bloodPressureSensor`
- `bloodOxygenSensor`
- `emgSensor` *(Electromyography)*
- `ecgSensor` *(Electrocardiogram)*
- `temperatureBodySensor`

## 📍 Location and Navigation Sensors
- `gpsSensor`
- `geoLocationSensor`
- `compassSensor`
- `altitudeSensor`

## 🧪 Other / Specialized Sensors
- `waterLeakSensor`
- `soilPhSensor`
- `flameSensor`
- `rfidSensor`
- `nfcSensor`
- `touchSensor`
- `weightSensor`
- `loadCellSensor`

---

> **Note:** This taxonomy does not represent an official standard but is based on common naming practices across IoT platforms and ontologies such as SOSA/SSN, SAREF, and QUDT. You are encouraged to extend it based on your specific domain or application.
