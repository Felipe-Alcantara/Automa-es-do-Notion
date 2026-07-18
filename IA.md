# 🤖 IA.md — Contexto operacional do projeto

> **O que é**: Memória técnica do projeto para retomada de contexto por IA ou por
> um novo mantenedor, sem precisar reler todo o código ou o histórico de conversa.
> Baseado no template de contexto do Felixo System Design.

> ⚠️ **NOTA DE ESTRUTURA (2026-07-02)**: o monorepo descrito neste documento foi
> separado em módulos. Os caminhos citados abaixo (`src/`, `cli/`, `server/`,
> `front/`) hoje vivem em repositórios próprios — veja o mapa de roteamento no
> **`AGENTS.md`** deste hub, que é o guia operacional atual. Este arquivo permanece
> como **histórico de decisões** (as decisões continuam válidas; só os caminhos
> mudaram): `src/notion_starter` → repo `notion-starter`; `cli/` + `core/` +
> `integrations/` + `services/` → repo `notion-tasks-cli`; `server/` + `front/` +
> `start_app.py` → repo `notion-workspace-app`.

---

## 📊 ESTADO ATUAL (RESUMO VIVO)

<!--
  EXCEÇÃO à regra append-only: esta seção é um RESUMO reescrevível.
  Ela responde "onde o projeto está AGORA" em poucas linhas. Reescreva-a
  livremente a cada mudança de estado — o histórico detalhado continua
  protegido nas seções datadas abaixo e nos archives.
-->

Última atualização: [2026-07-18]

- **Fase**: ecossistema modularizado e estável. O hub concentra documentação,
  roteamento (`AGENTS.md`) e scripts de workspace (`bootstrap.py`,
  `check-dev.py`, `sync.py`, `start_app.py`); o código vive nos módulos
  `notion-starter`, `notion-tasks-cli` e `notion-workspace-app` (em `modules/`).
- **Gate do hub**: `python start_app.py` + `python check-dev.py` (nenhum check
  exige token real). Gate de código é o de cada módulo (`ruff` + `pytest`).
- **Qualidade dos módulos**: READMEs no design system e contratos `QUALIDADE.md`;
  gates verdes em 2026-07-18 (starter 235, CLI 127, app 256 + 2 skips; front com
  `oxlint` e build Vite aprovados).
- **Histórico**: registros de junho/2026 (era monorepo) arquivados em
  [`docs/ia-archive/IA-ARCHIVE-2026-06.md`](docs/ia-archive/IA-ARCHIVE-2026-06.md).
- **Pendência aberta**: CLI avisar quando `NOTION_TOKEN` é ignorado por perfil
  ativo (melhoria nos módulos — ver resumo de [2026-07-13]).

[2026-07-18] Registros de junho/2026 (era monorepo) movidos na íntegra para
`docs/ia-archive/IA-ARCHIVE-2026-06.md` (compactação sem perda do template).

---

## 🎯 OBJETIVO DO PROJETO

[2026-06-24] `notion-starter-boilerplate` é um boilerplate/template open source para
iniciar projetos sobre a API do Notion. Traz um cliente Python tipado, helpers de
propriedade, validação de schema e exceções claras como base pronta para clonar e
adaptar. Independente de framework, uma única dependência de runtime (`requests`).
Público: desenvolvedores que vão começar uma integração com o Notion.
Distribuição: como TEMPLATE (clone/"Use this template" e renomeie), não como pacote
PyPI fechado. O `pyproject.toml` segue funcional para `pip install -e` local.

[2026-06-29] O repositório público `Automa-es-do-Notion` passou a ser documentado como
aplicação local de automações para Notion, GitHub e IA, não como template genérico.
O core `notion_starter` continua sendo a base importável, mas README, metadados do
`pyproject.toml`, CONTRIBUTING e `start_app.py` agora descrevem o produto real.

---

## 🏁 METAS & MILESTONES

_Registros de junho/2026 no [archive](docs/ia-archive/IA-ARCHIVE-2026-06.md)._

---

## 🛠️ STACK & DEPENDÊNCIAS

