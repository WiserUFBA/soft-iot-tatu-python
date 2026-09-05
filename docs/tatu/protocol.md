# TATU — protocolo e mensagens

Este documento descreve o comportamento da implementação atual presente neste repositório. Ele não redefine o protocolo.

## Tópicos MQTT

Com a configuração padrão atual:

```json
{
  "topicPrefix": "dev/",
  "topicReq": "/REQ",
  "topicRes": "/RES",
  "topicErr": "/ERR"
}
```

para um dispositivo `pizerosensor01`, os principais tópicos são:

```text
dev/pizerosensor01/REQ/#
dev/pizerosensor01/RES
dev/pizerosensor01/ERR
```

O nó assina requisições em `/REQ/#` e publica respostas em `/RES`.

## GET

### Leitura de um sensor

Requisição:

```json
{"method":"GET", "sensor":"temperatureSensor"}
```

Resposta:

```json
{
  "header": {
    "method": "GET",
    "device": "deviceName",
    "sensor": "temperatureSensor"
  },
  "payload": {
    "sensors": [
      {"temperatureSensor": [27.4]}
    ]
  }
}
```

`payload.sensors` é uma lista de objetos — um por sensor lido.

### Leitura de todos os sensores

Para solicitar todos os sensores de um dispositivo, a implementação compara o campo `sensor` ao `deviceName`.

```json
{"method":"GET", "sensor":"pizerosensor01"}
```

## FLOW

FLOW permite coletar dados em uma frequência e publicá-los em outra.

```json
{
  "method":"FLOW",
  "sensor":"temperatureSensor",
  "time": {
    "collect": 5,
    "publish": 30
  }
}
```

- `collect = 5`: ler o sensor a cada 5 segundos;
- `publish = 30`: publicar o conjunto de leituras quando o tempo acumulado atingir 30 segundos.

Se `time` for omitido, `collect` e `publish` assumem o valor padrão de 1 segundo.

Para todos os sensores do dispositivo, use o `deviceName` no campo `sensor`.

## EVENT

EVENT monitora um sensor e publica quando o valor muda.

```json
{
  "method":"EVENT",
  "sensor":"motionSensor",
  "time": {
    "collect":1
  }
}
```

A implementação:

1. lê um valor inicial;
2. publica esse valor;
3. espera `collect` segundos;
4. lê novamente;
5. publica apenas quando o valor for diferente do anterior.

A versão atual não implementa EVENT para todos os sensores de um dispositivo como uma única operação.

## STOP

Encerra uma operação FLOW ou EVENT em andamento.

### Mensagem de requisição

```json
{"method":"STOP", "target":"FLOW", "sensor":"temperatureSensor"}
```

Campos:

- `target`: método a encerrar (`FLOW` ou `EVENT`); padrão `FLOW` quando omitido;
- `sensor`: nome do sensor usado na operação a encerrar.

O identificador interno da thread-alvo é `<target>_<deviceName>_<sensor>`. A operação é encerrada imediatamente — o loop para ao receber o sinal, sem aguardar o próximo ciclo de coleta.

Não há resposta publicada para STOP.

## POST

Envia um valor para um atuador e publica a confirmação.

### Mensagem de requisição

```json
{"method":"POST", "sensor":"ledActuator", "value":true}
```

A função `ledActuator(value)` deve existir em `sensors.py` e aceitar o valor recebido como argumento.

### Resposta

```json
{
  "header": {
    "method": "POST",
    "device": "deviceName",
    "sensor": "ledActuator",
    "value": true
  },
  "payload": {"value": true}
}
```

O campo `value` no payload reflete o valor retornado pela função em `sensors.py`.

## Erros

Quando uma operação não consegue localizar/ler um sensor, a implementação publica mensagens no tópico de erro.

```json
{
  "code":"ERROR",
  "number":1,
  "message":"..."
}
```

## Convenção de nomes de sensores

O README atual sugere nomes em `camelCase`, por exemplo:

```text
temperatureSensor
humiditySensor
motionSensor
soundSensor
co2Sensor
```

Na implementação atual, esse nome deve corresponder a uma função com o mesmo nome em `sensors.py`.

## Checklist de validação do protocolo

- [ ] conexão com broker;
- [ ] assinatura do tópico `/REQ/#`;
- [ ] GET de um sensor;
- [ ] GET do dispositivo completo;
- [ ] FLOW de um sensor;
- [ ] FLOW do dispositivo, quando necessário;
- [ ] EVENT em sensor compatível;
- [ ] STOP de FLOW/EVENT;
- [ ] POST em atuador;
- [ ] mensagem de erro para sensor inexistente;
- [ ] formato real dos payloads validado.
