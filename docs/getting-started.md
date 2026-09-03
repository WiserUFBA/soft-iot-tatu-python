# Getting Started — TATU no IC/UFBA

Este guia foi preparado para a equipe PIBIC/PIBITI que irá usar o TATU como base dos nós IoT instalados no Instituto de Computação (IC/UFBA).

## Objetivo inicial

A primeira meta não é refatorar o TATU. O objetivo é entender a implementação atual, colocá-la para funcionar com sensores reais e usá-la para construir uma infraestrutura mínima:

```text
sensor -> nó TATU -> MQTT broker -> armazenamento -> AI Box
```

Quando essa infraestrutura estiver operacional e documentada, evoluções arquiteturais podem ser discutidas com base nas dificuldades observadas na prática.

## 1. Estrutura atual relevante

```text
soft-iot-tatu-python/
├── README.md
└── src/
    ├── requests.txt
    ├── sensorsExamples/
    └── tatu/
        ├── config.json
        ├── config.py
        ├── main.py
        ├── sensors.py
        ├── tatu.py
        └── templates/
```

Os arquivos centrais para começar são:

- `src/tatu/config.json`: configuração do dispositivo, sensores, broker e tópicos MQTT;
- `src/tatu/sensors.py`: funções que representam os sensores/atuadores disponíveis naquele nó;
- `src/tatu/main.py`: processo principal que conecta ao broker, assina o tópico de requisições e inicia o processamento TATU;
- `src/tatu/tatu.py`: implementação das operações TATU (`GET`, `FLOW`, `EVENT`; `POST` ainda não está concluído na implementação atual);
- `src/sensorsExamples/`: exemplos de integração com sensores reais.

## 2. Dependências

A implementação usa Python e MQTT. O código atual importa principalmente:

- `paho-mqtt`;
- `flask` para a página opcional de configuração;
- bibliotecas específicas de hardware dependendo do sensor utilizado.

Antes de instalar um nó real, valide a versão de Python e as dependências exigidas pelo sensor escolhido.

## 3. Configurando um nó

Edite `src/tatu/config.json`.

Exemplo atual:

```json
{
  "deviceName": "pizerosensor01",
  "sensors": [
    {"type": "int", "name": "humiditySensor"},
    {"type": "int", "name": "temperatureSensor"}
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

### Campos importantes

- `deviceName`: identificador único do nó;
- `sensors`: sensores disponíveis nesse nó;
- `mqttBroker`: endereço do servidor MQTT;
- `mqttPort`: porta MQTT;
- `mqttUsername` / `mqttPassword`: credenciais, quando utilizadas;
- `topicPrefix`: prefixo comum dos tópicos;
- `topicReq`: sufixo usado para requisições;
- `topicRes`: sufixo usado para respostas;
- `topicErr`: sufixo usado para erros.

Para os nós do IC, adotaremos nomes consistentes e únicos. Exemplo:

```text
ic-lab01-node01
ic-corredor2-node01
ic-sala123-node01
```

O padrão definitivo deve ser acordado pela equipe antes da implantação em escala.

## 4. Implementando sensores

O código atual localiza dinamicamente uma função em `sensors.py` cujo nome precisa ser exatamente igual ao `name` configurado em `config.json`.

Exemplo:

```python
def temperatureSensor():
    return 27.4
```

E no `config.json`:

```json
{
  "type": "float",
  "name": "temperatureSensor"
}
```

Essa correspondência de nomes é obrigatória na implementação atual.

O arquivo `src/tatu/sensors.py` vem com sensores simulados usando números aleatórios. Use-os primeiro para validar MQTT e o protocolo antes de conectar hardware real.

Depois, consulte `src/sensorsExamples/` e adapte a leitura ao sensor físico que estiver sendo usado.

## 5. Executando

A implementação atual foi escrita para ser executada a partir do diretório que contém `config.json` e `sensors.py`.

Exemplo:

```bash
cd src/tatu
python main.py
```

Ao conectar, o nó assina o tópico de requisições:

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

Antes de instalar sensores reais:

1. execute o TATU com os sensores simulados de `sensors.py`;
2. confirme a conexão com o broker;
3. publique uma requisição `GET`;
4. confirme a resposta em `/RES`;
5. teste `FLOW`;
6. teste `EVENT`;
7. somente depois substitua as funções simuladas por sensores físicos.

Exemplo de requisição GET:

```json
{"method":"GET", "sensor":"temperatureSensor"}
```

## 7. Critério de pronto para um nó do IC

Um nó só deve ser considerado pronto quando:

- possui `deviceName` único;
- sensores reais estão documentados;
- conecta automaticamente ao broker;
- responde a `GET`;
- opera `FLOW` quando aplicável;
- opera `EVENT` quando aplicável;
- dados chegam ao broker com tópico e payload esperados;
- falhas de rede e reinicializações básicas foram testadas;
- localização física do nó está registrada;
- configuração do nó está documentada sem expor credenciais.

## 8. O que não fazer nesta primeira fase

- não alterar o protocolo sem necessidade;
- não refatorar `tatu.py` antes de a infraestrutura mínima funcionar;
- não colocar senhas reais no Git;
- não inventar formatos de tópico diferentes para cada nó;
- não instalar muitos nós antes de validar um fluxo ponta a ponta.

## Próxima leitura

- [Visão geral do TATU](tatu-overview.md)
- [Protocolo e mensagens](protocol.md)
- [Implantação no IC](deployment-ic.md)
