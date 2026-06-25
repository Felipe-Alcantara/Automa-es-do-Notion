# 💡 Ideias extras — brainstorm aberto

> **O que é**: um catálogo de ideias além do roadmap principal ([PLANO.md](PLANO.md)).
> São **propostas abertas à comunidade**, não compromissos. Algumas são pequenas e
> isoladas; outras são direções inteiras. Pegue qualquer uma que te animar.

> Veja também: as fases concretas estão no [PLANO.md](PLANO.md); os caminhos de evolução
> em [SAAS.md](SAAS.md), [ESCALA.md](ESCALA.md) e [OTIMIZACAO.md](OTIMIZACAO.md).

---

## 📋 Índice

- [🤖 Provedores de IA: OpenRouter e assinaturas](#-provedores-de-ia-openrouter-e-assinaturas)
- [🧩 Cobertura da API do Notion](#-cobertura-da-api-do-notion)
- [🗂️ Camada de domínio reutilizável](#️-camada-de-domínio-reutilizável)
- [🔗 Mais fontes de dados](#-mais-fontes-de-dados)
- [🛠️ Ergonomia e template](#️-ergonomia-e-template)
- [🧠 Recursos de IA aplicada](#-recursos-de-ia-aplicada)
- [📥 Como propor uma ideia](#-como-propor-uma-ideia)

---

## 🤖 Provedores de IA: OpenRouter e assinaturas

A camada de IA **não deve assumir um único provedor**. O OpenRouter (pague por uso) é o
ponto de partida, mas o projeto também quer suportar **ferramentas e assinaturas que a
pessoa já paga** — apontando para a conta dela em vez de consumir tokens cobrados à parte.

Provedores/modos previstos (provedor plugável por estratégia — ver [PLANO.md](PLANO.md),
Fase 5):

- **OpenRouter** — pague por uso, multi-modelo, catálogo ao vivo com preço por modelo.
- **Assinaturas / CLIs com conta própria** (alvos futuros):
  - **Codex** (OpenAI)
  - **Claude Code Pro** (Anthropic)
  - **Cursor**
  - **Gemini CLI** (Google)
  - **Copilot CLI** (GitHub)

> O projeto irmão [Openia](https://github.com/Felipe-Alcantara/Openia) já trata os dois
> mundos — uso por chave do OpenRouter e modo "assinatura" (rodar a ferramenta com o
> login da própria conta). Essa é a referência de implementação a reaproveitar.

**Ideias abertas aqui:**

- Um **seletor de provedor** que escolhe, por tarefa, entre pague-por-uso e assinatura.
- Roteamento por custo/objetivo: tarefa simples → modelo barato; tarefa complexa →
  o melhor disponível na assinatura ativa.
- Suportar **várias contas/chaves nomeadas** e trocar a ativa, como no Openia.

---

## 🧩 Cobertura da API do Notion

Ampliar o que a biblioteca entende do Notion:

- **Mais tipos de propriedade** — `relation`, `rollup`, `people`, `files`, `formula`
  (escrita e leitura).
- **Helpers de leitura** — extrair valores de páginas de volta (a Fase 0 do roadmap já
  começa por aqui).
- **Suporte a blocos** — ler e escrever o conteúdo de páginas, não só as propriedades de
  database. Abre caminho para a IA escrever artigos/anotações dentro das páginas.

---

## 🗂️ Camada de domínio reutilizável

Hoje a `TaskList` é específica de tarefas. Uma ideia forte é **generalizar o padrão**:
uma camada que mapeia *qualquer* database para um objeto de domínio, configurada por
quais colunas ler e como convertê-las. A tasklist vira um caso particular. Domínios que
caem no mesmo molde: leituras, hábitos, finanças, CRM leve, conteúdo, estudos.

---

## 🔗 Mais fontes de dados

Além do GitHub (Fase 4), outras fontes plugáveis que viram páginas/tarefas no Notion:

- **Planilhas / CSV** — já há um exemplo de importação por CSV; dá para virar uma fonte
  de primeira classe.
- **APIs externas** — calendários, e-mail, sistemas de issues.
- **Pastas locais** — a ingestão de arquivos (Fase 3) com mais formatos
  (documentos, PDFs, notas).

A chave é manter o **tipo de fonte como ponto de extensão**, para crescer sem reescrever.

---

## 🛠️ Ergonomia e template

Tornar o projeto mais agradável de adotar e adaptar:

- **Comando "renomear o pacote"** — automatizar a adaptação de quem usa como template.
- **Mais receitas no menu** — novas opções de "Iniciar/Rodar" por fonte de dados.
- **Sincronização bidirecional real** — hoje os fluxos tendem a ser de mão única.
- **Documentação de integração** — mais exemplos ponta a ponta.

---

## 🧠 Recursos de IA aplicada

Coisas que a camada de IA poderia fazer, alinhadas à visão de "agentes que executam e
registram no Notion":

- **Linguagem natural → tasklist** — "cria uma tarefa pra revisar o artigo X amanhã".
- **Resumir e priorizar** — um resumo diário do que importa, com sugestão de ordem.
- **Pesquisar e rascunhar** — pesquisar um assunto, resumir e escrever um rascunho
  (artigo, roteiro, estudo) direto numa página do Notion.
- **Acompanhar projetos** — manter a página de cada projeto atualizada (estado atual,
  próximos passos) enquanto a IA trabalha.
- **Sugerir ideias de projetos** — a partir do que já existe no workspace.

Em todos, o padrão começa como **copiloto que sugere e a pessoa confirma**, evoluindo
para autônomo com guarda-corpos.

---

## 📥 Como propor uma ideia

- Abra uma issue descrevendo o problema que a ideia resolve (não só a solução).
- Prefira recortes pequenos e isolados — uma fonte, um tipo de propriedade, um provedor.
- Mantenha os guarda-corpos do projeto: integração isolada, testes com HTTP mockado,
  segredos fora do repositório, documentação viva.

Contribuições são bem-vindas — desde corrigir um detalhe até puxar uma direção inteira.
