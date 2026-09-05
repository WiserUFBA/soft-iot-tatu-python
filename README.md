# soft-iot-tatu-python

TATU protocol in Python

The TATU (Tiny Application for Things Universal) protocol is a lightweight application protocol designed for communication between IoT devices over MQTT, focusing on simplicity, interoperability, and efficiency. It defines a standardized set of JSON-based messages for common IoT operations such as reading sensor data (GET), sending commands or values (POST), periodic data collection (FLOW), and event-driven updates (EVENT). While the FLOW method publishes sensor readings at fixed time intervals, the EVENT method is triggered only when a sensor value changes, reducing network traffic and power consumption on constrained devices. By providing a simple and efficient abstraction layer over MQTT, TATU enables the development of scalable, interoperable, and easily integrable IoT systems across edge and cloud environments.


Request GET for a specific sensor:
`{"method":"GET", "sensor":"sensorName"}`

Request GET for all sensors at a device:
`{"method":"GET", "sensor":"deviceName"}`

Response GET sensorName:
`{"header":{"method":"GET", "device":"deviceName", "sensor":"sensorName"}, "payload":{"sensors":[{"sensorName":listValues}]}}`

Response GET deviceName:
`{"header":{"method":"GET", "device":"deviceName", "sensor":"deviceName"}, "payload":{"sensors":[{"sensorName1":listValues},{"sensorName2":listValues},{"sensorName3":listValues}]}}`



Request FLOW for a specific sensor:
`{"method":"FLOW", "sensor":"sensorName", "time":{"collect":collectTime,"publish":publishTime}}`

Request FLOW for all sensors at a device:
`{"method":"FLOW", "sensor":"deviceName", "time":{"collect":collectTime,"publish":publishTime}}`

Response FLOW sensorName:
`{"header":{"method":"FLOW", "device":"deviceName", "sensor":"sensorName", "time":{"collect":collectTime,"publish":publishTime}}, "payload":{"sensors":[{"sensorName":listValues}]}}`

Response FLOW deviceName:
`{"header":{"method":"FLOW", "device":"deviceName", "sensor":"deviceName","time":{"collect":collectTime,"publish":publishTime}},"payload":{"sensors":[{"sensorName1":listValues},{"sensorName2":listValues},{"sensorName3":listValues}]}}`



Request EVENT for a specific sensor:
`{"method":"EVENT", "sensor":"sensorName", "time":{"collect":collectTime}}`

Request EVENT for all sensors at a device:
- There's no EVENT for all sensors

Response EVENT sensor:
`{"header":{"method":"EVENT", "device":"deviceName", "sensor":"sensorName", "time":{"collect":collectTime,"publish":publishTime}}, "payload":{"sensors":[{"sensorName":listValues}]}}`


Request STOP (terminate a running FLOW or EVENT):
`{"method":"STOP", "target":"FLOW", "sensor":"sensorName"}`

- `target`: method to stop (`FLOW` or `EVENT`); defaults to `FLOW` when omitted
- `sensor`: sensor name of the running operation to terminate
- No response is published for STOP


Request POST sensor:
`{"method":"POST", "sensor":"sensorName", "value":value}`

Response POST sensor:
`{"header":{"method":"POST", "device":"deviceName", "sensor":"sensorName", "value":value}, "payload":{"value":value}}`

> The `sensorName` function in `sensors.py` must accept `value` as an argument for POST to work.


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
