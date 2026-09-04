# 📚 Documentação — Automações do Notion

> **O que é esta pasta**: a documentação viva de operação, arquitetura, contratos e
> evolução do projeto. A referência rápida de instalação fica no
> [`README.md`](../README.md); a implementação vive nos três módulos publicados.

---

## 🗂️ Índice da documentação

| Documento | Para quê serve |
|---|---|
| [📦 DISTRIBUICAO.md](DISTRIBUICAO.md) | Instalação pública, pacotes `0.3.0`, smoke, Trusted Publishing e limites da distribuição. |
| [✅ QUALIDADE.md](QUALIDADE.md) | Gate executável do hub e dos módulos, checklist de documentação e critério de pronto. |
| [🧱 CONTRATOS.md](CONTRATOS.md) | Contrato dos objetos, rotas REST, erros e fronteiras entre módulos. |
| [🤖 AGENTES.md](AGENTES.md) | Playbook histórico/operacional de orquestração multi-agente. |
| [🗺️ PLANO.md](PLANO.md) | Visão final, estado entregue e roadmap de contribuição. |
| [🎭 MODELOS-DE-USO.md](MODELOS-DE-USO.md) | Quem usa, em quais cenários, e os modos de operação (lib, CLI, servidor, IA, MCP). |
| [🔗 MCP.md](MCP.md) | Ferramentas MCP, transportes, confirmação e integração com o Felixo-AI-Core. |
| [🐙 GITHUB-DATABASE.md](GITHUB-DATABASE.md) | Sincronização idempotente de repositórios do GitHub para o Notion. |
| [📊 PADRAO-RELATORIOS.md](PADRAO-RELATORIOS.md) | Formato canônico dos relatórios diários e regras de upsert. |
| [🧩 MODULARIZACAO.md](MODULARIZACAO.md) | Arquitetura multi-repositório implementada e fronteiras de manutenção. |
| [🔌 PORTABILIDADE.md](PORTABILIDADE.md) | Como adaptar para outro domínio, outro provedor ou outra linguagem. Usar como template. |
| [💼 SAAS.md](SAAS.md) | O que mudaria para virar um produto multiusuário (auth, multi-tenant, cobrança, segurança). |
| [🏗️ INFRA.md](INFRA.md) | Como o servidor roda local e é hospedado: estrutura de pastas, config por ambiente, SQLite operacional, deploy. |
| [🧪 TESTE-WEB-2026-06-30.md](TESTE-WEB-2026-06-30.md) | Registro da validação da frente web focada na database `Tarefas — HOME (pessoal)`, com achados, correções aplicadas e prioridades. |
| [🔄 INTEGRACOES.md](INTEGRACOES.md) | GitHub e arquivos locais: configuração, schemas, idempotência, segurança e exemplos de sincronização. |
| [📈 ESCALA.md](ESCALA.md) | Como crescer sem quebrar: fila de jobs, workers, cache, rate limit, observabilidade. |
| [⚡ OTIMIZACAO.md](OTIMIZACAO.md) | Como reduzir latência e custo (chamadas ao Notion e ao OpenRouter, cache, idempotência). |
| [💡 IDEIAS-EXTRAS.md](IDEIAS-EXTRAS.md) | Brainstorm aberto: funcionalidades e integrações além do roadmap. |
| [🤖 IA-CAMADA.md](IA-CAMADA.md) | Camada de IA plugável: ProvedorIA, OpenRouter, catálogo de modelos, caso de uso copiloto (NL → tasklist). |
| [🩺 DIAGNOSTICO_PROBLEMA_CLI.md](DIAGNOSTICO_PROBLEMA_CLI.md) | Relato histórico do diagnóstico original da CLI; não substitui o guia atual. |
| [🛡️ PREVENCAO_STATUS_INVALIDO.md](PREVENCAO_STATUS_INVALIDO.md) | Decisão e testes da prevenção de status inválido. |
| [🧰 Guia do multiagentes/](Guia%20do%20multiagentes/) | Artefatos históricos de coordenação do canvas multiagente. |
| [🗄️ ia-archive/](ia-archive/) | Registros antigos do [`IA.md`](../IA.md) movidos na íntegra (compactação sem perda): linha do tempo completa = `IA.md` + archives. |

---

## 🧭 Como ler, por objetivo

- **Quero instalar e usar** → [DISTRIBUICAO.md](DISTRIBUICAO.md) → [`README.md`](../README.md)
- **Quero entender a visão** → [PLANO.md](PLANO.md) → [MODELOS-DE-USO.md](MODELOS-DE-USO.md)
- **Vou implementar uma frente do Ciclo 2 (front React, CLI, API v2)** →
  [CONTRATOS.md](CONTRATOS.md) (o contrato) → [AGENTES.md](AGENTES.md) → [PLANO.md](PLANO.md) (*Ciclo 2*)
- **Vou validar uma mudança antes de entregar** → [QUALIDADE.md](QUALIDADE.md)
- **Vou mexer em um módulo** → [`AGENTS.md`](../AGENTS.md) → [MODULARIZACAO.md](MODULARIZACAO.md)
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
- São **exploratórios** quando marcados como roadmap: descrevem caminhos possíveis, não compromissos. Muitos itens
  são **ideias abertas à comunidade**, não tarefas internas.
- Seguem o padrão de qualidade do projeto: linguagem acessível, sem segredos nem valores
  privados hardcoded, e trabalho futuro enquadrado como convite à contribuição.
- A fonte do estado corrente é o `README.md`, `docs/DISTRIBUICAO.md`,
  `docs/QUALIDADE.md` e o resumo vivo do `IA.md`. Relatos datados e o archive preservam
  o contexto histórico e não devem ser lidos como instruções de instalação atuais.
