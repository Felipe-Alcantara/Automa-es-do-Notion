# AGENTS.md — Roteamento para agentes

Este é o **mapa de roteamento** de pedidos para módulos. Leia isto **toda vez** que receber um pedido.

## Pré-requisito: bootstrap.py

Antes de qualquer coisa, verifique se `modules/` existe com os três repositórios:

```bash
python bootstrap.py
```

Se `modules/` não existe, rode isso. Se existe, `git pull` os módulos. Sem este passo, você não acessa o código dos módulos.

O `bootstrap.py` **reusa clones existentes**: se um módulo já estiver clonado na pasta acima (`../<nome>`), ele cria um link (junction no Windows, symlink no POSIX) em `modules/<nome>` apontando para lá, em vez de duplicar. Ou seja, `modules/<nome>` é sempre o caminho de dev — editar/testar/commitar ali escreve no clone real. Só clona do GitHub o que não existe em lugar nenhum.

---

## Dois modos de operação

### MODO USO — operar o Notion via CLI

O pedido é: *criar tarefa, ler página, mapear workspace, buscar dados, sincronizar…*

**Ação:** instale uma vez a distribuição pública (`pipx install
"notion-automacoes[app]"`), depois execute comandos. O executável histórico
`notion-tasks` continua disponível como alias.

```bash
notion-tasks listar
notion-tasks criar --titulo "..."
notion-tasks conteudo <id>
```

Não precise de módulos locais. O CLI já tem tudo pronto. Ver `--help` para o guia completo (escrito para IAs).

**Regras de operação no Notion (valem para CLI e MCP):**

> Em `--json`, todo erro vem no mesmo envelope: `{"ok": false, "erro": {"codigo", "mensagem", "proximo_passo", "http_status", ...}}`. Leia `codigo` e siga o `proximo_passo`.

> **Se você só for ler uma linha deste arquivo, leia esta.** Recebeu um link do
> Notion? Rode `notion-tasks conteudo <id>` **antes de escrever qualquer coisa**.
> Se a resposta trouxer `databases_dentro`, **o conteúdo daquela página são as
> LINHAS da tabela, não o corpo da página** — vá para `linhas <database_id>`.

1. **Regra do link**: ao receber um link ou ID do Notion, **leia e entenda do que se trata antes de qualquer escrita** (`notion-tasks conteudo <id>`; se for database, `notion-tasks linhas <id>`). Se o alvo é um database, o trabalho é **nas linhas**: localize a linha certa e atualize-a — nunca ignore o database e escreva blocos soltos abaixo dele.

   *A CLI agora faz isso valer sozinha*: `escrever` numa página que contém database **falha** com a lista das databases e o caminho pronto. Só passa com `--mesmo-com-database`, quando o bloco solto é mesmo a intenção.

2. **Regra do schema**: antes de escrever num database que você não conhece, rode **`notion-tasks schema <database_id>`**. Ele responde de uma vez: nome exato de cada coluna, tipo, **valores aceitos** por select/status, o que é calculado pelo Notion (e recusa PATCH) e como cada relação está configurada. Escrever antes disso é adivinhar — e o erro só aparece depois de gravado.

3. **Regra de leitura**: propriedades e corpo são partes da **mesma página**. Comece a leitura pelas propriedades (colunas) e só depois pelo corpo — há páginas com mais informação nas propriedades do que no corpo. `conteudo <id>` já devolve as duas partes, propriedades primeiro.

4. **Regra de escrita**: numa linha de database, edite primeiro as propriedades (`editar-linha`) e depois o corpo (`escrever`). Para uma linha **nova**, `criar "Título" --set "Coluna=valor" --conteudo "# Markdown"` faz as três coisas numa chamada só, na ordem certa.