_Registros de junho/2026 no [archive](docs/ia-archive/IA-ARCHIVE-2026-06.md).
Stack atual do hub: Python 3.10+ (scripts de workspace, sem dependência de
runtime além de `requests`/`pytest` para dev); código e dependências reais nos
módulos._

---

## 📐 DECISÕES DE ARQUITETURA

_Registros de junho/2026 no [archive](docs/ia-archive/IA-ARCHIVE-2026-06.md).
As decisões continuam válidas — só os caminhos mudaram para os módulos (ver
nota de estrutura no topo)._

---

## 🎨 DECISÕES DE DESIGN & CONVENÇÕES

_Registros de junho/2026 no [archive](docs/ia-archive/IA-ARCHIVE-2026-06.md).
Convenções vigentes resumidas no `AGENTS.md` (português, Conventional Commits,
fronteiras de camada)._

---

## 🧪 TESTES IMPORTANTES

_Registros de junho/2026 no [archive](docs/ia-archive/IA-ARCHIVE-2026-06.md).
As suítes vivem nos módulos; o gate do hub é `check-dev.py`._

---

## 🐛 BUGS & FIXES RELEVANTES

_Registros de junho/2026 no [archive](docs/ia-archive/IA-ARCHIVE-2026-06.md)._

---

## 🔗 INTEGRAÇÕES & SERVIÇOS EXTERNOS

_Registros de junho/2026 no [archive](docs/ia-archive/IA-ARCHIVE-2026-06.md).
Integrações (Notion, OpenRouter, GitHub, MCP) configuradas nos módulos; nenhum
segredo versionado._

---

## 📝 NOTAS GERAIS

_Registros de junho/2026 no [archive](docs/ia-archive/IA-ARCHIVE-2026-06.md)._

---

## 🧠 RESUMOS DE DECISÃO

_Resumos de junho/2026 no [archive](docs/ia-archive/IA-ARCHIVE-2026-06.md).
Abaixo, os registros da era hub (julho/2026 em diante)._

[2026-07-06] CONTEXTO: Rodada de padronização do hub segundo o Felixo System Design
("Padrão de qualidade"). O hub tinha diretórios fantasma remanescentes da divisão do
monorepo (`cli/`, `server/`, `src/`, `tests/` contendo apenas `__pycache__`), caches de
tooling (`.pytest_cache/`, `.ruff_cache/`) e o `operacional.sqlite3` (estado do app antigo,
gitignorado) na raiz — ruído que não pertence a um repositório que é só documentação e
roteamento. O README já era forte, mas faltavam seções obrigatórias do padrão de README.
DECISÃO: (1) remover o resíduo local do monorepo, deixando na raiz apenas docs + roteamento
+ ferramentas de bootstrap (`bootstrap.py`, `sync.py`, `check-dev.py`); (2) completar o
README com as seções ⭐ obrigatórias que faltavam — Índice, Estrutura do Projeto (árvore do
hub), Autor e o rodapé de Contribuições + CTA — e padronizar o header (badges
`for-the-badge`, descrição em negrito, links rápidos). Não alterei a titularidade do
`LICENSE` (copyright "André Gustavo" difere do autor Git "Felipe Martin"): mudança de
titularidade de licença é decisão do dono, fica registrada aqui como pendência a confirmar.
VALIDAÇÃO: âncoras do Índice conferidas contra os cabeçalhos `##` do README; `git status`
antes da limpeza estava limpo (o resíduo era não rastreado/ignorado, então a remoção não
afeta o histórico versionado). Nenhum código foi tocado — funcionalidade continua vivendo
nos módulos, conforme AGENTS.md.

