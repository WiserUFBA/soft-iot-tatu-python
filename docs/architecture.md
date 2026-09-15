# TATU CPython — Architecture

## Overview

TATU (*Tiny Application for Things Universal*) is a lightweight application protocol for IoT communication over MQTT. This repository implements it in CPython using paho-mqtt.

```text
Application / consumer
        |
        |  TATU requests via MQTT
        v
    MQTT Broker
        |
        v
     TATU Node
        |
        v
  Physical sensor / actuator
```

## Components

### `main.py`

The main process of the node:

- loads `config.json`
- connects to the MQTT broker
- subscribes to the device's request topic (`{topicPrefix}{deviceName}{topicReq}/#`)
- receives JSON messages
- handles STOP by signaling the target operation's `threading.Event`
- creates one daemon thread per TATU operation (GET, FLOW, EVENT, POST)

### `tatu.py`

Contains the protocol operation logic:

- `GET` — immediate single read
- `FLOW` — periodic collection and publish with drift-free deadline advancement
- `EVENT` — publish on value change; immediate mode (`publish=0`) and windowed mode (`publish>0`)
- `POST` — write value to an actuator and publish confirmation
- `STOP` — stop a running FLOW or EVENT task via `threading.Event`

### `sensors.py`

The layer most commonly edited to adapt the node to specific hardware. Each function name must exactly match a `name` entry in `config.json`. TATU locates the function via `getattr()` at runtime.

**Sensor** (read-only):

```python
def temperatureSensor():
    return read_temperature_from_hardware()
```

**Actuator** (POST — accepts the received value):

```python
def ledActuator(value=None):
    gpio.set(LED_PIN, value)
    return value
```

### `config.json`

Defines the node's identity, available sensors, and MQTT parameters:

```text
deviceName, sensors[], mqttBroker, mqttPort,
mqttUsername, mqttPassword,
topicPrefix, topicReq, topicRes, topicErr
```

### `config.py`

Optional Flask web interface to view and edit parts of `config.json`. Not required to understand or run the protocol.

### `sensorsExamples/`

Ready-to-use `sensors.py` files for validated hardware configurations. See the root `README.md` for the list.

---

## Request flows

### GET

```text
1. client publishes GET to /REQ
2. broker delivers to the TATU node
3. main.py receives the message
4. creates a daemon thread running tatu.main()
5. tatu.py identifies the requested sensor
6. tatu.py calls temperatureSensor() from sensors.py
7. function reads the sensor
8. tatu.py builds the JSON response
9. response is published to /RES
```

### FLOW

Separates two frequencies:

```text
collect: interval between reads
publish: interval between publishes

{"method":"FLOW","sensor":"temperatureSensor","time":{"collect":5,"publish":30}}
→ read every 5 s, publish accumulated batch every 30 s
```

Deadlines advance from their previous value (not from current time), so accumulated delays do not shift the schedule and missed cycles are skipped cleanly.

---

## Known limitations

- Each GET/FLOW/EVENT/POST opens its own `pub_client` MQTT connection to the broker — one connection per active operation.
- Sensor exceptions publish a `SENSOR_READ_ERROR` code; detail appears only in the process log.
- Sensor functions in `sensorsExamples/` may depend on library versions different from what is currently installed — validate before reuse.

---

## Node validation checklist

A node is considered functional when:

- [ ] unique `deviceName` set in `config.json`
- [ ] connects to the broker on startup
- [ ] responds to GET
- [ ] FLOW operates correctly when used
- [ ] STOP terminates FLOW/EVENT cleanly
- [ ] EVENT operates correctly when used
- [ ] POST operates correctly on actuators when used
- [ ] responses published to the expected topic
- [ ] configuration documented without exposing credentials
