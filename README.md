# 🧠 Automações do Notion

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Notion API](https://img.shields.io/badge/Notion-API-000000?style=for-the-badge&logo=notion&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Hub do ecossistema de automações do Notion — arquitetura, documentação e os módulos que nasceram aqui.**

</div>

---

Este repositório começou como um monorepo e foi separado em módulos independentes. Hoje ele é o **ponto de entrada do ecossistema**: reúne a documentação de arquitetura e aponta para os repositórios de cada módulo.

## 📦 Módulos

| Repositório | O que é | Depende de |
| --- | --- | --- |
| [notion-starter](https://github.com/Felipe-Alcantara/notion-starter) | Biblioteca Python para a API oficial do Notion: cliente resiliente, schema, tarefas, conteúdo, inventário e exemplos | — |
| [notion-tasks-cli](https://github.com/Felipe-Alcantara/notion-tasks-cli) | CLI pensado para IAs — um **"MCP via CLI"** que permite a qualquer modelo criar, editar e manipular qualquer workspace do Notion pelo terminal | notion-starter |
| [notion-workspace-app](https://github.com/Felipe-Alcantara/notion-workspace-app) | Aplicação local completa: API Django, SPA React (kanban, filtros, exploração), servidor MCP, sincronização GitHub↔Notion e launcher TUI | notion-starter |

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────┐
│                 notion-starter                  │
│   biblioteca base (cliente, schema, tarefas)    │
└────────────┬───────────────────────┬────────────┘
             │                       │
   ┌─────────▼─────────┐   ┌─────────▼──────────┐
   │  notion-tasks-cli │   │ notion-workspace-  │
   │  "MCP via CLI"    │   │ app (Django+React  │
   │  para IAs         │   │  + MCP + TUI)      │
   └───────────────────┘   └────────────────────┘
```

Os dois módulos de cima compartilham hoje uma camada de serviços (`core`, `integrations`, `services`); a consolidação dessa camada dentro do `notion-starter` está no roadmap.

## 🌌 Ecossistema Felixo

Este projeto faz parte de um ecossistema maior de desenvolvimento com multiagentes, em ordem cronológica:

1. [Felixo-System-Design](https://github.com/Felipe-Alcantara/Felixo-System-Design) — padrão de qualidade e boas práticas de vibe coding
2. [Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core) — orquestrador Electron para spawnar, monitorar e desenvolver com multiagentes
3. [Openia](https://github.com/Felipe-Alcantara/Openia) — qualquer modelo de IA na interface do Claude Code
4. **Automações do Notion** — este hub e seus três módulos
5. [OpenRouter-Monitorator](https://github.com/Felipe-Alcantara/OpenRouter-Monitorator) — métricas de uso e custo de modelos via OpenRouter

## 🤖 Para IAs (e para quem desenvolve com elas)

Este hub é o **ponto de entrada para agentes**. Aponte sua IA para este repositório e ela encontra em [`AGENTS.md`](AGENTS.md) o roteamento completo:

- **Usar o Notion** → instala o `notion-tasks` (CLI feito para IAs) e opera o workspace pelo terminal.
- **Desenvolver as ferramentas** → `python bootstrap.py` clona os módulos em `modules/`, e o agente edita, testa e commita no repositório correto sozinho.

Ou seja: você pode usar cada módulo separadamente, ou promptar a partir daqui e deixar o agente achar a função (ou o código) certo.

## 📚 Documentação

A pasta [`docs/`](docs/) guarda o material de arquitetura e planejamento que guiou o desenvolvimento (contratos, camada de IA, MCP, modularização, escala, SaaS…). O arquivo [`IA.md`](IA.md) é o guia de operação para agentes de IA trabalhando no ecossistema.

## 📄 Licença

MIT