5. **Regra da relação**: para ligar duas linhas use **`relacionar <a> <b> --coluna "Nome"`**, nunca `editar-linha` na mão. O tipo declarado (`single_property`/`dual_property`) **não permite prever** se o Notion espelha a outra ponta — medido no workspace real em 2026-08-17, uma relação auto-referente reportada como `single_property` espelhou sozinha. `relacionar` confere a outra ponta e grava só o que faltar, então funciona nos dois casos e é idempotente.

6. **Regra da reescrita**: `escrever --substituir` **escreve o conteúdo novo antes de apagar** o antigo (se a escrita falhar, a página não fica vazia) e **preserva** o que não se recria a partir de Markdown — imagem, arquivo, embed, subpágina, `child_database`, toggle, callout, equação, `link_to_page`, sumário, breadcrumb e qualquer bloco que contenha um desses. A saída lista os IDs apagados e preservados; `restaurar-bloco <id>...` desfaz. `--apagar-tudo` remove essas exceções também: use com cuidado, porque URL de arquivo do Notion expira e apagar um `child_database` leva o database inteiro.

7. **Regra de organização**: se o usuário não indicar um jeito específico de organizar o workspace, use o modelo padrão registrado em [`DESIGN-WORKSPACE-NOTION.md`](DESIGN-WORKSPACE-NOTION.md) (tópicos = heading + divisória + links full-page, databases tipadas com ícone/descrição/unique_id, relações em vez de fusão, arquivo original anexado, re-parent/arquivamento).

**Receita completa — "coloque isto no meu database":**

```bash
notion-tasks conteudo <id_do_link>        # 1. o que é isto? tem database dentro?
notion-tasks schema <database_id>         # 2. que colunas existem e o que aceitam
notion-tasks linhas <database_id>         # 3. já existe linha para este assunto?
notion-tasks criar "Título" \             # 4. cria completa numa chamada
  --status "Entrada" --set "Prioridade=Alta" --conteudo "## Contexto..."
notion-tasks relacionar <nova> <outra> --coluna "Subtarefas relacionadas"
```

### MODO DESENVOLVIMENTO — modificar código das ferramentas

O pedido é: *corrigir bug, adicionar comando, mudar frontend, melhorar resilência…*

**Pré-requisito:** `python bootstrap.py` (primeiro). Sem isso, `modules/` não existe.

**Fluxo:**
1. Use a tabela de roteamento abaixo para encontrar o módulo (`notion-starter`, `notion-tasks-cli`, `notion-workspace-app`).
2. Edite no arquivo correto, em `modules/<nome>/`.
3. Teste dentro do módulo: `cd modules/<nome> && python -m pytest`.
4. Commit e push **dentro do módulo**, não no hub.

> **Antes de confiar num teste do `notion-starter`, rode `python check-dev.py`.**
> Ele diz de onde o `notion_starter` está sendo importado. Se não vier de
> `modules/notion-starter`, sua edição **não está sendo executada** — nem pela CLI
> do PATH, nem pela suíte de quem depende dela — e nada avisa: o comando continua
> funcionando, só que com uma cópia antiga instalada. No desenvolvimento, instale
> a CLI **primeiro** e o starter **por último**, ambos `--editable`, ou use
> `python start_app.py → Instalar/Setup`, que já faz nessa ordem. A distribuição
> publicada usa a dependência versionada do PyPI e não depende de checkout vizinho.
> Medido em 24/08/2026; o contrato de distribuição está em
> [`docs/DISTRIBUICAO.md`](docs/DISTRIBUICAO.md).

Nunca desenvolva funcionalidade neste hub; este é documentação e roteamento.

---

## Catálogo de módulos

