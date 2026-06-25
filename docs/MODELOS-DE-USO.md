# 🎭 Modelos de uso

> **O que é**: as formas de usar o projeto e para quem cada uma serve. Vai do uso mais
> simples (importar a biblioteca) ao mais ambicioso (agentes autônomos via MCP). Ajuda a
> escolher o ponto de entrada certo e a enxergar como as camadas se empilham.

> Veja também: [PLANO.md](PLANO.md) (roadmap e fases) e
> [PORTABILIDADE.md](PORTABILIDADE.md) (adaptar para outros casos).

---

## 📋 Índice

- [🧩 As cinco camadas de uso](#-as-cinco-camadas-de-uso)
- [👥 Personas](#-personas)
- [🎬 Cenários práticos](#-cenários-práticos)
- [🪜 Trilha de adoção](#-trilha-de-adoção)

---

## 🧩 As cinco camadas de uso

O projeto é uma pilha: cada camada usa a de baixo e nenhuma obriga a de cima. Você pode
parar em qualquer degrau.

| # | Camada | Como se usa | Quando faz sentido |
|---|---|---|---|
| 1 | **Biblioteca** | `from notion_starter import NotionClient, TaskList` | Já existe um script/app seu e você só quer falar com o Notion de forma tipada |
| 2 | **Menu / CLI** | `python start_app.py` | Quer rodar exemplos, mapear o workspace ou configurar o token sem decorar comando |
| 3 | **Servidor + front web** | sobe o Django, abre o navegador | Quer ver e editar suas tarefas reais numa interface própria |
| 4 | **IA assistida** | a IA sugere, você confirma | Quer ajuda para priorizar, resumir, criar tarefas em linguagem natural |
| 5 | **Agentes via MCP** | o Felixo-AI-Core orquestra | Quer só ler e adicionar tarefas enquanto agentes executam e registram |

> As camadas 3–5 são o roadmap (ver [PLANO.md](PLANO.md)); as camadas 1–2 já existem.

---

## 👥 Personas

- **A pessoa dona do workspace** (uso central deste projeto): quer um "Notion do seu
  jeito" — lê, filtra, adiciona tarefas, e deixa a IA/agentes cuidarem do resto.
- **A desenvolvedora que integra**: pega só a **biblioteca** como base tipada para a
  própria integração com o Notion, sem querer o resto.
- **Quem usa como template**: clona, renomeia o pacote, troca o schema e adapta para um
  domínio diferente (ver [PORTABILIDADE.md](PORTABILIDADE.md)).
- **Quem contribui**: pega uma fase do roadmap ou uma ideia aberta e implementa de forma
  isolada.

---

## 🎬 Cenários práticos

### 1. "O que eu faço hoje?"
Lista as tarefas do dia (filtro por status/prazo) e, na camada de IA, pede um resumo
priorizado. Base já pronta: `TaskList.listar(status=...)`.

### 2. "Cria essa tarefa pra mim"
Em linguagem natural → a IA propõe a tarefa (nome, status, prazo) → você confirma →
`TaskList.criar(...)` escreve no Notion. O modo confirmar-antes-de-escrever é o padrão
inicial.

### 3. "Organiza esses arquivos no Notion"
Aponta uma pasta local; o servidor analisa os arquivos, extrai metadados/resumo e cria
páginas organizadas (Fase 3 do roadmap).

### 4. "Cada projeto do meu GitHub vira uma página + tarefa"
O conector lê os repositórios e gera, por projeto, uma página descritiva e um tópico no
todolist (Fase 4 do roadmap).

### 5. "Vários agentes trabalhando, eu só acompanho"
O estado-alvo: você lê e adiciona tarefas; agentes orquestrados pelo Felixo-AI-Core
executam (código, artigos, pesquisas…) e registram de volta no Notion (Fase 6).

---

## 🪜 Trilha de adoção

Uma ordem natural de crescer, sem pular degraus:

```text
1. Biblioteca / menu  →  já dá valor (ler e escrever no Notion de forma tipada)
2. Servidor + front   →  o momento aha: ver e editar tarefas reais no navegador
3. IA assistida       →  a IA sugere; você confirma cada escrita
4. Fontes de dados    →  arquivos locais e GitHub viram páginas/tarefas
5. Agentes via MCP    →  o cérebro (Felixo-AI-Core) assume a execução
```

Cada degrau é útil sozinho. A graça do projeto é que você colhe valor desde o primeiro,
sem precisar do topo da pilha.
