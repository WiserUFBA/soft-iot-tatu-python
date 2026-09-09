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

---

## Sensor examples

Arquivos `sensors.py` prontos para uso estão em [`src/sensorsExamples/`](src/sensorsExamples/):

| Arquivo | Hardware | Sensores / variáveis TATU |
|---------|----------|--------------------------|
| [`sensors_rpi4_grove.py`](src/sensorsExamples/sensors_rpi4_grove.py) | RPi4 + Grove Base HAT | `temperatureSensor`, `humiditySensor`, `lightSensor`, `soundSensor`, `ultrasonicSensor`, `vocSensor`, `noxSensor` |
| [`sensors_rpi_zero_grove.py`](src/sensorsExamples/sensors_rpi_zero_grove.py) | RPi Zero W 2 + Grove Base HAT | `temperatureSensor`, `humiditySensor`, `lightSensor`, `soundSensor`, `ultrasonicSensor` |

Instale as dependências de hardware antes de usar os exemplos Grove:

```bash
pip install -r src/sensorsExamples/requirements-grove-hat.txt
```

Para usar um exemplo, copie para `src/tatu/sensors.py`:

```bash
# RPi4 + Grove Base HAT
cp src/sensorsExamples/sensors_rpi4_grove.py src/tatu/sensors.py

# RPi Zero W 2 + Grove Base HAT
cp src/sensorsExamples/sensors_rpi_zero_grove.py src/tatu/sensors.py
```

> **Se você usa `iot-infrastructure`:** o `run.sh` de cada device faz esse symlink automaticamente.
> Não copie manualmente — o `run.sh` é o ponto de entrada correto.

Valide cada função manualmente antes de iniciar o TATU (executar de dentro de `src/tatu/`):

```bash
cd src/tatu
python3 -c "import sensors; print(sensors.temperatureSensor())"
```

---

## Notas de hardware — Grove Base HAT (IC/UFBA, validado 2026-09-09)

Esses problemas já foram resolvidos nos arquivos de exemplo. Leia para não perder tempo depurando o que já tem solução.

### ADC responde em 0x08, não 0x04

A documentação da Seeed indica que o ADC do Grove Base HAT fica no endereço I2C `0x04`. No hardware do IC/UFBA (e provavelmente em outros), o ADC responde em **`0x08`**. Use sempre `ADC(0x08)` no código:

```python
from grove.adc import ADC
_adc = ADC(0x08)   # 0x04 não funciona neste hardware
```

### SGP41 não aparece em i2cdetect

O `i2cdetect -y 1` não mostra o SGP41 (endereço `0x59`) mesmo com o sensor corretamente conectado. Isso é um bug conhecido do BCM2835 (chip I2C do RPi): durante a fase de probe, o SGP41 estica o clock e o BCM2835 interpreta como NACK.

**O sensor funciona normalmente para comunicação real** — apenas a probe do i2cdetect falha.

**Workaround obrigatório:** adicionar em `/boot/firmware/config.txt` e reiniciar:

```ini
dtparam=i2c_arm_baudrate=10000
```

**Confirmar que o sensor está presente** (funciona mesmo sem aparecer no i2cdetect):

```bash
sudo i2ctransfer -y 1 w2@0x59 0x36 0x82 r9@0x59
```

Retornando 9 bytes → sensor OK. Se der erro → verificar cabo/porta.

**Não use** `sensirion-i2c-sgp41` — os exemplos usam `smbus2` diretamente com CRC-8 manual, que é mais leve e não tem a dependência da biblioteca Sensirion.

### ultrasonicSensor — timeout de 1 s

O driver Grove do Ultrasonic Ranger pode bloquear indefinidamente se não houver eco (objeto fora da faixa ou ausente). Os exemplos resolvem isso com uma thread daemon e timeout:

```python
import threading

def ultrasonicSensor():
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
```

Retorna `-1.0` se nenhum eco for recebido em 1 s. Seguro incluir no FLOW sem objeto na frente.

### SGP41 — warmup de ~10 s

O SGP41 precisa de ~10 s de conditioning antes de produzir leituras estáveis. Os exemplos fazem o conditioning em uma background thread ao importar o módulo, e retornam `-1` enquanto não estiver pronto:

```python
vocSensor()   # → -1 nos primeiros ~10 s, depois SRAW_VOC (0–65535)
noxSensor()   # → -1 nos primeiros ~10 s, depois SRAW_NOX (0–65535)
```

O TATU não é bloqueado durante o warmup — os primeiros valores no FLOW virão como `-1`.

**Os valores SRAW são sinais brutos** (0–65535). Para obter índices VOC/NOx (0–500) é necessário o Gas Index Algorithm (GIA) da Sensirion, que será aplicado no servidor.

### Biblioteca DHT22 — grove, não adafruit

Os exemplos usam `grove.grove_temperature_humidity_sensor.DHT`, não `adafruit_dht`. A biblioteca adafruit tem conflitos com o GPIO do Grove Base HAT no RPi:

```python
from grove.grove_temperature_humidity_sensor import DHT
_dht = DHT("22", 16)   # DHT22 em GPIO 16 (porta D16)
```

---

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