| Repositório | Papel | Local após bootstrap |
| --- | --- | --- |
| [notion-starter](https://github.com/Felipe-Alcantara/notion-starter) | Biblioteca Python base + camada compartilhada: `NotionClient`, schema, tarefas, conteúdo, inventário, adaptadores e `notion_starter.services` | `modules/notion-starter/` |
| [notion-tasks-cli](https://github.com/Felipe-Alcantara/notion-tasks-cli) | CLI para IAs ("MCP via CLI"): borda fina; `integrations/` e `services/` comuns são shims para `notion-starter` | `modules/notion-tasks-cli/` |
| [notion-workspace-app](https://github.com/Felipe-Alcantara/notion-workspace-app) | App completo: API Django, SPA React, servidor MCP, launcher `start_app.py` | `modules/notion-workspace-app/` |

## Roteamento — MODO USO

Para uso global, instale a distribuição pública: `pipx install
"notion-automacoes[app]"` (`python -m pip install "notion-automacoes[app]"` também
é válido em um ambiente virtual).
Para desenvolvimento pelo checkout, o fluxo continua sendo `python bootstrap.py`
seguido da instalação editável dos módulos.
Requer autenticação: um **perfil ativo** salvo na CLI **ou** `NOTION_TOKEN` (e opcionalmente
`NOTION_DATABASE_ID`) no ambiente/`.env` — veja a precedência abaixo.
`notion-tasks --help` traz o guia completo, escrito para ser lido por modelos.

**Autenticação — ordem de precedência (da maior para a menor):**

1. `--perfil <alias>` na linha de comando — vale só naquela execução e vence tudo;
2. **perfil ativo** salvo na CLI (`notion-tasks perfis usar <alias>`) — vence **mesmo que
   `NOTION_TOKEN` esteja exportado**, silenciosamente;
3. `NOTION_TOKEN` do ambiente ou `.env` — só é usado quando **nenhum** perfil está ativo.

A CLI gerencia os perfis locais de workspaces/keys com
`notion-tasks perfis listar/adicionar/usar/mostrar/remover`.

> **Troubleshooting — "Recurso não encontrado" com um link/ID válido:** antes de concluir que a
> página não foi compartilhada com a integração, siga esta ordem:
>
> 1. `notion-tasks perfis listar` — confira **qual perfil está ativo** e a **qual workspace** ele
>    aponta (é ele que responde, não o `NOTION_TOKEN` exportado);
> 2. se for o workspace errado, use `--perfil <alias>` (pontual) ou
>    `notion-tasks perfis usar <alias>` (permanente);
> 3. só então investigue compartilhamento da página com a integração.
>
> O sintoma clássico de perfil errado é trocar o token no ambiente e a busca continuar
> devolvendo exatamente as mesmas páginas — sinal de que a variável nem está sendo lida.

| Você quer… | Comando |
| --- | --- |
| Listar/criar/editar/mover/concluir tarefas | `notion-tasks listar / criar / editar / mover / concluir`. `criar` aceita `--set "Coluna=valor"` e `--conteudo "# Markdown"` para nascer completa numa chamada só (evita o vaivém criar → editar-linha → escrever); `--database <id>` grava em **qualquer** database só nesta chamada (vale com `--arquivo` e `--dry-run`) |
| Descobrir status, durações e áreas válidas | `notion-tasks opcoes` (sempre antes de criar/mover) |
| Mapear o workspace inteiro | `notion-tasks mapear` |
| Pesquisar páginas e databases | `notion-tasks buscar <termo>` |
| Listar databases / linhas de um database | `notion-tasks databases` / `notion-tasks linhas <id>` |
| Ler uma página como Markdown | `notion-tasks conteudo <id>` — avisa em `databases_dentro` quando a página **contém** database (aí o trabalho é nas linhas dela) |
| **Descobrir as colunas de um database antes de escrever** (nome exato, tipo, valores aceitos, o que é calculado, como cada relação está configurada) | `notion-tasks schema <database_id>` (`--editaveis` esconde o que o Notion calcula). **Faça isto antes de qualquer escrita em database desconhecido** |
| Ligar duas linhas por uma coluna de relação, garantindo os dois sentidos | `notion-tasks relacionar <page_a> <page_b> --coluna "Nome"` (`--desfazer` remove). Confere a outra ponta e grava só o que faltar — idempotente. O tipo `single_property`/`dual_property` **não** permite prever se o Notion espelha sozinho |
| Editar propriedades (colunas) de uma linha de database | `notion-tasks editar-linha <id> --set "Nome=valor"` (substitui) / `--append "Nome=texto"` (acrescenta preservando). **Faça isto antes de escrever o conteúdo.** |
| Escrever/editar/apagar blocos | `notion-tasks escrever / editar-bloco / apagar-bloco` (apagar exige `--sim`, confere o alvo e aceita vários IDs; subpágina/database exigem `--forcar-tipos-arriscados`; o Notion arquiva, e `restaurar-bloco <id>...` desfaz). `escrever --apos <bloco> / --inicio` insere no meio da página e devolve `blocos_criados`. `editar-bloco --trocar "trecho" --por "novo"` troca só um trecho **preservando** menções, cores e links; `editar-bloco --arquivo lote.json` edita vários blocos numa chamada. `escrever` **recusa** página que contém database — libere com `--mesmo-com-database`. Markdown também entra por stdin (`-`) ou `--arquivo-md` |
| Ler blocos com ID e metadados | `notion-tasks blocos <page_id> --metadados` (criado/editado em e por quem) · `--completo` (Markdown inteiro de cada bloco) · `--recursivo` · `--contendo "trecho"`; `notion-tasks ler-bloco <id>` lê um bloco só. IDs e links do Notion são aceitos com ou sem hífens em qualquer argumento |
| Clonar páginas/estruturas | `notion-tasks clonar <id>` |
| Criar database com schema tipado | `notion-tasks criar-database <pagina_id> <titulo> --prop "Coluna=tipo"` (tipos em português; `--inline`, `--icone`, `--descricao`, `--prefixo-id` para unique_id — prefixo único por workspace) |
| Adicionar coluna a um database já existente (nenhum outro comando faz isso — `criar-database` só define schema na criação) | `notion-tasks garantir-coluna <database_id> <nome_coluna> <tipo>` — idempotente, não mexe em nada se a coluna já existe. Para ligar dois databases: `<tipo>` = `relacao` + `--relacionar-com <database_alvo_id>` (relação bidirecional; o Notion cria a coluna espelho no alvo) |
| Renomear um database (o clássico "Untitled" que sobra de template duplicado) | `notion-tasks renomear-database <database_id> "<novo título>"` — só troca o título, não mexe em schema nem linhas |
| Criar uma subpágina simples (não é linha de database) | `notion-tasks criar-subpagina <pagina_pai_id> <titulo> --conteudo "Markdown opcional"` |
| Investigar a estrutura (subpáginas/databases) de uma página de referência, sem editar nada | `notion-tasks inspecionar-estrutura <pagina_id> --profundidade 3` |
| Copiar a forma de um projeto (títulos de subpágina + schema de databases) para outra página | `notion-tasks clonar-estrutura <pagina_referencia_id> <pagina_destino_id>` |
| Aplicar do zero o padrão de projeto do workspace (`## Acompanhamento` com 4 subpáginas + `## Planejamento e documentação` com 2 databases) | `notion-tasks montar-estrutura-projeto <pagina_id>` — ver [`DESIGN-WORKSPACE-NOTION.md`](DESIGN-WORKSPACE-NOTION.md) |
| Reordenar um bloco dentro da mesma página (a API do Notion não move blocos: recria e só depois apaga o original, com backup em JSON) | `notion-tasks reordenar-bloco <pagina_id> <bloco_id> --apos <outro_id>` ou `--inicio`. Recusa `child_page`/`child_database` e blocos com filhos (o ID mudaria ou os filhos se perderiam). Backup em `~/.local/state/notion-automacoes/backups` (nunca no diretório atual); `--dir-backup` troca a pasta. Para **inserir** conteúdo no meio, prefira `escrever --apos` |
| Importar planilha (.xlsx/.csv) para um database | `notion-tasks importar-planilha <database_id> <arquivo> --chave "Coluna"` (upsert idempotente pela coluna-chave; sem `--chave`, a posição da linha é a chave e reordenar a planilha sobrescreveria outros registros). `--dry-run` mostra o plano e os conflitos; `--tipo "Coluna=numero/data/..."` converte formato BR, inválidos vão para Observações) |
| Anexar arquivo local (até 20 MB) numa linha | `notion-tasks anexar-arquivo <page_id> <arquivo>` (preserva anexos existentes; `--substituir` troca) |
| Mover (re-parentear) página ou database | `notion-tasks mover-pagina <id> <novo_pai_id> [--tipo-pai page_id|database_id|data_source_id] [--dry-run] [--aceitar-perdas]` — usa `POST /pages/{id}/move` e **relê o pai** (o `PATCH` com `parent` antigo respondia 200 e o Notion ignorava). Linha movida para outro database: o Notion **cria no destino** as colunas que faltam lá e **descarta** valores com opção inexistente e relações — a saída lista `colunas_acrescentadas_no_destino` e `valores_perdidos`, e perda exige `--aceitar-perdas`. `mover-database <id> <novo_pai_id>` move o database inteiro |
| Copiar o corpo de uma página para outra **bloco a bloco** (tabela, checklist, colunas, callout e menções preservados) | `notion-tasks copiar-corpo <origem> <destino> [--so-se-vazio] [--dry-run] [--conferir]` — lista branca de tipos; subpágina, database e arquivo hospedado no Notion vão para `ignorados` com o motivo |
| Modelos nativos (templates) de um database | `notion-tasks modelos listar <database_id>` / `modelos preencher <database_id> --manifesto modelos.json [--dry-run]` — preenche os modelos vazios (`New page`) com nome, colunas e corpo, idempotente. A API **não cria** modelo nem define o padrão: crie os modelos em branco pela interface |
| Remover uma coluna do schema (ex.: a que o Notion criou ao mover uma linha) | `notion-tasks remover-coluna <database_id> <coluna> --sim` — destrutivo (os valores somem de todas as linhas); recusa a coluna de título |
| **Levantar o acervo inteiro** (datas, caminho, texto completo) e procurar no texto, não só no título | `notion-tasks inventario --saida inv.json` → `baixar-corpos inv.json --destino corpos/ [--ignorar-caminho "A / B"] [--priorizar regex] [--limite N]` (retomável: o que já baixou é pulado) → `buscar-conteudo corpos/ "regex"` (sem acentos, trechos do original) |
| **Reconstruir os relatórios diários a partir do git**, de vários repositórios de uma vez | `notion-tasks relatorios-do-git --database <id> --descobrir <pasta>` — agrupa por dia, com **hora e duração por projeto**. `--descobrir` varre a pasta e inclui todo repositório git encontrado (é o que acha o dia de trabalho que ficou sem registro); `--repo "Nome=caminho"` dá nome de produto e vence a varredura. Idempotente pela data: dia existente é **complementado**, nunca sobrescrito. Use `--dry-run` antes |
| Exportar relatórios diários para DOCX | `notion-tasks exportar-docx --database <id> --de YYYY-MM-DD --ate YYYY-MM-DD --saida <dir>` (também aceita `NOTION_REPORTS_DATABASE_ID`; gera um `.docx` por relatório/dia). A saída reproduz o modelo visual dos relatórios, mas é gerada programaticamente — o acabamento fino pode exigir ajuste manual no Word. |
| Importar/atualizar repositórios do GitHub numa database (vários perfis de uma vez, com dedup) | `notion-tasks atualizar-github --contas <login/@handle/URL,...>` (upsert por URL, propriedades ricas e README em subpágina). Flags: `--sem-readme` (só propriedades), `--sem-arquivados` (ignora arquivados), `--apenas-mudancas` (pula sem alteração). Guia: [`docs/GITHUB-DATABASE.md`](docs/GITHUB-DATABASE.md) |
| Trocar de workspace / gerenciar keys salvas | `notion-tasks perfis listar / adicionar / usar / mostrar / remover`; numa única execução, `--perfil <alias>` |
| Interface gráfica ou servidor MCP | use o `notion-workspace-app` (`python start_app.py`) |
| **CLI distribuída sem clone** | instale `notion-automacoes[app]`; use `notion-automacoes tasks`, `auth`, `doctor`, `app start` e `mcp start` (versão pública atual: `0.5.0`) |

## Roteamento — MODO DESENVOLVIMENTO

Primeiro `python bootstrap.py` (clona ou atualiza os módulos em `modules/`). Depois localize o alvo:

| O pedido mexe em… | Repositório | Onde |
| --- | --- | --- |
| Cliente HTTP, retries, rate limit, erros da API | notion-starter | `src/notion_starter/client.py` |
| Schema de databases: comparação (`comparar_schema`) e **leitura legível** (`descrever_database`, `DescricaoDatabase`, `Coluna`, `Relacao`) | notion-starter | `src/notion_starter/schema.py` |
| Ligar linhas por relação nos dois sentidos (confere a outra ponta antes de gravar) | notion-starter | `src/notion_starter/services/relacoes.py` |
| Guarda contra escrever bloco solto em página que contém database; preservação de blocos não recriáveis na reescrita | notion-starter | `src/notion_starter/services/conteudo.py` (`databases_da_pagina`, `TIPOS_NAO_RECRIAVEIS`, `EscritaAbaixoDeDatabaseError`) |
| Modelo de tarefas (`Tarefa`, `TaskList`) | notion-starter | `src/notion_starter/tasks.py` |
| Conversão Markdown ↔ blocos; builders de propriedade (fatia de texto >2000) | notion-starter | `src/notion_starter/content.py`, `properties.py`, `readers.py` |
| Ler/editar propriedades de uma página (`obter_pagina`/`atualizar_pagina`) | notion-starter | `src/notion_starter/client.py` |
| Inventário/varredura do workspace | notion-starter | `src/notion_starter/inventory.py` |
| Saneamento de texto/JSON (surrogates), `fatiar_utf16` | notion-starter | `src/notion_starter/utils.py` |
| Subcomandos do CLI, saída JSON, `--help` | notion-tasks-cli | `cli/notion_tasks.py` |
| Regra de negócio compartilhada (tarefas, clonagem, conteúdo, ingestão, sync GitHub, exportação DOCX, anexos, import retomável) | notion-starter | `src/notion_starter/services/` |
| Relatório por dia em um database (upsert pela data; anexa em vez de duplicar) — padrão de hora/duração em [`docs/PADRAO-RELATORIOS.md`](docs/PADRAO-RELATORIOS.md) | notion-starter | `src/notion_starter/services/relatorios_diarios.py` |
| Histórico de um repositório git agrupado por dia (lógica pura, sem rede) | notion-starter | `src/notion_starter/git_historico.py` |
| Histórico de **vários** repositórios consolidado por dia + varredura que descobre repositórios numa pasta | notion-starter | `src/notion_starter/services/historico_repositorios.py` (`consolidar_dias`, `descobrir_repositorios`, `corpo_markdown`) |
| Fonte de planilha (.xlsx/.csv) do framework de ingestão | notion-starter | `src/notion_starter/services/ingestao.py` (`FontePlanilha`) |
| Normalização de números/datas no formato brasileiro | notion-starter | `src/notion_starter/valores_br.py` |
| Re-parent (mover página/database), File Upload API, schema de coluna por tipo | notion-starter | `src/notion_starter/client.py` (`mover_pagina` usa `POST /pages/{id}/move` e relê o pai; `resolver_data_source`; `listar_modelos`), `properties.py` (`schema_propriedade`, `valor_de_texto`) |
| Prever colunas criadas/valores perdidos ao mover uma linha entre databases | notion-starter | `src/notion_starter/services/movimentacao.py` (`prever_movimento`, `mover_pagina`, `MovimentoComPerdasError`) |
| Copiar corpo bloco a bloco (lista branca, sem `null`, aninhamento em etapas, desfaz em falha) | notion-starter | `src/notion_starter/services/copia_corpo.py` |
| Modelos nativos de database (listar, preencher a partir de manifesto) | notion-starter | `src/notion_starter/services/modelos.py` |
| Acervo: inventário com datas e caminho, download retomável de corpos, busca por regex no texto | notion-starter | `src/notion_starter/services/inventario_workspace.py`, `corpos.py`, `busca_conteudo.py` |
| Garantir, renomear e remover coluna de schema | notion-starter | `src/notion_starter/services/schema.py` |
| Comando da CLI que usa serviço do starter **ainda não publicado** (import dentro do comando, recusa `configuracao` com o starter do PyPI) | notion-tasks-cli | `cli/notion_tasks.py` (`_servico_do_starter`) |
| Editar propriedades de linha genérica (`editar-linha`, set/append) | notion-tasks-cli | `services/propriedades.py` |
| Adaptadores GitHub/OpenRouter/Notion | notion-tasks-cli | `integrations/` |
| Endpoints REST, serializers | notion-workspace-app | `server/api/` |
| Servidor MCP (ferramentas `notion.*`) | notion-workspace-app | `server/mcp_server.py` |
| Interface web (kanban, filtros, exploração) | notion-workspace-app | `front/src/` |
| Launcher TUI | notion-workspace-app | `start_app.py` |

**Consolidação:** `integrations/github.py`, `integrations/openrouter.py` e os `services/`
compartilhados do CLI/app são shims para `notion-starter`. Corrija a implementação real em
`modules/notion-starter/src/notion_starter/`. O que ainda é específico do consumidor permanece
no consumidor (ex.: `services/propriedades.py` do CLI e `integrations/notion.py` de cada borda).

### Fluxo de trabalho

1. `python bootstrap.py` — garante `modules/` atualizado (`git pull` em cada módulo).
2. Edite no módulo correto. Cada módulo tem seu próprio `AGENTS.md` com detalhes locais.
3. Rode os testes **do módulo**: `python -m pytest` dentro dele.
4. Commite e push **dentro do módulo** (Conventional Commits: `feat:`/`fix:`/`docs:`/`refactor:`/`chore:`).
5. Se mudou arquitetura, contratos entre módulos ou o roteamento acima, atualize este hub (`AGENTS.md`, `README.md`) e registre a decisão no `IA.md`.

### Convenções (valem para todos os módulos)

- **Prefira scripts e automações a mudanças manuais** — sempre. Toda vez que precisar manipular dados (no Notion ou em qualquer projeto que use o padrão de qualidade Felixo), use primeiro a CLI `notion-tasks`, os serviços do `notion-starter` ou um script reutilizável; edição manual é exceção e deve ser registrada com o motivo. Por quê: scripts reutilizáveis viram patrimônio — modelos de IA cada vez melhores podem ler, melhorar e estender essas ferramentas, aprimorando o ecossistema naturalmente ao longo do tempo. Uma mudança manual não deixa rastro reutilizável; um script deixa.
- Código, docstrings e mensagens de erro **em português**.
- Fronteiras de camada sagradas: bordas (CLI/API/MCP) não têm regra de negócio; `services` não conhece HTTP; só o `NotionClient` fala com a API do Notion.
- Tipagem forte (`TypedDict` para payloads, `dataclass` para resultados); exceções derivam de `NotionSyncError`.
- Nunca commitar `.env`, tokens ou bancos SQLite.
- Histórico de decisões de arquitetura: `IA.md` (leia antes de mudanças estruturais).
- Cada módulo tem seu próprio gate (`ruff check .` + `python -m pytest`; o app também `npm run lint`/`npm run build` em `front/`) e CI no GitHub Actions. As suítes passam 100% em Windows e POSIX.
