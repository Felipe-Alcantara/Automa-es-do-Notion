# 🔌 Portabilidade — como adaptar o projeto

> **O que é**: caminhos para reaproveitar este projeto fora do caso de uso original —
> outro domínio de tarefas, outro provedor de dados, ou até outra linguagem. O projeto
> nasceu como template tipado sobre o Notion; esta página mostra como dobrá-lo sem
> deformar o núcleo.

> Veja também: [MODELOS-DE-USO.md](MODELOS-DE-USO.md) e o `CONTRIBUTING.md` da raiz.

---

## 📋 Índice

- [🧬 O que torna o projeto portável](#-o-que-torna-o-projeto-portável)
- [🎯 Portar para outro domínio](#-portar-para-outro-domínio)
- [🔄 Portar para outro provedor de dados](#-portar-para-outro-provedor-de-dados)
- [🌐 Portar para outra linguagem](#-portar-para-outra-linguagem)
- [📦 Usar como template](#-usar-como-template)

---

## 🧬 O que torna o projeto portável

Três escolhas de arquitetura facilitam a adaptação:

- **Integração isolada** — o formato cru do Notion vive só no cliente; o resto do código
  não depende dele. Trocar o provedor é trocar uma camada, não o sistema.
- **Colunas configuráveis** — a `TaskList` aceita `CamposTarefa`, então o mesmo código
  serve a databases que nomeiam as colunas de forma diferente.
- **Ferramenta antes da solução** — primeiro a peça reutilizável (cliente, helpers,
  tasklist), depois a aplicação concreta por cima. A aplicação é uma composição, não um
  bloco rígido.

---

## 🎯 Portar para outro domínio

A `TaskList` é uma camada de "tasklist", mas o padrão serve a qualquer database de
domínio. Generalizar é o caminho:

- **Hoje**: `TaskList` mapeia um database de tarefas para um objeto `Tarefa`.
- **Ideia aberta**: extrair um padrão reutilizável — uma camada que mapeia *qualquer*
  database para um objeto de domínio, configurada por quais colunas ler e como
  convertê-las. A `TaskList` vira um caso particular dessa base.

Exemplos de domínios que cairiam no mesmo molde: leituras/livros, hábitos, finanças
pessoais, CRM leve, conteúdo (artigos/roteiros), estudos. Em todos, o que muda são as
colunas e os valores — não a mecânica de ler/criar/atualizar.

**Passo prático**: comece copiando o padrão de `tarefa_de_pagina` (conversão pura,
testável sem rede) para o seu domínio, e mantenha a conversão separada do I/O.

---

## 🔄 Portar para outro provedor de dados

A visão trata o Notion como "o banco". Se um dia o banco for outro (uma planilha, um
SQLite, uma API), a fronteira certa já existe:

- O **cliente** é a camada de integração. Um novo provedor é um novo cliente que oferece
  as mesmas operações de alto nível (listar, criar, atualizar).
- As **camadas acima** (tasklist, casos de uso, front) não deveriam precisar saber qual
  provedor está embaixo. Modele a operação por trás de um contrato (estratégia/adaptador)
  e deixe cada provedor implementá-lo.

Isso também abre espaço para **sincronização entre fontes** (ex.: arquivos locais ou
GitHub → Notion), que é justamente o que as Fases 3 e 4 do [PLANO.md](PLANO.md) exploram.

---

## 🌐 Portar para outra linguagem

O projeto é Python, mas a arquitetura é independente de linguagem. Se a equipe preferir
outro ecossistema, o que se preserva é o **desenho**, não o código:

- As **camadas** (cliente isolado, helpers de propriedade, tasklist de alto nível,
  casos de uso finos) se traduzem direto.
- Os **contratos** (objetos simples de domínio, paginação, exceções explícitas) são os
  mesmos.
- Os **padrões de integração** (retry com backoff, tratamento de rate limit,
  idempotência) valem em qualquer linguagem.

Use os módulos atuais como especificação executável: cada um documenta um contrato que a
porta para outra linguagem deve respeitar.

---

## 📦 Usar como template

O caminho de uso mais comum é clonar e adaptar:

1. **Renomear o pacote** para o seu projeto (uma ideia aberta é automatizar isso com um
   comando — ver [IDEIAS-EXTRAS.md](IDEIAS-EXTRAS.md)).
2. **Definir o schema** do seu database e validá-lo com a comparação de schema antes de
   escrever.
3. **Configurar as colunas** da sua tasklist (ou da sua camada de domínio) via
   `CamposTarefa` ou equivalente.
4. **Trocar a fonte de dados** nos exemplos para o seu caso real.
5. **Manter os guarda-corpos**: token fora do repositório, testes com HTTP mockado,
   `start_app.py` como porta de entrada, documentação viva.

O objetivo do template é dar um ponto de partida sólido — não um produto fechado. Adapte
à vontade e mantenha a separação de responsabilidades que ele já traz.
