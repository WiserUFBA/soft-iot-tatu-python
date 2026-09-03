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

Resposta gerada pela implementação atual segue a estrutura:

```json
{
  "header": {
    "method": "GET",
    "device": "deviceName",
    "sensor": "temperatureSensor"
  },
  "payload": {
    "sensors": [
      {"temperatureSensor": ["27.4"]}
    ]
  }
}
```

Observação: o README histórico mostra exemplos de payloads com objeto em alguns trechos, enquanto `tatu.py` atualmente monta `payload.sensors` como uma lista de objetos. Considere o comportamento do código executado como referência e valide consumidores com mensagens reais.

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

Para todos os sensores do dispositivo, use o `deviceName` no campo `sensor`.

## EVENT

EVENT monitora um sensor e publica quando o valor muda.

```json
{
  "method":"EVENT",
  "sensor":"motionSensor",
  "time": {
    "collect":1,
    "publish":0
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

`main.py` trata mensagens com método `STOP` para terminar um processo TATU anteriormente iniciado.

A identificação do processo segue o padrão interno:

```text
<METHOD>_<deviceName>_<sensorName>
```

A mensagem STOP utiliza `target` para indicar qual operação deve ser interrompida.

Antes de usar STOP em produção, teste e registre exemplos concretos de mensagens válidas, pois o README atual não documenta esse método com o mesmo nível de detalhe dos demais.

## POST

O protocolo possui intenção de suporte a POST/atuadores e há código relacionado a essa operação, mas o fluxo está incompleto na implementação atual.

Em `tatu.py`, a função `buildPostAnwserDevice()` existe, porém o despacho em `main()` atualmente não a executa: para `met == "POST"`, o código faz apenas `pass`.

> **Não considerar POST funcional sem implementação e testes adicionais.**

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
- [ ] mensagem de erro para sensor inexistente;
- [ ] formato real dos payloads validado.