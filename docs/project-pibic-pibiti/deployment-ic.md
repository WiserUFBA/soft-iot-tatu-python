# Implantação inicial no Instituto de Computação (IC/UFBA)

> **Documento específico do projeto PIBIC/PIBITI.** Mantido temporariamente neste repositório porque o TATU será usado na infraestrutura inicial. Deve ser migrado posteriormente para o repositório próprio do projeto.

Este documento organiza a primeira fase do trabalho da equipe: colocar uma infraestrutura IoT mínima, estável e documentada em funcionamento no IC.

## Objetivo da fase

A infraestrutura mínima deve permitir:

```text
sensores reais
    ↓
nós TATU
    ↓
MQTT broker
    ↓
armazenamento no servidor
    ↓
AI Box
```

A prioridade é ter um fluxo ponta a ponta funcional. Novas funcionalidades vêm depois.

## 1. Nós IoT

Cada nó deve ter:

- hardware definido (ESP32, Raspberry Pi ou equivalente);
- sensor(es) conectado(s);
- conectividade com a rede do IC;
- um `deviceName` único;
- TATU configurado;
- serviço de inicialização/reinicialização documentado;
- localização física registrada.

### Sugestão de identificação

Use um padrão que identifique local e número do nó, por exemplo:

```text
ic-lab01-node01
ic-lab01-node02
ic-corredor2-node01
```

A equipe deve aprovar um padrão único antes de espalhar os dispositivos.

## 2. Broker MQTT

O broker ficará inicialmente em um servidor já existente.

Antes da implantação, a equipe deve avaliar o estado desse servidor e decidir se será necessária reinstalação/formatação.

Checklist:

- [ ] inventariar SO e serviços existentes;
- [ ] decidir manter ou reinstalar;
- [ ] definir hostname/IP estável;
- [ ] instalar/configurar broker MQTT;
- [ ] definir autenticação;
- [ ] restringir acesso de rede quando possível;
- [ ] configurar serviço para iniciar automaticamente;
- [ ] definir retenção/logs necessários;
- [ ] testar publish/subscribe a partir de outra máquina.

Não versionar usuário/senha reais no repositório.

## 3. Persistência dos dados

No primeiro momento, broker e armazenamento poderão compartilhar o mesmo servidor.

A escolha final do banco/serviço de persistência deve atender ao fluxo experimental do projeto e à AI Box.

Independentemente da tecnologia escolhida, registrar:

- timestamp de recebimento;
- `deviceName`;
- sensor;
- método TATU;
- valor(es);
- tópico MQTT de origem;
- payload original quando útil para auditoria.

O consumidor responsável por persistir as mensagens deve ser executado como serviço e possuir logging básico.

## 4. Fluxo TATU esperado

Para um dispositivo `ic-lab01-node01` com a convenção atual:

```text
requisições: dev/ic-lab01-node01/REQ/#
respostas:   dev/ic-lab01-node01/RES
erros:       dev/ic-lab01-node01/ERR
```

Durante os primeiros testes, use ferramentas MQTT de linha de comando ou cliente equivalente para observar diretamente os tópicos.

## 5. Estratégia de implantação

Não instalar todos os dispositivos de uma vez.

### Etapa A — laboratório

1. broker funcionando;
2. um nó TATU com sensores simulados;
3. GET/FLOW/EVENT testados;
4. persistência funcionando;
5. um sensor físico integrado;
6. fluxo completo repetido.

### Etapa B — piloto no IC

Instalar 1 ou 2 nós físicos em locais fáceis de acessar.

Observar por alguns dias:

- conectividade;
- perdas de mensagens;
- reinicializações;
- estabilidade do sensor;
- crescimento do banco/logs;
- comportamento após queda do broker/servidor.

### Etapa C — expansão

Somente depois do piloto estável, espalhar novos nós no IC.

## 6. Integração com a AI Box

A AI Box parte da versão atual já em desenvolvimento pelo grupo.

Na primeira fase, o objetivo não é fazer todos os recursos avançados da AI Box. O objetivo é garantir que ela consiga participar da infraestrutura instalada.

Primeiro marco desejado:

```text
TATU -> MQTT -> storage
              ↓
           AI Box
```

A AI Box deverá inicialmente conseguir consumir/consultar os dados necessários e possuir health/logs suficientes para comprovar que está operacional.

## 7. Informações que devem ser registradas para cada nó

Crie um inventário com pelo menos:

| Campo | Exemplo |
|---|---|
| deviceName | `ic-lab01-node01` |
| Local físico | Lab 01 |
| Hardware | Raspberry Pi Zero 2 W |
| Sensor | DHT11 |
| IP/hostname | conforme rede |
| Tópicos | `dev/...` |
| Responsável pela implantação | aluno |
| Data de instalação | YYYY-MM-DD |
| Estado | piloto / ativo / manutenção |

Não registrar credenciais no inventário versionado.

## 8. Testes mínimos de cada nó

- [ ] boot e conexão de rede;
- [ ] processo TATU inicia;
- [ ] conexão com broker;
- [ ] GET funciona;
- [ ] FLOW funciona, quando utilizado;
- [ ] EVENT funciona, quando utilizado;
- [ ] mensagens chegam ao armazenamento;
- [ ] reinício do dispositivo recupera operação;
- [ ] interrupção temporária do broker foi observada/testada;
- [ ] localização e configuração foram documentadas.

## 9. Definition of Done da infraestrutura mínima

Consideramos o primeiro marco concluído quando:

- existem nós TATU com sensores reais instalados no IC;
- o broker MQTT está operacional no servidor;
- as mensagens dos nós são recebidas e persistidas;
- a AI Box está executando no IC e integrada ao fluxo mínimo;
- os serviços essenciais reiniciam de forma previsível;
- existe logging suficiente para diagnóstico;
- a infraestrutura foi testada ponta a ponta;
- outra pessoa da equipe consegue reproduzir a instalação usando a documentação.

## 10. Evidências a manter no GitHub

Para cada etapa relevante, use Issues/PRs para registrar:

- procedimento executado;
- decisões tomadas;
- configurações não sensíveis;
- problemas encontrados;
- evidências de teste;
- documentação atualizada.

A regra para a equipe deve ser simples: **uma implantação que só uma pessoa sabe reproduzir ainda não está concluída.**