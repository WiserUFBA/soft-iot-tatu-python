# TATU — visão geral para novos desenvolvedores

## O que é o TATU

TATU (*Tiny Application for Things Universal*) é um protocolo leve de aplicação para comunicação entre dispositivos IoT sobre MQTT. A implementação deste repositório usa mensagens JSON padronizadas para solicitar leituras, iniciar fluxos periódicos e receber eventos.

A ideia central é separar a aplicação que consome os dados da lógica específica de cada sensor.

```text
Aplicação / consumidor
        |
        |  requisições TATU via MQTT
        v
     Broker MQTT
        |
        v
      Nó TATU
        |
        v
 Sensor / atuador físico
```

## Componentes da implementação atual

### `main.py`

É o processo principal do nó. Atualmente ele:

- carrega `config.json`;
- conecta ao broker MQTT;
- assina o tópico de requisições do dispositivo;
- recebe mensagens JSON;
- trata `STOP` sinalizando o `threading.Event` da operação alvo;
- cria uma thread daemon por operação TATU iniciada (GET, FLOW, EVENT, POST).

O tópico assinado é construído como:

```text
<topicPrefix><deviceName><topicReq>/#
```

### `tatu.py`

Contém a lógica das operações do protocolo.

A implementação atual suporta operacionalmente:

- `GET` — leitura imediata;
- `FLOW` — coleta periódica com publicação periódica;
- `EVENT` — publicação quando o valor muda;
- `POST` — envio de valor a um atuador e publicação de confirmação;
- `STOP` — interrupção imediata de operações FLOW ou EVENT em andamento.

### `sensors.py`

É a camada mais diretamente editada para adaptar um nó a sensores específicos.

Na implementação atual, o nome da função Python precisa ser igual ao nome do sensor no `config.json`.

```python
def humiditySensor():
    return read_humidity_from_hardware()
```

Configuração correspondente:

```json
{"type":"float", "name":"humiditySensor"}
```

O TATU usa `getattr()` para localizar essa função durante a execução.

Para atuadores (POST), a função deve aceitar o valor recebido como argumento:

```python
def ledActuator(value):
    gpio.set(LED_PIN, value)
    return value
```

### `config.json`

Define a identidade do nó, sensores disponíveis e parâmetros MQTT:

```text
deviceName
sensors[]
mqttBroker
mqttPort
mqttUsername
mqttPassword
topicPrefix
topicReq
topicRes
topicErr
```

### `config.py`

Fornece uma aplicação Flask simples para visualizar/alterar parte de `config.json` por meio de uma interface web. É uma ferramenta opcional de configuração e não é necessária para compreender o protocolo.

### `sensorsExamples/`

Contém implementações antigas e exemplos de sensores reais, incluindo DHT11, distância, chama, microfone e exemplos para plataformas como Raspberry Pi Zero e Intel Galileo.

Esses exemplos devem ser usados como referência, não necessariamente copiados sem revisão: dependências de hardware e bibliotecas podem ter mudado.

## Fluxo de uma requisição GET

Exemplo:

```json
{"method":"GET", "sensor":"temperatureSensor"}
```

Fluxo simplificado:

```text
1. cliente publica GET no tópico /REQ
2. broker entrega a mensagem ao nó TATU
3. main.py recebe a mensagem
4. cria uma thread daemon que executa tatu.main()
5. tatu.py identifica o sensor solicitado
6. tatu.py procura temperatureSensor() em sensors.py
7. a função lê o sensor
8. tatu.py monta a resposta JSON
9. a resposta é publicada em /RES
```

## Fluxo FLOW

`FLOW` separa duas frequências:

- `collect`: intervalo entre leituras;
- `publish`: intervalo entre publicações.

```json
{
  "method":"FLOW",
  "sensor":"temperatureSensor",
  "time":{"collect":5,"publish":30}
}
```

Interpretação:

```text
ler a cada 5 s
acumular leituras
publicar aproximadamente a cada 30 s
```

A operação pode ser interrompida a qualquer momento com STOP.

## Fluxo EVENT

`EVENT` realiza leituras periódicas e publica quando o valor observado muda.

```json
{
  "method":"EVENT",
  "sensor":"motionSensor",
  "time":{"collect":1,"publish":0}
}
```

É especialmente útil para sensores cujo estado muda de forma esporádica.

A operação pode ser interrompida com STOP.

## Modelo mental de um nó

```text
Nó físico
├── Linux / Python
├── TATU
├── config.json
├── sensors.py
├── sensor(es) físico(s)
└── conexão de rede com o broker
```

## Limitações conhecidas da implementação atual

Sem propor refatoração neste momento, é importante reconhecer algumas características do código atual:

- configuração depende de caminhos/arquivos locais;
- sensores são descobertos pelo nome da função em `sensors.py`;
- `pub_client` aberto por operação: cada GET/FLOW/EVENT cria uma conexão MQTT própria ao broker;
- tratamento de exceções publica um erro genérico — detalhes aparecem apenas no log do processo;
- exemplos de hardware têm idades e dependências diferentes.

Esses pontos devem ser registrados durante o uso para orientar melhorias futuras.
