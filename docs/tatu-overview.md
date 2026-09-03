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

É o processo principal do nó.

Responsabilidades atuais:

- carregar `config.json`;
- conectar ao broker MQTT;
- assinar o tópico de requisições do dispositivo;
- receber mensagens JSON;
- tratar `STOP`;
- criar um processo para cada operação TATU iniciada.

O tópico assinado é construído como:

```text
<topicPrefix><deviceName><topicReq>/#
```

### `tatu.py`

Contém a lógica das operações do protocolo.

A implementação atual suporta operacionalmente:

- `GET` — leitura imediata;
- `FLOW` — coleta periódica com publicação periódica;
- `EVENT` — publicação quando o valor muda.

Há código referente a `POST`, mas o fluxo não está concluído no estado atual do repositório. Portanto, a equipe não deve assumir que `POST` está pronto para uso sem validação adicional.

### `sensors.py`

É a camada mais diretamente editada para adaptar um nó a sensores específicos.

Na implementação atual, o nome da função Python precisa ser igual ao nome do sensor no `config.json`.

Exemplo:

```python
def humiditySensor():
    return read_humidity_from_hardware()
```

Configuração correspondente:

```json
{"type":"float", "name":"humiditySensor"}
```

O TATU usa `getattr()` para localizar essa função durante a execução.

### `config.json`

Define a identidade do nó, sensores disponíveis e parâmetros MQTT.

Exemplo conceitual:

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

Fornece uma aplicação Flask simples para visualizar/alterar parte de `config.json` por meio de uma interface web.

Ela não é necessária para entender o protocolo e pode ser tratada como uma ferramenta opcional de configuração.

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
4. tatu.py identifica o sensor solicitado
5. tatu.py procura temperatureSensor() em sensors.py
6. a função lê o sensor
7. tatu.py monta resposta JSON
8. resposta é publicada em /RES
```

## Fluxo FLOW

`FLOW` separa duas frequências:

- `collect`: intervalo entre leituras;
- `publish`: intervalo entre publicações.

Exemplo:

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

Isso permite reduzir a quantidade de mensagens MQTT sem necessariamente reduzir a frequência de amostragem.

## Fluxo EVENT

`EVENT` realiza leituras periódicas e publica quando o valor observado muda.

Exemplo:

```json
{
  "method":"EVENT",
  "sensor":"motionSensor",
  "time":{"collect":1,"publish":0}
}
```

É especialmente útil para sensores cujo estado muda de forma esporádica.

## Modelo mental para o projeto PIBIC/PIBITI

Durante a implantação inicial no IC, pensem em cada nó como:

```text
Nó físico
├── Linux / Python
├── TATU
├── config.json
├── sensors.py
├── sensor(es) físico(s)
└── conexão de rede com o broker
```

E na infraestrutura completa como:

```text
[Nós IoT + TATU]
        |
       MQTT
        |
        v
[Broker no servidor]
        |
        +--> [Persistência dos dados]
        |
        +--> [AI Box]
```

## Limitações que os alunos devem conhecer

Sem refatorar nada agora, é importante reconhecer algumas características do código atual:

- configuração depende de caminhos/arquivos locais;
- sensores são descobertos pelo nome da função;
- há uso de processos para operações iniciadas;
- tratamento de exceções é bastante genérico;
- `POST` não está finalizado;
- exemplos de hardware têm idades e dependências diferentes;
- ainda não há uma suíte de testes automatizados consolidada.

Esses pontos não são tarefas de refatoração neste momento. Devem apenas ser registrados durante a implantação para orientar melhorias futuras.
