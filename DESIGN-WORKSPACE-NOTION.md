# Design padrão de organização de workspace Notion

> **Origem**: mapeado do workspace real **Central pessoal** (Vitis Souls, `aa12f7941f658218ae568196d51942d0`), montado por agente em 10/07/2026 — 1 raiz, ~21 databases, ~1.100 páginas, seis projetos organizados sem retrabalho.
>
> **Regra**: se o usuário **não indicar** um jeito específico de organização, **use este modelo**. Ele é o padrão consolidado do ecossistema (o guia genérico correspondente vive no Felixo System Design: `guias/integracao/GUIA-NOTION-COMO-BASE-DE-DADOS.md`).

## 1. Estrutura macro: uma página-central, tópicos por projeto

- **Uma página raiz** ("Central") concentra tudo; nenhum item órfão no workspace.
- Cada projeto/assunto é um **tópico** na página raiz: `## Heading` + **divisória** (`---`) + databases/páginas **full-page linkadas** logo abaixo. **Sem parágrafos de introdução** entre o heading e os itens.
- Projeto com muitas bases ganha uma **página-pasta** (ex.: "Descontos VIP") com **subtópicos** internos no mesmo formato (ex.: "Bases do projeto" e "Rede de Amplificação Cruzada").
- Hierarquia de pastas (ex.: vindas do Drive) vira tópicos/subtópicos; **só os arquivos/registros finais viram linhas de database** (ex.: Relatórios ECOVS → subtópico por membro → uma database por membro).

## 2. Databases: uma linha = uma entidade, schema tipado

- **Granularidade explícita**: "1 linha = 1 conta" e "1 linha = 1 conta × plataforma" são databases **diferentes e relacionadas** — nunca fundir granularidades.
- **Propriedades tipadas**, nunca tudo em texto: `select`/`multi_select` (com cores) para estados e categorias, `email`, `url`, `date`, `number`, `checkbox`, `people`, `files`, `relation`.
- **ID nativo com prefixo** (`unique_id`) por database: `DVIP` no Cadastro, `FEL` nos Relatórios do Felipe, `CC` nas lojas. Nunca número sequencial colado no título. O prefixo é **único por workspace**.
- **Toda database tem ícone (emoji) e descrição** dizendo o que é, de onde veio o dado e a granularidade (ex.: "Registro das 240 contas do projeto… Importada da planilha 09/04…").
- **Propriedade "Observações"** (`rich_text`) em toda base importada: informação ambígua ou inválida da fonte **nunca é descartada** — vai para lá.
- **Arquivo original anexado**: quando a linha nasce de um documento (docx etc.), o conteúdo vira blocos na página da linha **e** o arquivo original fica na propriedade `Arquivos e mídia` (a linha tem o dado, a leitura e a fonte de verdade).

## 3. Relações e consolidação

- Ligar bases por **`relation`** usando uma chave real (ex.: e-mail), em vez de duplicar dados.
- Projeto espalhado se **consolida por re-parent** (mover databases para dentro do folder do projeto), nunca recriando.
- Redundância se resolve **arquivando** (reversível), nunca apagando.

## 4. Página = propriedades + corpo

- As propriedades (colunas) carregam o dado estruturado; o corpo (blocos) carrega a leitura. **Leia e preencha primeiro as propriedades, depois o corpo.**
- Ao receber um link/ID: entender do que se trata antes de escrever; database ⇒ trabalhar **nas linhas** (ver regras no `AGENTS.md`).

## 5. Como aplicar (sempre via ferramentas, nunca à mão)

| Passo | Ferramenta |
| --- | --- |
| Criar database tipada com ícone/descrição/unique_id | `notion-tasks criar-database <pagina> <titulo> --prop "Col=tipo" --icone 📋 --descricao "..." --prefixo-id XyZ` |
| Importar planilha com tipos BR e Observações | `notion-tasks importar-planilha <db> <arquivo> --tipo "Col=numero/data/..."` |
| Anexar o arquivo original na linha | `notion-tasks anexar-arquivo <page_id> <arquivo>` |
| Montar tópicos (heading + divisória) | `notion-tasks escrever <pagina> $'## Tópico\n\n---'` |
| Consolidar/reorganizar | `notion-tasks mover-pagina` / `mover-database` |
| Criar uma subpágina simples (README, Estado atual, etc.) | `notion-tasks criar-subpagina <pagina_pai_id> <titulo>` |
| Investigar a estrutura de um projeto de referência antes de replicar (sem editar nada) | `notion-tasks inspecionar-estrutura <pagina_id> --profundidade 3` |
| Copiar a forma (subpáginas + schema de databases) de um projeto existente para outro | `notion-tasks clonar-estrutura <pagina_referencia_id> <pagina_destino_id>` |
| Aplicar o padrão de projeto (Acompanhamento + Planejamento e documentação) do zero | `notion-tasks montar-estrutura-projeto <pagina_id>` |

### Como montar o padrão de projeto (Acompanhamento + Planejamento e documentação)

Toda página de projeto segue a mesma moldura fixa (ver o mapeamento original na
seção 1): `## Acompanhamento` + divisória, 4 subpáginas (`Estado atual`,
`Trabalho em andamento`, `Problemas encontrados`, `Decisões e registros`),
`## Planejamento e documentação` + divisória, 2 databases (`Próximos passos`,
`Documentações`). Duas formas de aplicar:

- **Do zero**, numa página nova: `notion-tasks montar-estrutura-projeto <pagina_id>`
  cria a moldura com subpáginas vazias e databases com schema mínimo
  (título + Observações) — depois preencha o conteúdo real do projeto.
- **Copiando de uma referência**, quando o padrão da página de origem tem
  variações que valem a pena preservar (ex.: databases extras, propriedades
  próprias): `notion-tasks inspecionar-estrutura <referência>` primeiro, para
  entender a forma exata, e `notion-tasks clonar-estrutura <referência> <destino>`
  para replicá-la (títulos de subpágina + schema de databases, sem linhas nem
  conteúdo específico do projeto de origem).

Nos dois casos, o conteúdo de cada subpágina (Estado atual, Decisões e
registros, …) continua sendo escrito à mão com `notion-tasks escrever`, a
partir de dados reais do projeto (README, `IA.md`, histórico de commits) —
essas ferramentas só cuidam da moldura estrutural, nunca do texto.

## Checklist ao montar/organizar um workspace

- [ ] Tudo pendurado numa página-central; tópico = heading + divisória + links full-page, sem texto de introdução.
- [ ] Cada database com ícone, descrição, tipos corretos, `unique_id` com prefixo próprio e "Observações".
- [ ] Granularidades separadas e ligadas por `relation` (chave real).
- [ ] Arquivo original anexado quando a linha nasce de um documento.
- [ ] Reorganização por re-parent; remoção por arquivamento.
- [ ] Tudo executado por scripts/CLI (regra do hub), com import idempotente.
- [ ] Página de projeto segue a moldura fixa: README + `## Acompanhamento` (4 subpáginas) + `## Planejamento e documentação` (2 databases) — via `montar-estrutura-projeto` ou `clonar-estrutura`.
