# Getting Started — TATU

Este guia explica como executar a implementação atual do TATU e validar um nó antes de conectá-lo a uma infraestrutura maior.

## 1. Estrutura relevante

```text
soft-iot-tatu-python/
└── src/
    ├── requests.txt          (dependências antigas — referência histórica)
    ├── sensorsExamples/
    └── tatu/
        ├── requirements.txt  ← instalar com pip install -r
        ├── config.json
        ├── config.py
        ├── main.py
        ├── sensors.py
        ├── tatu.py
        └── templates/
```

Arquivos centrais:

- `src/tatu/config.json`: identidade do dispositivo, sensores, broker e tópicos MQTT;
- `src/tatu/sensors.py`: funções que representam os sensores/atuadores disponíveis;
- `src/tatu/main.py`: processo principal que conecta ao broker e recebe requisições;
- `src/tatu/tatu.py`: implementação das operações TATU;
- `src/sensorsExamples/`: exemplos de integração com sensores reais.

## 2. Dependências

```bash
pip install -r src/tatu/requirements.txt
```

Requer Python 3.11+ (Raspberry Pi OS Bookworm ou equivalente). A implementação usa principalmente:

- `paho-mqtt>=2.0.0`;
- `flask`, caso a página opcional de configuração seja utilizada;
- bibliotecas específicas do hardware para sensores reais.

Antes de usar um sensor físico, valide a versão do Python e as dependências exigidas pelo hardware.

## 3. Configurando um nó

Edite `src/tatu/config.json`.

Exemplo:

```json
{
  "deviceName": "pizerosensor01",
  "sensors": [
    {"type": "int",  "name": "humiditySensor"},
    {"type": "int",  "name": "temperatureSensor"},
    {"type": "bool", "name": "ledActuator"}
  ],
  "mqttBroker": "10.8.0.30",
  "mqttPort": 1883,
  "mqttUsername": "",
  "mqttPassword": "",
  "topicPrefix": "dev/",
  "topicReq": "/REQ",
  "topicRes": "/RES",
  "topicErr": "/ERR"
}
```

Campos principais:

- `deviceName`: identificador único do nó;
- `sensors`: sensores e atuadores disponíveis;
- `mqttBroker`: endereço do broker MQTT;
- `mqttPort`: porta MQTT;
- `mqttUsername` / `mqttPassword`: credenciais, quando utilizadas;
- `topicPrefix`: prefixo dos tópicos;
- `topicReq`: sufixo de requisições;
- `topicRes`: sufixo de respostas;
- `topicErr`: sufixo de erros.

## 4. Implementando sensores e atuadores

O código atual localiza dinamicamente uma função em `sensors.py` cujo nome precisa ser exatamente igual ao `name` configurado em `config.json`.

**Sensor** (sem argumento):

```python
def temperatureSensor():
    return 27.4
```

**Atuador** (POST — aceita o valor recebido):

```python
def ledActuator(value=None):
    if value is None:
        return False        # leitura simulada
    print("LED:", value)
    return value            # substituir por lógica real de GPIO
```

O arquivo `src/tatu/sensors.py` inclui sensores simulados com valores aleatórios e `ledActuator` para teste de POST. Consulte `src/sensorsExamples/` para adaptação a hardware real.

## 5. Executando

A implementação atual deve ser executada a partir do diretório que contém `config.json` e `sensors.py`.

```bash
cd src/tatu
python main.py
```

Ao conectar, o nó assina:

```text
<topicPrefix><deviceName><topicReq>/#
```

Com a configuração de exemplo:

```text
dev/pizerosensor01/REQ/#
```

As respostas são publicadas em:

```text
dev/pizerosensor01/RES
```

E erros em:

```text
dev/pizerosensor01/ERR
```

## 6. Primeiro teste recomendado

1. execute o TATU com os sensores simulados de `sensors.py`;
2. confirme a conexão com o broker;
3. publique uma requisição `GET`;
4. confirme a resposta em `/RES`;
5. teste `FLOW`;
6. teste `STOP` para encerrar o FLOW;
7. teste `POST` com `ledActuator`;
8. teste `EVENT`;
9. somente depois substitua as funções simuladas por sensores físicos.

Exemplos:

```json
{"method":"GET", "sensor":"temperatureSensor"}
```

```json
{"method":"FLOW", "sensor":"temperatureSensor", "time":{"collect":5,"publish":30}}
```

```json
{"method":"STOP", "target":"FLOW", "sensor":"temperatureSensor"}
```

```json
{"method":"POST", "sensor":"ledActuator", "value":true}
```

## 7. Critério mínimo de validação de um nó

Um nó pode ser considerado funcional quando:

- possui `deviceName` único;
- conecta ao broker;
- responde a `GET`;
- opera `FLOW` quando aplicável;
- `STOP` encerra operações corretamente;
- opera `EVENT` quando aplicável;
- opera `POST` em atuadores quando aplicável;
- publica respostas no tópico esperado;
- a configuração utilizada está documentada sem expor credenciais.

## 8. Cuidados

- não versionar senhas reais;
- não alterar o formato do protocolo sem necessidade;
- validar exemplos de sensores físicos antes de reutilizá-los em hardware atual.

## Próxima leitura

- [Visão geral do TATU](tatu-overview.md)
- [Protocolo e mensagens](protocol.md)