[2026-07-06b] CONTEXTO: Ergonomia de desenvolvimento dos módulos (task "verificar se está
fácil tanto para uso quanto para desenvolvimento"). Observado que os módulos estavam
clonados em DOIS lugares — em `modules/` (cópia feita pelo bootstrap dentro do hub) e na
pasta acima (`../notion-starter`, `../notion-tasks-cli`, `../notion-workspace-app`), mesmos
remotes e commits. O `bootstrap.py` antigo sempre criava a cópia dentro do hub, ignorando o
clone que já existia, gerando duplicação e ambiguidade sobre "onde eu desenvolvo".
DECISÃO: `bootstrap.py` passa a reusar o clone existente. Ordem de preferência por módulo:
(1) já preparado em `modules/<nome>` → `git pull --ff-only`; (2) já clonado em `../<nome>` →
cria um LINK em `modules/<nome>` apontando para lá (junction no Windows via `mklink /J`, que
não exige admin; symlink no POSIX), reusando o mesmo working copy; (3) não existe →
`git clone` do GitHub. `modules/<nome>` segue sendo o caminho canônico de dev, então
check-dev.py e todo o roteamento do AGENTS.md continuam válidos sem mudança — o `.git` é
resolvido através do link. Escolhi o link (em vez de "só usar ../<nome>") para não quebrar
nada que já aponta para `modules/`.
VALIDAÇÃO: removido `modules/`, rodado `python bootstrap.py` → detectou os três clones em
`../` e criou junctions (confirmado por `os.path.realpath('modules/notion-starter')` →
`...\Github\notion-starter`); `git pull --ff-only` rodou dentro de cada link ("Already up to
date"); `python check-dev.py` reporta os três `[OK]` (o `.git` é encontrado através da
junction). Docs vivas atualizadas no mesmo passo: README (seção "Primeiro passo") e AGENTS.md
(pré-requisito bootstrap).

[2026-07-06c] CONTEXTO: Lote de tarefas de uso/dev vindas de agentes que operavam o Notion:
(1) "resolver as propriedades" — ao editar uma página que é linha de database, os agentes só
mexiam no conteúdo (blocos), nunca nas propriedades, a menos que explicitados; (4) proposta de
um comando "editar-linha" no notion-tasks-cli (o CLI cobria conteúdo e tarefas, mas não editava
propriedades de linhas genéricas, forçando ir à API crua com o token do hub); (3) tornar o
append de conteúdo seguro (preservar o existente, respeitar limites, verificar pós-PATCH).
DECISÃO: as tarefas 1 e 4 têm a mesma raiz — faltava um caminho de propriedades para linha
genérica. Adicionado `NotionClient.obter_pagina` no notion-starter (GET /pages/{id} já traz o
`type` de cada coluna) e o comando `editar-linha <page_id> --set "Nome=valor"` no
notion-tasks-cli (`services/propriedades.py`), que infere o tipo da própria página, converte o
valor (title, rich_text, number, checkbox, select, status, multi_select, relation, people, date
com intervalo "inicio..fim", email, phone, url), limpa com valor vazio e recusa tipos calculados.
O `--help`/guia passou a recomendar "comece pelas propriedades, depois o conteúdo" — atacando a
raiz da tarefa 1 (agora há caminho e ele é o recomendado). Tarefa 3: `escrever_conteudo` passou a
anexar em lotes de 100 (limite do Notion por requisição; o limite de 2000 chars/rich_text já era
tratado por `content.py` na lib) e a confirmar, pela resposta da API, que todos os blocos foram
criados (erro em escrita parcial); o append sempre entra ao final, preservando o existente. A
correção de conteudo.py foi espelhada em notion-workspace-app/server (camada services duplicada).
VALIDAÇÃO: notion-starter 21/21 testes; notion-tasks-cli 72/72 (incl. novos test_services_
propriedades e test_services_conteudo, e casos de editar-linha no test_cli); notion-workspace-app
test_services_conteudo 12/12 (novo teste de lotes via callback do `responses`). Smoke test:
`python -m cli editar-linha --help` e `guia` mostram o comando e a nova dica. Os três repos foram
commitados e publicados no main. PENDÊNCIA de runtime: o notion_starter instalado (site-packages,
via git+https) ainda não tem `obter_pagina` — é preciso reinstalar a dependência para o
`editar-linha` funcionar em execução real (os testes usam doubles e não dependem disso).

[2026-07-06d] CONTEXTO: Ao atualizar o relatório diário no Notion (database "Relatórios
diários"), caí exatamente no vício da tarefa 1: atualizei o CONTEÚDO (blocos, via `escrever`)
e esqueci as PROPRIEDADES (colunas rich_text "O que fiz", "Resumo", "Próximos passos"). O
usuário apontou. Além disso pediu que a PRÓPRIA ferramenta recomende, de forma explícita,
mexer nas propriedades primeiro e no conteúdo depois.
DECISÃO: (1) Atualizei as propriedades preservando o conteúdo original — peguei os objetos
rich_text originais de cada coluna e anexei um item novo ao final (respeitando o teto de 2000
unidades por item), via `atualizar_pagina`; isso é exatamente o comportamento que a tarefa 3
descrevia para rich_text. (2) Reforcei o guia do CLI: novo campo estrutural
`fluxo_recomendado` (guia --json e humano) com a REGRA "propriedades primeiro (editar-linha),
conteúdo depois (escrever)", e os `--help` de `editar-linha` e `escrever` passaram a apontar a
ordem. Commit `feat` no notion-tasks-cli (add8e33), com teste garantindo a ordem no guia.
LIMITAÇÃO REGISTRADA (próximo passo): o comando `editar-linha` faz FULL-REPLACE do valor e o
builder `properties.rich_text` cria um único item — ou seja, não fatia texto >2000 nem anexa
preservando o existente. Para colunas rich_text longas (como as do relatório) hoje é preciso ir
via `atualizar_pagina` montando o array. Ideia: dar ao `editar-linha` um modo "append" e fazer
o builder de rich_text fatiar em ≤2000 como o `content.py` já faz para blocos.
VALIDAÇÃO: notion-tasks-cli 74/74 testes; guia humano mostra o fluxo em destaque; relatório
06/07 conferido via API — "O que fiz" (6932 chars, 5 itens: 4 originais + 1 novo), "Resumo"
(2064, 2 itens) e "Próximos passos" (1355, 2 itens) com o texto original íntegro no início e a
seção Automações do Notion ao final; Status/Área/Data mantidos.

[2026-07-06e] CONTEXTO: Fechar a lacuna registrada em [2026-07-06d]: o `editar-linha` fazia
full-replace e não fatiava rich_text >2000, então atualizar propriedades longas (como as do
relatório) exigia montar o array via API na mão. Pedido: deixar tudo preparado para uso da
forma mais otimizada, seguindo o padrão.
DECISÃO: (1) Na lib (notion-starter): centralizei a fatia UTF-16 em `utils.fatiar_utf16` e o
teto em `constants.MAX_RICH_TEXT` (antes privados em content.py — agora reusados sem duplicar,
content.py passou a importá-los), e os builders `properties.title`/`rich_text` passaram a
fatiar texto >2000 em vários itens que o Notion concatena. Texto curto segue gerando 1 item
(compatível). (2) No CLI (notion-tasks-cli): `editar-linha` ganhou `--append "Nome=texto"`, que
acrescenta ao final de colunas de texto preservando os itens rich_text originais (lê via
obter_pagina, limpa os itens para forma gravável, junta o texto novo fatiado, num único PATCH);
`--set` segue substituindo. Valida conflito set+append na mesma coluna e append em coluna não
textual. O append NÃO apara espaços (preserva o separador \n\n), diferente do --set.
(3) Dev: instalei o notion-starter em modo EDITÁVEL apontando para o clone local (via o junction
de modules/), então mudanças na lib valem na hora para o CLI, sem reinstalar do git a cada vez —
o setup de desenvolvimento mais otimizado, alinhado ao fluxo de junctions do bootstrap.
VALIDAÇÃO: notion-starter 171/171 (novos testes de fatia: 4500 chars→[2000,2000,500], emoji
conta 2 unidades UTF-16, vazio→1 item); notion-tasks-cli 79/79 (append preserva original,
fatia em 2000, erro em coluna não-texto, erro set+append na mesma coluna, set+append juntos em
colunas diferentes). End-to-end real na Notion: `editar-linha <relatório> --append "Resumo="`
(no-op) reenviou os itens originais e o Resumo continuou com 2 itens/2064 chars — preservação
confirmada sem poluir. Commits e push: notion-starter (d278d3d), notion-tasks-cli (ad2e52a).

[2026-07-06f] CONTEXTO: Fechamento da rodada — garantir que git, docs e a database (relatório
no Notion) reflitam tudo, seguindo o padrão de qualidade.
DECISÃO: (1) Git: os quatro repositórios (hub + três módulos) já estavam commitados (Conventional
Commits, docs no mesmo passo) e sincronizados com o origin/main — confirmado por fetch, sem
ahead/behind. (2) Docs vivas atualizadas: hub AGENTS.md (roteamento MODO USO ganhou `editar-linha`
com a ordem propriedades→conteúdo; MODO DEV ganhou linhas para `obter_pagina`/`atualizar_pagina`
e `services/propriedades.py`), hub README (comandos e tabela de roteamento com editar-linha e
obter_pagina), e notion-starter README/AGENTS (obter_pagina, builders de propriedade que fatiam
>2000, `utils.fatiar_utf16`). (3) Database: o relatório de 06/07 foi atualizado com o trabalho
mais recente usando a PRÓPRIA CLI — `escrever` para o conteúdo e `editar-linha --append` para as
colunas "O que fiz", "Resumo" e "Próximos passos" (dogfooding do modo append), preservando o
conteúdo original.
VALIDAÇÃO: relatório conferido via API — "O que fiz" 6 itens/7311 chars, "Resumo" 3/2387,
"Próximos passos" 3/1510, todos com o texto original íntegro no início e a atualização ao final.
Commits/push: notion-starter docs (81ecb75); hub (docs de roteamento) neste passo.

[2026-07-07] CONTEXTO: Task do Notion "Colocar um módulo de github para notion" (Prioridade
Hiperfoco/Urgente) pedia um módulo que importasse repositórios do GitHub para uma database do
Notion e fosse fácil de atualizar. Investigação mostrou que a FUNCIONALIDADE JÁ EXISTIA madura no
`notion-tasks-cli` (`services/inventario_github.py` + `integrations/github.py`, exposta pelo
comando `atualizar-github`): upsert por URL, ~20 propriedades ricas, README em subpágina com
detecção de mudança por hash. O trabalho real foi documentar/expor e estender, não recriar.
DECISÃO: (1) Documentar/expor — novo guia `docs/GITHUB-DATABASE.md` (uso, rotina, FAQ), linkado no
README e no AGENTS (a tabela MODO USO não citava `atualizar-github`; agora cita). (2) Estender — o
serviço e o CLI ganharam `ignorar_arquivados`/`--sem-arquivados` para manter a database só com
repositórios ativos; filtro aplicado no ponto compartilhado `_coletar_repos` (vale para
`exportar_repos` e `atualizar_repos`), com testes de serviço e de CLI. (3) Qualidade do hub
(Felixo): o hub ganhou `start_app.py` — menu interativo obrigatório (contrato #11) que instala a
CLI, sincroniza módulos, configura o `.env` e opera o Notion; documentado no README como forma
principal de rodar. `docs/QUALIDADE.md` estava desatualizado (descrevia o gate do antigo monorepo:
`scripts/quality_check.py`, `front/`, npm, `CONTRIBUTING.md` — nada disso existe no hub); reescrito
para a realidade do hub (gate = `check-dev.py`/`start_app.py`; gate de código = `pytest` por módulo).
VALIDAÇÃO: suíte do `notion-tasks-cli` verde (82 passed); `--sem-arquivados` aparece no `--help` e é
propagado ao serviço (teste de CLI); `start_app.py` valida sintaxe, helpers e renderiza o Status.
Commit/push do código vai no repo do módulo (`notion-tasks-cli`), não no hub.

[2026-07-07b] CONTEXTO: Pedido de portar as funções de coleta/análise do app React
`Felipe-Alcantara/Git-Hub-Repositories` para o Notion — "principalmente importar vários perfis de uma
vez, verificando duplicatas". INVESTIGAÇÃO: a função destacada JÁ existia no ecossistema
(`atualizar-github --contas a,b,c`: multi-conta, dedup por URL/upsert, privados do usuário
autenticado, resiliente por conta). Cruzando o app com o módulo, faltavam de fato duas coisas: (1)
aceitar URL de perfil/`@handle` (o app tem `extractUsername`); (2) sync incremental por data
(`updated_at`) que o app usa para pular repos sem mudança e reportar novos/atualizados/pulados.
DECISÃO — ONDE MORAR (seguindo o padrão de qualidade #9, evitar duplicação): `integrations/github.py`
era byte-idêntico nos dois repos (`notion-tasks-cli` e `notion-workspace-app/server`) e
`inventario_github.py` só divergia pela minha edição `--sem-arquivados` de [2026-07-07] que eu tinha
esquecido de espelhar (drift proibido pelo AGENTS). Consolidar a camada no `notion-starter` é o
passo de roadmap, mas é refactor grande/arriscado (imports de 3 repos + Django/MCP) —
desproporcional. Escolhi: escrever a lógica nova como FUNÇÕES PURAS reutilizáveis no ponto DRY que
cobre todos os callers, e manter as duas cópias byte-idênticas (política vigente), corrigindo o
drift. IMPLEMENTAÇÃO: (a) `extrair_login(texto)` em `integrations/github.py`, chamada por
`_validar_usuario` — logo TODO caller (CLI, serviço, app/MCP) passa a aceitar URL/@handle/nome sem
mudar; (b) `apenas_mudancas` em `atualizar_repos` + helpers puros `_parse_data` (tolera `Z` e
`+00:00`) e `_repo_mudou_desde_pagina` (compara `updated_at` do GitHub com a coluna "Atualizado em"
gravada; na dúvida atualiza), novo contador `paginas_puladas`; (c) flags CLI `--apenas-mudancas` (a
`--sem-arquivados` já existia) e o resumo humano/JSON ganhou `pulados`. Aplicado nos DOIS repos
(cópias idênticas de novo); testes espelhados nas suítes de cada um (o app tinha suíte bem mais
rica). Expor as flags no MCP/REST do workspace-app fica como dívida anotada.
VALIDAÇÃO: `notion-tasks-cli` 96 passed; `notion-workspace-app` 66 passed nos testes de
github/inventário (as 3 falhas restantes são as pré-existentes conhecidas do Windows —
`test_start_app`×2, `test_services_ingestao`×1). Ruff sem erros novos (só o `I001` pré-existente em
`inventario_github.py`, idêntico nos dois repos). `github.py` e `inventario_github.py` confirmados
byte-idênticos entre os repos após a mudança.

[2026-07-07c] CONTEXTO: Fechamento da dívida anotada em [2026-07-07b]: versionar melhor o
`notion-tasks-cli`, expor as flags novas no MCP/REST do `notion-workspace-app` e reduzir duplicação
entre CLI e app. Havia uma tensão de arquitetura: o hub fala em consolidar `integrations/services`
no `notion-starter`, mas o AGENTS local do `notion-starter` proíbe regra de negócio de produto
nessa biblioteca base.
DECISÃO: consolidar agora apenas os ADAPTADORES puros e reutilizáveis (`GitHubClient`/`RepoInfo` e
OpenRouter) no `notion-starter`, mantendo os imports públicos antigos como shims compatíveis em
`notion-tasks-cli/integrations/*` e `notion-workspace-app/server/integrations/*`. Os `services/*`
continuam nos consumidores por enquanto, porque carregam regra de negócio de produto e movê-los
para a lib base violaria a fronteira local; a próxima consolidação deve ser desenhada como pacote
compartilhado ou como camada explicitamente aceita no `notion-starter`, não como despejo automático.
O `notion-tasks-cli` foi bumpado para `0.1.1`; o `notion-starter` também para `0.1.1` por expor
novos módulos públicos. O workspace-app ganhou `POST /api/github/atualizar` e a ferramenta MCP
`notion.update_github_inventory`, ambas com `sem_readme`, `sem_arquivados` e `apenas_mudancas`,
delegando finas para `services.inventario_github.atualizar_repos`.
VALIDAÇÃO: `notion-starter` 171/171; `notion-tasks-cli` 96/96; `notion-workspace-app`
269/272, restando só as três falhas Windows já documentadas no AGENTS (`test_services_ingestao`
encoding cp1252 e `test_start_app`×2 normalização de paths POSIX em Windows). Testes focados das
novas bordas passaram: `tests/test_api_tarefas.py` + `tests/test_mcp_server.py` = 63/63, e
`tests/test_integrations_openrouter.py` = 15/15 após ajustar o shim para preservar monkeypatch do
cache.

[2026-07-07d] CONTEXTO: Fechamento da dívida restante de [2026-07-07c]. Depois de expor as flags
no REST/MCP e consolidar adaptadores, ainda restava a duplicação de `services/*` entre
`notion-tasks-cli` e `notion-workspace-app/server`. O usuário pediu resolver de vez e atualizar a
nota do relatório.
DECISÃO: mover os 10 serviços byte-idênticos para `notion-starter/src/notion_starter/services/`
(`clonagem`, `conteudo`, `exploracao`, `ia`, `ingestao`, `inventario_github`, `normalizacao`,
`projetos`, `sincronizar_github`, `tarefas`) e transformar os arquivos correspondentes nos dois
consumidores em shims de compatibilidade. `services/propriedades.py` permanece no CLI porque não
é duplicado e representa funcionalidade específica da borda CLI. `integrations/notion.py` também
permanece em cada consumidor: é a fábrica de configuração/ambiente, não regra compartilhada. O
`notion-starter` foi bumpado para `0.1.2`; o `notion-tasks-cli` também para `0.1.2` para distinguir
a build com shims. AGENTS/README dos quatro repos foram atualizados para remover a regra antiga
de "aplique bugfix nos dois" e apontar a implementação real para `notion_starter.services`.
VALIDAÇÃO: `notion-starter` 171/171; `notion-tasks-cli` 96/96; `notion-workspace-app` 269/272,
restando somente as três falhas Windows já documentadas (`test_services_ingestao` e
`test_start_app`×2). Falha intermediária por mojibake foi corrigida restaurando os serviços do
Git com leitura/escrita UTF-8 explícita antes dos testes finais.

[2026-07-07e] CONTEXTO: Pedido de transformar a exportação one-off de relatórios diários do
Notion para DOCX em módulo padronizado. A nota da task exigia: sem token hardcoded, sem paths/IDs
fixos, unificar propriedades + corpo sem `props.json`, preferir Python, testes e documentação.
DECISÃO: a regra de negócio ficou em `notion-starter/src/notion_starter/services/relatorios_docx.py`
porque já é a camada compartilhada consolidada; o `notion-tasks-cli` ganhou apenas a borda fina
`exportar-docx`. O serviço consulta o database por período (`Data` por padrão), lê blocos
recursivamente como Markdown, renderiza um DOCX por relatório com capa, sumário manual, tabela de
propriedades, seções de destaque (Resumo/Bloqueios/Próximos passos) e relatório completo. A
dependência escolhida foi `python-docx` por coesão com o ecossistema Python. O CLI aceita
`--database` ou `NOTION_REPORTS_DATABASE_ID` (fallback `NOTION_DATABASE_ID`), `--de`, `--ate`,
`--saida` e `--campo-data`. `notion-starter` e `notion-tasks-cli` foram bumpados para `0.1.3`.
VALIDAÇÃO: testes focados criados para o serviço (`test_services_relatorios_docx.py`) e para a CLI
(`test_cli_notion_tasks.py -k exportar_docx`). Renderização visual DOCX via LibreOffice não foi
possível no ambiente local porque `soffice` não está instalado; a validação estrutural abre o
arquivo com `python-docx` e verifica propriedades/corpo/tabelas.

[2026-07-08] CONTEXTO: Pedido de colocar todos os repositórios do ecossistema no padrão de
qualidade (Felixo System Design). A separação do monorepo deixou os módulos sem os artefatos
obrigatórios que viviam na raiz: CONTRIBUTING, IA.md, CI, `.env.example` (starter) e menu de
entrada (CLI). O workspace-app ainda carregava 13 erros de ruff pós-consolidação e 3 falhas de
teste "conhecidas" no Windows.
DECISÃO: cada módulo ganhou `CONTRIBUTING.md`, `IA.md` próprio (linha do tempo a partir da
separação, apontando para este IA.md como histórico) e CI GitHub Actions (ruff + pytest em
Python 3.10–3.13; o app também valida o front com oxlint + build Vite, recuperando o gate do
monorepo). `notion-starter` ganhou `.env.example`; a exceção "sem start_app.py por ser
biblioteca" foi registrada no IA.md dele. `notion-tasks-cli` ganhou `start_app.py` (menu
interativo: Instalar / Configurar .env / Status / Usar). No `notion-workspace-app`, o ruff foi
zerado (imports pós-shims + E501) e as 3 falhas Windows foram corrigidas de vez — eram bugs de
portabilidade dos TESTES (escrita sem `encoding="utf-8"` e comparação de caminhos POSIX
literais com `Path` do Windows), não do produto; a nota de "falhas pré-existentes" saiu do
AGENTS.md do hub.
VALIDAÇÃO: `notion-starter` 183/183 + ruff limpo; `notion-tasks-cli` 109/109 + ruff limpo +
smoke do menu (Status/Usar); `notion-workspace-app` 272/272 + ruff limpo + `npm run lint` +
`npm run build` verdes — primeira vez com as três suítes 100% verdes no Windows. Commits
pushados nos três módulos (Conventional Commits, direto no main).

[2026-07-13] CONTEXTO: Numa sessão de MODO USO, um agente recebeu um link válido de página
("Relatórios") e a CLI devolveu "Recurso não encontrado" mesmo após trocar o `NOTION_TOKEN`
exportado pelo token correto. O agente diagnosticou errado ("página não compartilhada com a
integração") e só depois descobriu a causa real: havia um **perfil ativo** salvo na CLI
(`notion-tasks perfis`), e o perfil ativo vence silenciosamente a variável de ambiente — os dois
tokens testados nunca chegaram a ser usados. `--perfil relatorios` resolveu na hora.
DECISÃO: documentar a precedência (perfil ativo > `NOTION_TOKEN` do ambiente/`.env`) no
AGENTS.md (seção MODO USO, com troubleshooting do sintoma "mesmo workspace com tokens
diferentes") e no README (bloco de configuração do token), e rotear `perfis`/`--perfil` na tabela
de comandos do AGENTS.md — o hub documentava apenas a variável de ambiente, que não é a fonte de
verdade quando há perfis salvos.
VALIDAÇÃO: reprodução real na sessão (busca idêntica com dois tokens diferentes; acesso imediato
com `--perfil relatorios`). Melhoria de código correspondente (avisar quando `NOTION_TOKEN` é
ignorado e indicar o perfil em uso nos erros) pertence ao `notion-tasks-cli`/`notion-starter`,
registrada aqui como pendência para PR futuro nos módulos.

[2026-07-18] CONTEXTO: conclusão da padronização de qualidade do hub e dos três módulos.
O hub já atendia ao padrão de README, mas o `IA.md` havia crescido a ponto de dificultar
retomadas; os módulos ainda tinham READMEs mínimos e não possuíam um contrato `QUALIDADE.md`.
DECISÃO: compactar sem perda os registros de junho do hub em
`docs/ia-archive/IA-ARCHIVE-2026-06.md`; adicionar resumo vivo; elevar os três READMEs ao
Felixo System Design; criar `QUALIDADE.md` por módulo; registrar como exceção motivada o uso
de versões mínimas em pacotes Python instaláveis, mantendo o lockfile do frontend.
VALIDAÇÃO: todas as linhas não vazias do `IA.md` anterior continuam no arquivo vivo ou no
archive; links locais e comandos do CLI foram conferidos; `check-dev.py` e compilação do hub
passaram; `notion-starter` 235 testes, `notion-tasks-cli` 127, `notion-workspace-app` 256 com
2 skips, Ruff limpo nos três, Oxlint e build Vite verdes, e `npm audit` sem vulnerabilidades.
