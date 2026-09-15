# soft-iot-tatu-python

CPython implementation of the TATU protocol for Linux single-board computers (Raspberry Pi, Intel Galileo, etc.).

TATU is a lightweight IoT protocol built on top of MQTT that lets a gateway or broker send commands to devices to read sensors (GET, FLOW, EVENT) and write actuators (POST), and stop ongoing operations (STOP).

This implementation uses **paho-mqtt** with one subscriber client and per-task threads for FLOW and EVENT operations.

---

## Requirements

- Python 3.8+
- `paho-mqtt` — see `requirements.txt`
- An MQTT broker reachable from the device (e.g. Mosquitto)

```bash
pip install -r requirements.txt
```

---

## Quick start

### 1. Configure the device

Edit `config.json`:

```json
{
    "deviceName": "rpi4-grove-01",
    "mqttBroker": "192.168.1.100",
    "mqttPort": 1883,
    "mqttUsername": "",
    "mqttPassword": "",
    "topicPrefix": "dev/",
    "topicReq": "/REQ",
    "topicRes": "/RES",
    "topicErr": "/ERR",
    "sensors": [
        {"type": "float", "name": "temperatureSensor"},
        {"type": "float", "name": "humiditySensor"}
    ]
}
```

### 2. Implement your sensors

Each name in `sensors` must match a function in `sensors.py`. See `sensorsExamples/` for hardware-specific examples.

### 3. Run

```bash
python3 main.py
```

---

## TATU protocol reference

All requests are JSON published to `{topicPrefix}{deviceName}{topicReq}/...`.
All responses are published to `{topicPrefix}{deviceName}{topicRes}`.
Errors are published to `{topicPrefix}{deviceName}{topicErr}`.

### GET — one-shot read

```json
{"method": "GET", "sensor": "temperatureSensor"}
```

Response:
```json
{
  "header": {"method": "GET", "device": "rpi4-grove-01", "sensor": "temperatureSensor"},
  "payload": {"sensors": [{"temperatureSensor": [24.2]}]}
}
```

Use `"sensor": "rpi4-grove-01"` (the device name) to read all sensors at once.

---

### FLOW — periodic collection

Collects values every `collect` seconds and publishes a batch every `publish` seconds.

**Constraints:** `collect` and `publish` must be positive integers, and `publish` ≥ `collect`.

```json
{"method": "FLOW", "sensor": "temperatureSensor", "time": {"collect": 5, "publish": 30}}
```

Response (every `publish` seconds):
```json
{
  "header": {
    "method": "FLOW", "device": "rpi4-grove-01", "sensor": "temperatureSensor",
    "time": {"collect": 5, "publish": 30}
  },
  "payload": {"sensors": [{"temperatureSensor": [24.2, 24.5, 24.5, 24.8, 24.5, 24.5]}]}
}
```

---

### EVENT — change detection

Polls the sensor every `collect` seconds and publishes when the value changes. The current value is published immediately on creation as a reference baseline.

**Constraints:** `collect` must be a positive integer and `publish` (if given) must be ≥ `collect`.

#### Immediate mode (`publish` omitted or `0`)

Publishes as soon as a change is detected.

```json
{"method": "EVENT", "sensor": "soundSensor", "time": {"collect": 1}}
```

Response on creation (initial value):
```json
{
  "header": {"method": "EVENT", "device": "rpi4-grove-01", "sensor": "soundSensor", "time": {"collect": 1, "publish": 0}},
  "payload": {"sensors": [{"soundSensor": [4]}]}
}
```

#### Windowed mode (`publish` > 0)

Buffers only changed values and publishes them in a batch every `publish` seconds. Skips the publish if nothing changed in the window.

```json
{"method": "EVENT", "sensor": "soundSensor", "time": {"collect": 1, "publish": 30}}
```

Response every 30 s (only if changes occurred):
```json
{
  "header": {"method": "EVENT", "device": "rpi4-grove-01", "sensor": "soundSensor", "time": {"collect": 1, "publish": 30}},
  "payload": {"sensors": [{"soundSensor": [6, 4, 5, 61, 72, 4]}]}
}
```

---

### POST — actuator write

```json
{"method": "POST", "sensor": "ledActuator", "value": true}
```

Response:
```json
{
  "header": {"method": "POST", "device": "rpi4-grove-01", "sensor": "ledActuator", "value": true},
  "payload": {"value": true}
}
```

---

### STOP — stop an ongoing operation

```json
{"method": "STOP", "sensor": "temperatureSensor", "target": "FLOW"}
```

- `target`: `"FLOW"` or `"EVENT"`. Defaults to `"FLOW"` if omitted.
- `sensor`: required. Omitting it produces an `INVALID_PARAMS` error. If the target task is not running, produces a `STOP_NOT_FOUND` error.

---

### Error response

Published to `/ERR` when a request cannot be fulfilled:
```json
{"code": "SENSOR_NOT_FOUND", "message": "unknownSensor"}
```

| Code | Cause |
|---|---|
| `SENSOR_NOT_FOUND` | Sensor name not in `config.json` |
| `INVALID_PARAMS` | Missing or invalid `time` fields; STOP without `sensor` |
| `UNKNOWN_METHOD` | Unrecognised `method` value |
| `STOP_NOT_FOUND` | STOP target task is not running |
| `SENSOR_READ_ERROR` | Exception while reading or writing the sensor |

---

## Related projects

- [soft-iot-tatu-upython](https://github.com/WiserUFBA/soft-iot-tatu-upython) — MicroPython version (ESP8266)
