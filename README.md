# soft-iot-tatu-python

CPython implementation of the **TATU protocol** for Linux single-board computers (Raspberry Pi, Intel Galileo, etc.).

TATU is a lightweight IoT protocol built on top of MQTT for reading sensors and writing actuators. See [soft-iot-tatu-spec](https://github.com/WiserUFBA/soft-iot-tatu-spec) for the full protocol specification.

This implementation uses **paho-mqtt** with one subscriber client and per-task threads for FLOW and EVENT operations.

---

## Quick start

See [`src/tatu/README.md`](src/tatu/README.md) for requirements, configuration, sensor implementation, and the full protocol reference.

---

## Sensor examples

Ready-to-use `sensors.py` files for Grove hardware are in [`src/sensorsExamples/`](src/sensorsExamples/):

| File | Hardware | TATU variables |
|------|----------|----------------|
| [`sensors_rpi4_grove.py`](src/sensorsExamples/sensors_rpi4_grove.py) | RPi4 + Grove Base HAT | `temperatureSensor`, `humiditySensor`, `lightSensor`, `soundSensor`, `ultrasonicSensor`, `vocSensor`, `noxSensor` |
| [`sensors_rpi_zero_grove.py`](src/sensorsExamples/sensors_rpi_zero_grove.py) | RPi Zero W 2 + Grove Base HAT | `temperatureSensor`, `humiditySensor`, `lightSensor`, `soundSensor`, `ultrasonicSensor` |

Install Grove HAT dependencies before using these examples:

```bash
pip install -r src/sensorsExamples/requirements-grove-hat.txt
```

> **If you use `iot-infrastructure`:** the `run.sh` for each device handles the symlink automatically — do not copy manually.

Validate each function before starting TATU (run from inside `src/tatu/`):

```bash
cd src/tatu
python3 -c "import sensors; print(sensors.temperatureSensor())"
```

---

## Hardware notes — Grove Base HAT (validated at IC/UFBA, 2026-09-09)

These issues are already resolved in the example files. Read this to avoid debugging known problems.

### ADC responds at 0x08, not 0x04

Seeed documentation says the Grove Base HAT ADC is at `0x04`. On the IC/UFBA hardware (and likely others) it responds at **`0x08`**. Always use `ADC(0x08)`:

```python
from grove.adc import ADC
_adc = ADC(0x08)   # 0x04 does not work on this hardware
```

### SGP41 does not appear in i2cdetect

`i2cdetect -y 1` does not show the SGP41 (address `0x59`) even when correctly connected. This is a known BCM2835 bug: the SGP41 clock-stretches during probe and the BCM2835 interprets it as NACK.

**The sensor communicates normally** — only the i2cdetect probe fails.

**Required workaround:** add to `/boot/firmware/config.txt` and reboot:

```ini
dtparam=i2c_arm_baudrate=10000
```

**Confirm the sensor is present:**

```bash
sudo i2ctransfer -y 1 w2@0x59 0x36 0x82 r9@0x59
```

9 bytes returned → sensor OK. Error → check cable/port.

Do **not** use `sensirion-i2c-sgp41` — the examples use `smbus2` directly with manual CRC-8, which is lighter and avoids the Sensirion library dependency.

### ultrasonicSensor — 1 s timeout

The Grove Ultrasonic Ranger driver can block indefinitely if no echo is received (object out of range or absent). The examples solve this with a daemon thread and timeout, returning `-1.0` if no echo arrives within 1 s. Safe to include in FLOW with nothing in front of the sensor.

### SGP41 — ~10 s warmup

The SGP41 needs ~10 s of conditioning before producing stable readings. Returns `-1` during warmup. TATU is not blocked — early FLOW readings will be `-1`.

SRAW values (0–65535) are raw signals. VOC/NOx indices (0–500) require the Sensirion Gas Index Algorithm, applied server-side.

### DHT22 library — grove, not adafruit

The examples use `grove.grove_temperature_humidity_sensor.DHT`, not `adafruit_dht`. The adafruit library conflicts with Grove Base HAT GPIO on RPi:

```python
from grove.grove_temperature_humidity_sensor import DHT
_dht = DHT("22", 16)   # DHT22 on GPIO 16 (port D16)
```

---

## Related projects

- [soft-iot-tatu-spec](https://github.com/WiserUFBA/soft-iot-tatu-spec) — canonical protocol specification
- [soft-iot-tatu-upython](https://github.com/WiserUFBA/soft-iot-tatu-upython) — MicroPython version (ESP8266)
- [docs/architecture.md](docs/architecture.md) — component architecture and design notes
