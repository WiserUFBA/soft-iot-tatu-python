# sensors.py — Raspberry Pi 4 + Grove Base HAT
#
# Copy this file to src/tatu/sensors.py to use with real hardware.
# Install dependencies: pip install -r src/sensorsExamples/requirements-grove-hat.txt
#
# Wiring (Grove Base HAT port → sensor):
#   D16 (GPIO16) → DHT22          (temperatureSensor, humiditySensor)
#   A0            → Light v1.2    (lightSensor)    — ADC 0, raw (0-4095)
#   A2            → Sound/Mic     (soundSensor)    — ADC 2, raw (0-4095)
#   D5  (GPIO5)  → Ultrasonic     (ultrasonicSensor) — cm, -1.0 se sem eco em 1 s
#   I2C 0x59     → SGP41          (vocSensor, noxSensor) — SRAW 0-65535, -1 durante warmup
#
# config.json sensors list for this node:
#   temperatureSensor, humiditySensor, lightSensor, soundSensor,
#   ultrasonicSensor, vocSensor, noxSensor
#
# Notas de hardware (validado no IC/UFBA em 2026-09-09):
#   - Grove Base HAT ADC responde em I2C 0x08 (não 0x04 como documenta a Seeed)
#   - SGP41 (0x59) NÃO aparece em i2cdetect (clock stretching BCM2835); adicionar
#     dtparam=i2c_arm_baudrate=10000 em /boot/firmware/config.txt + reboot
#   - Comunicação com SGP41 via smbus2 funciona normalmente
#   - ultrasonicSensor usa thread daemon com timeout 1 s (evita bloqueio indefinido)
#   - vocSensor/noxSensor retornam -1 nos ~10 s iniciais (conditioning SGP41 em background)
#
# Padrão para sensores com warmup longo (SGP30, CCS811 também precisam):
#   background thread → conditioning → _ready = True; função retorna -1 enquanto não pronto

import time
import threading
import smbus2
from grove.grove_temperature_humidity_sensor import DHT
from grove.adc import ADC
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger

_dht = DHT("22", 16)           # DHT22 em D16 (GPIO 16)
_adc = ADC(0x08)               # Grove Base HAT ADC — validado em 0x08 (Seeed documenta 0x04)
_ultrasonic = GroveUltrasonicRanger(5)  # Ultrasonic em D5 (GPIO 5)

_dht_cache = {"humi": 0.0, "temp": 0.0, "ts": 0.0}
_DHT_TTL = 3.0  # segundos — evita leitura dupla quando GET pede temp+humi juntos

_SGP41_ADDR = 0x59
_sgp41_ready = False
_sgp41_lock = threading.Lock()


def _read_dht():
    if time.monotonic() - _dht_cache["ts"] >= _DHT_TTL:
        humi, temp = _dht.read()
        _dht_cache.update(
            {"humi": round(humi, 1), "temp": round(temp, 1), "ts": time.monotonic()}
        )
    return _dht_cache["humi"], _dht_cache["temp"]


def _crc8(data):
    """CRC-8 Sensirion: polinômio 0x31, valor inicial 0xFF."""
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def _ensure_sgp41_ready():
    """
    Conditioning loop do SGP41 (execute_conditioning, 0x2612) — chamado pela
    background thread. Não bloqueia as funções do sensor (retornam -1 enquanto aquece).
    """
    global _sgp41_ready
    with _sgp41_lock:
        if _sgp41_ready:
            return

    rh = [0x80, 0x00]
    temp = [0x66, 0x66]
    payload = rh + [_crc8(rh)] + temp + [_crc8(temp)]

    for _ in range(10):  # 10 × ~1 s = ~10 s de conditioning
        with smbus2.SMBus(1) as bus:
            cmd = smbus2.i2c_msg.write(_SGP41_ADDR, [0x26, 0x12] + payload)
            bus.i2c_rdwr(cmd)
            time.sleep(0.055)
            res = smbus2.i2c_msg.read(_SGP41_ADDR, 3)
            bus.i2c_rdwr(res)
        time.sleep(0.945)

    _sgp41_ready = True


# Pré-aquece o SGP41 em background — pronto antes do primeiro FLOW
threading.Thread(target=_ensure_sgp41_ready, daemon=True).start()


def _sgp41_measure_raw():
    """Retorna (SRAW_VOC, SRAW_NOX). Assume _sgp41_ready = True."""
    rh = [0x80, 0x00]
    temp = [0x66, 0x66]
    payload = rh + [_crc8(rh)] + temp + [_crc8(temp)]
    with smbus2.SMBus(1) as bus:
        cmd = smbus2.i2c_msg.write(_SGP41_ADDR, [0x26, 0x19] + payload)
        bus.i2c_rdwr(cmd)
        time.sleep(0.055)
        res = smbus2.i2c_msg.read(_SGP41_ADDR, 6)
        bus.i2c_rdwr(res)
    data = list(res)
    return (data[0] << 8) | data[1], (data[3] << 8) | data[4]


# ── Funções TATU (nome = nome do sensor em config.json) ──────────────────────

def temperatureSensor():
    _, temp = _read_dht()
    return temp


def humiditySensor():
    humi, _ = _read_dht()
    return humi


def lightSensor():
    return _adc.read(0)


def soundSensor():
    return _adc.read(2)


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


def vocSensor():
    """SGP41 SRAW_VOC 0–65535. Retorna -1 nos ~10 s iniciais (warmup)."""
    if not _sgp41_ready:
        return -1
    return _sgp41_measure_raw()[0]


def noxSensor():
    """SGP41 SRAW_NOX 0–65535. Retorna -1 nos ~10 s iniciais (warmup)."""
    if not _sgp41_ready:
        return -1
    return _sgp41_measure_raw()[1]
