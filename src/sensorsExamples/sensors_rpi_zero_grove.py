# sensors.py — Raspberry Pi Zero W 2 + Grove Base HAT
#
# Copy this file to src/tatu/sensors.py to use with real hardware.
# Install dependencies: pip install -r src/sensorsExamples/requirements-grove-hat.txt
#
# Wiring (Grove Base HAT port → sensor):
#   D16 (GPIO16) → DHT22          (temperatureSensor, humiditySensor)
#   A0            → Light v1.2    (lightSensor)    — ADC 0, raw (0-4095)
#   A2            → Sound/Mic     (soundSensor)    — ADC 2, raw (0-4095)
#   D5  (GPIO5)  → Ultrasonic     (ultrasonicSensor) — cm, -1.0 se sem eco em 1 s
#
# SGP41 (vocSensor/noxSensor) é reservado para RPi4 em M1 — não cabeado aqui.
#
# config.json sensors list for this node:
#   temperatureSensor, humiditySensor, lightSensor, soundSensor, ultrasonicSensor
#
# Notas de hardware (implementação baseada no RPi4 validado no IC/UFBA em 2026-09-09;
# ainda não validada no RPi Zero W 2 — issue #8 cobre a validação):
#   - Grove Base HAT ADC responde em I2C 0x08 (não 0x04 como documenta a Seeed)
#   - ultrasonicSensor usa thread daemon com timeout 1 s (evita bloqueio indefinido)

import time
import threading
from grove.grove_temperature_humidity_sensor import DHT
from grove.adc import ADC
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger

_dht = DHT("22", 16)           # DHT22 em D16 (GPIO 16)
_adc = ADC(0x08)               # Grove Base HAT ADC — validado em 0x08 (Seeed documenta 0x04)
_ultrasonic = GroveUltrasonicRanger(5)  # Ultrasonic em D5 (GPIO 5)

_dht_cache = {"humi": 0.0, "temp": 0.0, "ts": 0.0}
_DHT_TTL = 3.0  # segundos — evita leitura dupla quando GET pede temp+humi juntos


def _read_dht():
    if time.monotonic() - _dht_cache["ts"] >= _DHT_TTL:
        humi, temp = _dht.read()
        _dht_cache.update(
            {"humi": round(humi, 1), "temp": round(temp, 1), "ts": time.monotonic()}
        )
    return _dht_cache["humi"], _dht_cache["temp"]


# ── Funções TATU (nome = nome do sensor em config.json) ──────────────────────

def temperatureSensor():
    _, temp = _read_dht()
    return temp


def humiditySensor():
    humi, _ = _read_dht()
    return humi


def lightSensor():
    return _adc.read(0)   # A0, raw (0-4095)


def soundSensor():
    return _adc.read(2)   # A2, raw (0-4095)


def ultrasonicSensor():
    """Distância em cm. Retorna -1.0 se sem eco em 1 s."""
    _result = [None]
    def _measure():
        try:
            _result[0] = round(_ultrasonic.get_distance(), 1)
        except Exception:
            pass
    t = threading.Thread(target=_measure, daemon=True)
    t.start()
    t.join(timeout=1.0)
    return _result[0] if _result[0] is not None else -1.0
