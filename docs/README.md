# 📚 Documentação — Automações do Notion

> **O que é esta pasta**: a documentação de visão e estratégia do projeto. Aqui mora o
> plano de longo prazo, os modelos de uso e os caminhos possíveis de evolução
> (portabilidade, SaaS, escala, otimização). É leitura para quem quer entender **onde o
> projeto está indo** e **como contribuir** — não a referência de API (essa fica no
> [`README.md`](../README.md) da raiz e nas docstrings do código).

---

## 🗂️ Índice da documentação

| Documento | Para quê serve |
|---|---|
| [🗺️ PLANO.md](PLANO.md) | **Comece aqui.** Roadmap completo, visão final, arquitetura-alvo e as fases de evolução. |
| [🎭 MODELOS-DE-USO.md](MODELOS-DE-USO.md) | Quem usa, em quais cenários, e os modos de operação (lib, CLI, servidor, IA, MCP). |
| [🔌 PORTABILIDADE.md](PORTABILIDADE.md) | Como adaptar para outro domínio, outro provedor ou outra linguagem. Usar como template. |
| [💼 SAAS.md](SAAS.md) | O que mudaria para virar um produto multiusuário (auth, multi-tenant, cobrança, segurança). |
| [🏗️ INFRA.md](INFRA.md) | Como o servidor roda local e é hospedado: estrutura de pastas, config por ambiente, SQLite operacional, deploy. |
| [🔄 INTEGRACOES.md](INTEGRACOES.md) | GitHub e arquivos locais: configuração, schemas, idempotência, segurança e exemplos de sincronização. |
| [📈 ESCALA.md](ESCALA.md) | Como crescer sem quebrar: fila de jobs, workers, cache, rate limit, observabilidade. |
| [⚡ OTIMIZACAO.md](OTIMIZACAO.md) | Como reduzir latência e custo (chamadas ao Notion e ao OpenRouter, cache, idempotência). |
| [💡 IDEIAS-EXTRAS.md](IDEIAS-EXTRAS.md) | Brainstorm aberto: funcionalidades e integrações além do roadmap. |
| [🤖 AGENTES.md](AGENTES.md) | Playbook de orquestração multi-agente: papéis, o que cada agente lê e entrega, ordem e coordenação (para o Felixo-AI-Core). |
| [🧱 CONTRATOS.md](CONTRATOS.md) | Contrato fixado pelo Agente 0: objetos de domínio, rotas REST, formato de erro e estrutura de pastas do servidor. |
| [🤖 IA-CAMADA.md](IA-CAMADA.md) | Camada de IA plugável: ProvedorIA, OpenRouter, catálogo de modelos, caso de uso copiloto (NL → tasklist). |
| [🔗 MCP.md](MCP.md) | Camada MCP: ferramentas `notion.*`, transportes, confirmação no catálogo do Felixo-AI-Core e estado da integração. |

---

## 🧭 Como ler, por objetivo

- **Quero entender a visão** → [PLANO.md](PLANO.md) → [MODELOS-DE-USO.md](MODELOS-DE-USO.md)
- **Vou implementar uma frente do Ciclo 2 (front React, CLI, API v2)** →
  [CONTRATOS.md](CONTRATOS.md) (o contrato) → [AGENTES.md](AGENTES.md) → [PLANO.md](PLANO.md) (*Ciclo 2*)
- **Quero reaproveitar o projeto** → [PORTABILIDADE.md](PORTABILIDADE.md)
- **Quero pensar em produto** → [SAAS.md](SAAS.md) → [ESCALA.md](ESCALA.md)
- **Quero entender a camada de IA** → [IA-CAMADA.md](IA-CAMADA.md)
- **Quero integrar com o Felixo-AI-Core via MCP** → [MCP.md](MCP.md)
- **Quero deixar mais rápido/barato** → [OTIMIZACAO.md](OTIMIZACAO.md)
- **Quero contribuir com algo novo** → [IDEIAS-EXTRAS.md](IDEIAS-EXTRAS.md)
- **Sou um agente (ou o orquestrador) construindo o projeto** → [AGENTES.md](AGENTES.md)

---

## ⚠️ Natureza destes documentos

- São **documentos vivos**: evoluem junto com o código, o [`README.md`](../README.md) e o
  [`IA.md`](../IA.md).
- São **exploratórios**: descrevem caminhos possíveis, não compromissos. Muitos itens
  são **ideias abertas à comunidade**, não tarefas internas.
- Seguem o padrão de qualidade do projeto: linguagem acessível, sem segredos nem valores
  privados hardcoded, e trabalho futuro enquadrado como convite à contribuição.
