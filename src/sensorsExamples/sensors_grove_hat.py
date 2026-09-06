# sensors.py — Grove Base HAT (RPi4 / RPi Zero W 2)
#
# Copy this file to src/tatu/sensors.py to use with real hardware.
# Install dependencies: pip install -r src/sensorsExamples/requirements-grove-hat.txt
#
# Wiring (Grove Base HAT ports → sensor):
#   D16 (GPIO16) → DHT22            (temperatureSensor, humiditySensor)
#   A0            → Light v1.2      (lightSensor)   — raw 12-bit ADC (0-4095)
#   A2            → Sound/Mic       (soundSensor)   — raw 12-bit ADC (0-4095)
#   D5  (GPIO5)  → Ultrasonic       (ultrasonicSensor) — cm, 1 decimal
#   I2C 0x59     → SGP41            (vocSensor, noxSensor) — SRAW 0-65535
#
# config.json should list only the sensors connected to this specific node.
# RPi4 can use all 7; RPi Zero W 2 omits vocSensor/noxSensor (no SGP41 in M1).

import time
import adafruit_dht
import board
from grove.adc import ADC
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection
from sensirion_i2c_sgp41.device import Sgp41Device

# --- hardware init ---

_dht = adafruit_dht.DHT22(board.D16)
_adc = ADC()                            # Grove ADC (I2C 0x04) for A0/A2 ports
_ultrasonic = GroveUltrasonicRanger(5)  # D5 = GPIO5

_i2c = LinuxI2cTransceiver('/dev/i2c-1')
_sgp41 = Sgp41Device(I2cConnection(_i2c))

# --- DHT22 cache (reads both temp+humidity in one call; min 2.5s between reads) ---

_dht_cache = (None, None)   # (temperature_C, humidity_pct)
_dht_last_t = 0.0
_DHT_MIN_INTERVAL = 2.5


def _dht_measure():
    global _dht_cache, _dht_last_t
    now = time.monotonic()
    if _dht_cache[0] is None or now - _dht_last_t >= _DHT_MIN_INTERVAL:
        _dht_cache = (round(_dht.temperature, 1), round(_dht.humidity, 1))
        _dht_last_t = now
    return _dht_cache


# --- SGP41 cache (reads VOC+NOX in one call; SRAW values take ~24h to stabilize) ---

_sgp41_cache = (None, None)  # (sraw_voc, sraw_nox)


def _sgp41_measure():
    global _sgp41_cache
    # Default compensation: 25°C (0x6666), 50% RH (0x8000)
    sraw_voc, sraw_nox = _sgp41.measure_raw(
        relative_humidity=0x8000, temperature=0x6666
    )
    _sgp41_cache = (int(sraw_voc), int(sraw_nox))
    return _sgp41_cache


# --- sensor functions (names must match config.json exactly) ---

def temperatureSensor():
    temp, _ = _dht_measure()
    return temp


def humiditySensor():
    _, humi = _dht_measure()
    return humi


def lightSensor():
    # Grove ADC channel 0 (A0 port) — 12-bit raw value (0-4095)
    return _adc.read(0)


def soundSensor():
    # Grove ADC channel 2 (A2 port) — 12-bit raw value (0-4095)
    return _adc.read(2)


def ultrasonicSensor():
    # Distance in cm, 1 decimal place
    return round(_ultrasonic.get_distance(), 1)


def vocSensor():
    # SGP41 SRAW VOC signal (0-65535); lower = more VOC. Stabilizes after ~24h.
    voc, _ = _sgp41_measure()
    return voc


def noxSensor():
    # SGP41 SRAW NOX signal (0-65535). Requires SGP41 to be warmed up.
    _, nox = _sgp41_measure()
    return nox
