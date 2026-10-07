# Felixo Notion MCP — spec do monolito

> **Estado:** design aprovado em conversa, seção por seção, em 07/10/2026; esta spec
> aguarda revisão do mantenedor antes do plano de implementação.
>
> **O que é:** a especificação para transformar o hub `Automa-es-do-Notion` e os
> módulos `notion-starter`, `notion-tasks-cli` e `notion-workspace-app` num único
> produto, o **Felixo Notion MCP**: um monólito modular cujo centro é um servidor
> MCP, usável localmente e hospedado para qualquer pessoa. Também traz para dentro
> dele as funções do Notion hoje espalhadas no Felixo AI Core e no Felixo Editor
> (repositório `felixo-blog`), e faz esses dois apps passarem a usá-lo.
>
> **Padrão de qualidade:** tudo nesta spec segue o Felixo System Design (Guia
> Mínimo de Qualidade, Política de Git, Design System Backend, Guia do
> `start_app.py` e Guia de Deploy no Railway). Onde esta spec diverge do padrão,
> a divergência está justificada no próprio item.

---

## 1. Contexto

### 1.1 Estado de partida (medido em 07/10/2026)

| Repositório | Papel hoje | Tamanho (código, sem testes) | Pacote PyPI |
| --- | --- | --- | --- |
| `Automa-es-do-Notion` (hub) | documentação, roteamento (`AGENTS.md`), `bootstrap.py`, scripts | — | — |
| `notion-starter` | biblioteca: `NotionClient`, schema, conteúdo, serviços | ~17,5 mil linhas | `notion-starter` 0.4.1 |
| `notion-tasks-cli` | CLI para IAs, 59 subcomandos; binários nativos e auto-update | ~9,2 mil linhas | `notion-automacoes` 0.5.0 |
| `notion-workspace-app` | API Django, SPA React, launcher, servidor MCP | ~5,8 mil linhas | `notion-workspace-app` 0.3.1 |

- O servidor MCP atual (`server/mcp_server.py`, FastMCP via stdio) expõe **18**
  ferramentas `notion.*`; a CLI tem **59** subcomandos. A diferença é a falta de
  paridade que motiva parte deste trabalho.
- O ecossistema **já foi um monorepo** até 02/07/2026 e foi separado de propósito
  (`docs/MODULARIZACAO.md`). A separação trouxe custo real: três pacotes com
  faixas de versão casadas, `bootstrap.py`, `check-dev.py` e o bug das "três
  cópias do starter" (`IA.md`, 24/08/2026).
- Funções do Notion fora do ecossistema:
  - **Felixo AI Core** (`app/electron/services/notion-*.cjs`, ~2,9 mil linhas):
    cliente HTTP próprio na API de *data sources*, várias conexões com token
    cifrado (`safeStorage`), **detecção semântica de colunas** para operar
    tarefas em qualquer database, cache em SQLite com recuo de sincronização.
  - **Felixo Editor** (`felixo-blog/app/src/principal/notion/`, ~530 linhas):
    importar página como artigo Markdown com imagens, gravar URL e status
    "publicado" de volta no Notion, descoberta de propriedades, paginação, retry.

### 1.2 Objetivos (decididos pelo mantenedor)

1. **IAs operarem via MCP**: um servidor MCP com tudo que a CLI faz hoje.
2. **Menos manutenção**: um repositório, um pacote, uma versão.
3. **Substituir o MCP oficial do Notion**, inclusive remoto (claude.ai e celular).
4. **Produto/distribuição**: um produto único e instalável, para o mantenedor e
   para qualquer pessoa.

### 1.3 Decisões tomadas na conversa de design

| Tema | Decisão |
| --- | --- |
| Escopo do monolito | **Tudo junto**: núcleo + MCP + CLI + API Django + SPA React |
| Repositório | o **hub** absorve os três módulos, com histórico git preservado |
| Nome do repositório | `Felixo-Notion-MCP` (produto: **Felixo Notion MCP**) |
| Pacotes publicados | **um só**: `felixo-notion-mcp` (renomeado; os antigos viram transição) |
| MCP remoto | **na primeira entrega**, aberto a **qualquer pessoa** |
| Credencial do Notion | OAuth da integração pública **e** chave de integração (`ntn_…`), ambas de primeira classe |
| Funções do blog e do AI Core | portadas para o monolito |
| AI Core e Editor | passam a usar o monolito **já na primeira entrega** |
| Arquitetura | **A — registro único de operações**, MCP como contrato, Django como casa do HTTP |

### 1.4 Critério de sucesso

- Qualquer pessoa adiciona `https://<domínio>/mcp` como conector personalizado no
  claude.ai (web e celular), entra com o Notion **ou** com a própria chave de
  integração e usa todas as ferramentas, com dados isolados por pessoa.
- Claude Code, Cursor e scripts usam o mesmo servidor por header com chave.
- Claude Code e o Felixo AI Core continuam podendo usar o modo **local** (stdio),
  sem internet e sem enviar o token para servidor algum.
- O AI Core e o Felixo Editor operam o Notion pelo monolito, sem cliente próprio.
- Quem tem `notion-automacoes` (pipx ou binário nativo) migra sem quebrar.
- Um repositório, um pacote e uma versão; os repositórios antigos arquivados.

### 1.5 Fora desta entrega

Ideias que o projeto pode expandir depois, abertas a contribuição: cobrança;
listagem no Marketplace do Notion e no diretório de conectores do Claude; Client
ID Metadata Document (CIMD), já que o DCR vem primeiro; upload de arquivo no modo
hospedado; contas de equipe compartilhadas; redesenho da SPA.

---

## 2. Repositório, layout e regras do padrão

### 2.1 Repositório e histórico

- `Automa-es-do-Notion` é renomeado no GitHub para `Felixo-Notion-MCP`. O GitHub
  redireciona o nome antigo (web, `git clone` e API) enquanto nenhum repositório
  novo usar esse nome.
- Cada módulo entra com o **histórico preservado**: um clone de cada é reescrito
  para um subdiretório com `git filter-repo --to-subdirectory-filter`, mesclado no
  hub com `--allow-unrelated-histories` e depois movido (`git mv`) para o layout
  final. `git log --follow` e `git blame` continuam funcionando.
- `notion-starter`, `notion-tasks-cli` e `notion-workspace-app` são **arquivados**
  (nunca apagados), com o README apontando para o monolito, na ordem da seção 6.4.

### 2.2 Layout por camadas

Segue a estrutura do Design System Backend (§4) e o "monólito modular" (§5.5). Os
nomes de pasta seguem as camadas do padrão, como o projeto já faz (`services/`,
`integrations/`, `core/`); código, docstrings e mensagens continuam em português.

```text
Felixo-Notion-MCP/
├── start_app.py              # menu interativo obrigatório
├── src/felixo_notion_mcp/
│   ├── domain/               # regras puras: propriedades, schema, Markdown↔blocos,
│   │                         #   detecção semântica de colunas
│   ├── services/             # casos de uso (ex-starter + blog + AI Core)
│   ├── repositories/         # persistência (Django ORM): contas, conexões, tokens, jobs
│   ├── integrations/         # cliente HTTP do Notion (único que fala com a API),
│   │                         #   OAuth do Notion, GitHub, OpenRouter
│   ├── api/
│   │   ├── operations/       # registro único: o contrato das três bordas
│   │   ├── mcp/              # servidor MCP gerado do registro (stdio e HTTP)
│   │   ├── cli/              # CLI gerada do registro + perfis, doctor, update nativo
│   │   └── http/             # Django: REST da SPA, login, consentimento, ASGI com /mcp
│   └── core/                 # configuração centralizada, autenticação, logging, erros
├── front/                    # fonte da SPA React; o build vai para api/http
├── tests/                    # espelha as camadas + e2e
├── scripts/                  # scripts reutilizáveis (hoje soltos na raiz do hub)
├── packaging/                # PyInstaller, Dockerfile/configuração do Railway
├── docs/                     # um documento por responsabilidade; specs; ia-archive/
└── README.md · IA.md · CONTRIBUTING.md · LICENSE · .env.example · pyproject.toml · lockfiles
```

### 2.3 Regras do padrão aplicadas

1. **Git:** refatoração estrutural de alto risco em vários módulos justifica
   branch: **uma branch por etapa** (seção 8). Cada uma entra no `main` quando o
   gate dela passa e é apagada (local e remota) logo depois. Commits pequenos, em
   Conventional Commits, sem misturar interno (`IA.md`), público (README, guias)
   e API (contratos MCP/REST). Esta spec, por ser só documentação, vai direto ao
   `main`.
2. **`start_app.py` único na raiz**, com menu colorido e descritivo: Iniciar (MCP
   local, app web local, servidor hospedado em modo de desenvolvimento),
   Instalar/Setup, Configurar (perfis/chaves, variáveis do modo hospedado),
   Status (o `doctor`) e Sair. Substitui os menus dos módulos.
3. **Scripts fora da raiz:** `sync.py` e `criar_tarefas_investigadas_*.py` vão para
   `scripts/`. `bootstrap.py` e `check-dev.py` são aposentados (não há mais
   módulos para clonar nem cópias do starter para conferir); as verificações
   úteis do `check-dev.py` passam para o `doctor`.
4. **Dependências pinadas com lockfile** (`uv.lock` e `package-lock.json`), com
   `pip-audit` e `npm audit` na CI e antes de cada release.
5. **Multiplataforma:** CI em matriz Ubuntu/Windows/macOS; limites específicos
   de um sistema ficam registrados.
6. **Documentação viva:** o `IA.md` do hub continua append-only; os `IA.md` dos
   módulos vão na íntegra para `docs/ia-archive/`. O README segue o Design System
   README.
7. **Pastas locais antigas:** o hub tem pastas ignoradas pelo git, sobras do
   monorepo (`cli/`, `front/`, `server/`, `src/`, `operacional.sqlite3`,
   `.notion-backups/`, `Arquivos/`), que colidem com o layout novo. Elas são
   **movidas para fora** do repositório antes da importação, nunca apagadas, e o
   `.gitignore` é ajustado.

### 2.4 Nomes e versão

- Import: `notion_starter` → `felixo_notion_mcp.domain/services/integrations`
  conforme a camada, numa troca mecânica protegida pelas suítes atuais, **sem**
  camada de compatibilidade (quem importa o nome antigo segue com a última versão
  do `notion-starter` no PyPI).
- Origem → destino de cada parte:

  | Origem | Destino |
  | --- | --- |
  | `notion_starter/client.py`, `github.py`, `openrouter.py` | `integrations/` |
  | `notion_starter/properties.py`, `readers.py`, `content.py`, `schema.py`, `tasks.py`, `valores_br.py`, `git_historico.py` | `domain/` |
  | `notion_starter/services/*`, `inventory.py`; `notion-tasks-cli/services/propriedades.py`, `services/preflight.py` | `services/` |
  | `notion_starter/constants.py`, `exceptions.py`, `logging.py`, `utils.py`; `notion-tasks-cli/core/config.py`, `core/workspaces.py` (perfis) | `core/` |
  | `notion-tasks-cli/integrations/notion.py` (adaptador próprio da borda) | `integrations/` |
  | `notion-tasks-cli/cli/*` (incluindo `atualizacao_nativa.py`, `unificada.py`, `versao.py`) | `api/cli/` |
  | `notion-tasks-cli/integrations/github.py`, `openrouter.py` e os demais `services/*.py` de 21 linhas | removidos (são shims que só reexportam o starter; medido em 07/10/2026) |
  | `notion-tasks-cli/scripts/build_native.py`, `native_entrypoint.py`, `smoke_native.py` | `packaging/` |
  | `notion-workspace-app/server/mcp_server.py` | `api/mcp/` |
  | `notion-workspace-app/server/api/`, `server/config/`, `templates/`, `static/` | `api/http/` |
  | `notion-workspace-app/server/operations/` (modelos `Job`, `Lock`) | `repositories/` |
  | `notion-workspace-app/server/core/config.py` e `server/integrations/notion.py` | unificados com os equivalentes da CLI em `core/` e `integrations/` (hoje são cópias quase iguais: diferem só na exceção de configuração, medido em 07/10/2026) |
  | `notion-workspace-app/server/integrations/github.py`, `openrouter.py` e `server/services/*.py` | removidos (shims de 21–31 linhas que só reexportam o starter) |
  | `notion-workspace-app/front/` | `front/` |
  | `notion-workspace-app/start_app.py`, `start_app.py` do hub | `start_app.py` único na raiz |

  Arquivo que não se encaixar exatamente nesta tabela é decidido no plano da
  etapa 1 pelo critério da camada (seção 2.2) e registrado no `IA.md`.
- Comando principal: `felixo-notion-mcp`, com os subcomandos de hoje (`tasks`,
  `auth`, `mcp`, `app`, `doctor`, `update`). **`notion-tasks` é apelido
  permanente** (skills, prompts e `AGENTS.md` dependem dele);
  `notion-automacoes` é apelido de transição.
- A numeração continua a linha atual: a primeira versão é **0.6.0**.

---

## 3. Núcleo e registro de operações

### 3.1 Contexto de execução explícito

Hoje vários serviços leem configuração global; por exemplo,
`services/tarefas.py` usa `_tasklist_padrao()`, que lê o perfil/ambiente da
máquina. Isso impede o multiusuário. No monolito, **todo caso de uso recebe um
`Contexto`**:

- o cliente do Notion já autenticado para a conexão em uso;
- o mapeamento de colunas de tarefas (detectado ou configurado);
- o logger.

O `Contexto` é montado por uma de três estratégias, todas atrás da mesma interface:

| Estratégia | Onde | De onde vem a credencial |
| --- | --- | --- |
| Perfil local | CLI e MCP stdio | precedência atual: `--perfil` > perfil ativo > `NOTION_TOKEN` |
| Conta hospedada | MCP HTTP com OAuth ou chave pessoal | conta → conexão escolhida → token cifrado no banco |
| Repasse | MCP HTTP com a chave `ntn_…` no header | a chave da requisição, sem guardar nada |

Um **teste de arquitetura** falha se `domain/` ou `services/` importarem
`os.environ`, Django, `mcp` ou `argparse`, ou se qualquer camada além de
`integrations/` falar HTTP com o Notion.

### 3.2 Registro único (`api/operations/`)

Cada operação é declarada **uma vez**:

| Campo | Conteúdo |
| --- | --- |
| `nome` | snake_case em português, igual ao comando da CLI (`editar_linha`) |
| `descricao` | texto escrito para IA: quando usar, o que devolve, armadilhas |
| `entrada` / `saida` | modelos pydantic (já dependência do SDK MCP): validação e JSON Schema únicos para MCP, CLI e REST |
| `efeito` | `leitura`, `criacao`, `alteracao` ou `destrutiva`: gera as anotações MCP (`readOnlyHint`, `destructiveHint`, `idempotentHint`) e exige `--sim` na CLI / `confirmar: true` no MCP |
| `executar(contexto, entrada)` | só chama o serviço |
| `cli` | posicionais, nomes de flag e apelidos, para manter o contrato atual |
| `conjunto` | `essencial` ou `completo` |
| `disponibilidade` | `local`, `hospedado` ou `ambos` |

O uso de pydantic para entrada/saída é uma convenção nova em relação a
"TypedDict para payloads, dataclass para resultados": a justificativa é ter uma
única fonte de validação e de JSON Schema para três bordas. Resultados internos
dos serviços continuam em dataclass.

**Bordas geradas:**

- **MCP:** cada operação vira uma chamada `FastMCP.add_tool(fn, name, title,
  description, annotations, structured_output)` (assinatura conferida no SDK
  `mcp` 1.28.0). Nomes **sem ponto**, porque a API do Claude só aceita
  `[a-zA-Z0-9_-]` em nome de ferramenta. As 18 ferramentas `notion.*` atuais saem,
  com tabela de equivalência no changelog.
- **CLI:** subcomandos argparse gerados. Perfis, `doctor`, `update`, `app start`,
  `mcp start` e `guia` continuam escritos à mão porque pertencem só à borda local.
- **REST:** as operações que a SPA usa, com o mesmo modelo de entrada e saída.
- **Erro:** um único envelope (`codigo`, `mensagem`, `proximo_passo`,
  `http_status`), igual ao da CLI atual: `isError` com o mesmo JSON no MCP, o
  mesmo corpo com status HTTP no REST.

**Garantias por teste:**

- **retrato do parser da CLI** (59 subcomandos, argumentos e flags) gravado
  **antes** da migração; o parser gerado aceita exatamente as mesmas linhas de
  comando;
- **paridade:** toda operação `ambos` aparece no MCP e na CLI;
- **orçamento de contexto:** o tamanho total das definições de ferramenta é
  medido e o teste falha acima do limite; o servidor aceita
  `--conjunto essencial|completo` (padrão `completo`).

### 3.3 Funções vindas do Felixo Editor

| Operação | Comportamento |
| --- | --- |
| `importar_artigo` | página → título + Markdown + lista de imagens com legenda. Local: pode baixar as imagens para uma pasta. Hospedado: devolve as URLs avisando que expiram em cerca de 1 h |
| `registrar_publicacao` | grava a URL do post e o status "publicado": acha a coluna do tipo `url` e uma opção de select/status que signifique publicado. **Nunca inventa coluna nem opção**; sem certeza, avisa e não grava |

- **Conversor único de Markdown:** os conversores do starter e do blog (este com
  listas compactas e numeração real, commit `4fd6bbf` do `felixo-blog`) recebem os
  mesmos casos em testes de caracterização; fica o comportamento melhor de cada
  caso, num conversor só.
- O que já existe no núcleo não é duplicado: retry, descoberta de propriedades
  (`schema`) e listagem (`linhas`). O registro "post ↔ página"
  (`associacoes.ts`) é estado do editor e fica nele.

### 3.4 Funções vindas do Felixo AI Core

- **Detecção semântica de colunas** em qualquer database (título, status,
  "concluída", prazo), por tipo e por palavras em português e inglês, a partir de
  `findSemanticProperty`/`pickStatusPropertyName` do AI Core. Ela preenche o
  mapeamento de tarefas automaticamente; o schema fixo atual (`Etapa`, `Esforço`,
  `Prazo`, `Áreas da vida`) passa a ser um caso detectado ou configurado. Com
  isso, `listar`, `criar`, `mover` e `concluir` funcionam no database de qualquer
  pessoa, requisito do produto aberto.
- **API de data sources como padrão:** o cliente passa a enviar `Notion-Version
  2025-09-03` por padrão, com resolução database → data source. Hoje o starter
  fixa `2022-06-28` (`constants.py`) e usa a versão nova só em alguns endpoints. A
  troca é medida contra o workspace real antes de entrar.
- Várias conexões e token cifrado: seção 4. O cache do canvas é estado de
  interface e continua no AI Core: seção 5.

---

## 4. Modo hospedado

### 4.1 Forma

Um serviço no Railway com o processo ASGI do pacote `[servidor]` e Postgres do
Railway. O padrão prefere SQLite e indica Postgres quando há vários usuários
concorrentes, que é este caso; o modo local continua em SQLite. Domínio próprio
(proposto: `mcp.felixo.com.br`).

| Rota | Função |
| --- | --- |
| `/mcp` | MCP via Streamable HTTP, protegido |
| `/.well-known/oauth-protected-resource`, `/.well-known/oauth-authorization-server`, `/register`, `/authorize`, `/token`, `/revoke` | servidor de autorização próprio (rotas de auth do SDK MCP: `OAuthAuthorizationServerProvider`, `AuthSettings`, conferidos no `mcp` 1.28.0), com armazenamento no Django |
| `/` | Django: login, consentimento, "Minhas conexões", "Minhas chaves", privacidade, termos, SPA e REST |
| `/saude` | healthcheck exigido pelo Railway |

### 4.2 Como o cliente MCP acessa o servidor

| Caminho | Para quem | Como |
| --- | --- | --- |
| OAuth | claude.ai web, Desktop, celular, Cowork | DCR (RFC 7591), PKCE S256 obrigatório e anunciado em `code_challenge_methods_supported`, refresh token rotativo, `invalid_grant` quando o refresh vence, `/token` aceitando `application/x-www-form-urlencoded`, `401` com `WWW-Authenticate: Bearer resource_metadata=…`, `resource` igual à URL do `/mcp`; callback `https://claude.ai/api/mcp/auth_callback` (e `https://claude.com/...`); loopback do Claude Code em `localhost`/`127.0.0.1` em qualquer porta; rotas de OAuth respondendo bem abaixo de 10 s |
| Chave pessoal no header | Claude Code, Cursor, AI Core, scripts, claude.ai com `static_headers` (beta) | `Authorization: Bearer <chave>`; a chave é gerada em "Minhas chaves", mostrada uma vez, guardada só como hash, revogável e presa a uma conexão |
| Repasse da chave do Notion | os mesmos acima | `Authorization: Bearer ntn_…`; usada só naquela requisição, **sem conta e sem gravar nada** |

Nunca se aceita credencial na URL (`?token=`), como exigem a documentação do
Claude e a especificação MCP.

### 4.3 Como o servidor acessa o Notion

Cada **Conexão** (um workspace) tem um tipo:

- **`oauth`:** "Conectar com o Notion" pela **integração pública**
  (`https://api.notion.com/v1/oauth/authorize?owner=user`). A pessoa escolhe as
  páginas liberadas; o retorno traz `access_token`, `refresh_token`,
  `workspace_id`, `workspace_name`, `bot_id` e `owner`. Em 401 do Notion, o
  servidor tenta o refresh (`grant_type=refresh_token`).
- **`chave`:** a pessoa cola a chave da integração interna (`ntn_…`). O servidor
  valida com `GET /v1/users/me` antes de aceitar. Não há refresh; chave
  revogada vira erro com `proximo_passo` pedindo uma nova.

As duas opções aparecem lado a lado na tela de consentimento do `/authorize` e em
"Minhas conexões".

### 4.4 Identidade, credenciais e isolamento

- **Conta sem senha:** identificada pelo usuário do Notion (`owner` do OAuth, ou o
  dono do bot retornado por `/v1/users/me`). Uma conta pode ter várias conexões;
  no consentimento, a pessoa escolhe qual conexão aquele cliente MCP usa.
- **Tokens do Notion cifrados** no Postgres, com a chave de cifragem só nas
  variáveis do Railway. Nossos tokens de acesso/refresh e chaves pessoais
  guardados **só como hash**.
- **Desconectar** revoga nossos tokens e apaga os do Notion. Conexão com refresh
  falho é marcada inválida e as ferramentas devolvem `proximo_passo:
  "reconecte o workspace"`.
- **Isolamento:** o `Contexto` vem **somente** da credencial da requisição; no modo
  hospedado não há cliente global. Toda consulta em `repositories/` filtra pela
  conta. O Notion ainda limita o alcance às páginas liberadas.
- **Dados mínimos:** conteúdo do Notion não é guardado, só atravessa o servidor.
  Logs registram operação, conta e duração; nunca token nem conteúdo.
- **Diferenças do local:** operações de disco (`relatorios_do_git`,
  `anexar_arquivo` por caminho, `importar_planilha`, `exportar_docx`,
  `baixar_corpos`) têm `disponibilidade = local` e não são anunciadas no
  hospedado. Destrutivas exigem `confirmar: true`, além do `destructiveHint`.
- **Limite de requisições** por conta e por IP no OAuth e nas ferramentas.
- **Proteções do Django** ativas (CSRF nas telas com sessão, escape de saída) e
  consentimento mostrando o host do redirect, como pede a especificação MCP.

### 4.5 Operação

- Deploy por push no Railway, **nativo**, sem GitHub Actions para deploy; as
  Actions ficam só com testes, lint e auditoria antes do merge (Guia de Deploy
  Railway, §3).
- Variáveis e segredos **só** no Railway (§5 do guia), com `.env.example`
  documentando os nomes.
- Ambientes `staging` e `production` separados.
- Primeira validação real: adicionar `https://<domínio>/mcp` como conector
  personalizado no claude.ai e no celular.

---

## 5. AI Core e Felixo Editor usando o monolito

Os dois apps trocam o cliente próprio do Notion por chamadas MCP, **sem mudar o que
a interface deles enxerga**. O cliente é o SDK oficial
`@modelcontextprotocol/sdk`, sem pacote npm novo nosso.

### 5.1 Felixo AI Core

- **Execução:** binário nativo do `felixo-notion-mcp` **embutido** no instalador
  de cada sistema (`extraResources` do electron-builder), com versão fixada por
  Release do AI Core e assinado junto com o app. Funciona offline, sem Python. O
  auto-update do binário fica desligado quando embutido.
- **Credencial:** continua no `safeStorage` do AI Core. O processo principal inicia
  o MCP por stdio com a chave em variável de ambiente (nunca em argumento), um
  processo por conexão ativa. Opcional nas configurações: usar o servidor
  hospedado.
- **Sai:** `notion-client.cjs` e a parte HTTP/normalização do
  `notion-service.cjs`. **Entra:** `notion-mcp-client.cjs`, que chama as
  operações e devolve **os mesmos formatos** de hoje.
- **Não muda:** canais IPC `notion:connections:*`, `notion:databases:list`,
  `notion:tasks:*`; renderer; cache em SQLite (migrações 011 e 012); recuo de
  sincronização. Um teste de contrato grava os formatos IPC atuais antes da troca.
- As skills `notion-operacoes` e `notion-anotacoes-para-tarefas` seguem válidas
  (`notion-tasks` continua) e ganham a menção ao MCP (seção 6.5).

### 5.2 Felixo Editor (`felixo-blog`)

- **Execução:** o `start_app.py` do blog instala `felixo-notion-mcp` (pipx) em
  Instalar/Setup; o processo principal do Electron o inicia por stdio. Se faltar,
  a tela mostra o passo a passo.
- **Sai:** `principal/notion/` (`cliente`, `paginacao`, `blocos`, `importacao`,
  `descoberta`, `paginasDaDatabase`, `statusDeVolta`), substituídos por
  `linhas`, `schema`, `importar_artigo` (baixando as imagens para a pasta do post)
  e `registrar_publicacao`.
- **Fica:** `associacoes.ts`, `canais/notion.ts` e o renderer.

### 5.3 Regras comuns

- Os schemas das ferramentas MCP são o **contrato versionado**: mudança que quebra
  schema exige versão maior. Cada app fixa a versão e roda testes de contrato
  contra ela na própria CI.
- O envelope de erro chega aos apps, que mostram `mensagem` e `proximo_passo`.
- As mudanças são commitadas **nos repositórios dos apps** (`Felixo-AI-Core`,
  `felixo-blog`), com o gate e a CI deles, em branch própria, coordenadas pelo
  scratchpad do canvas (o AI Core tem vários agentes em paralelo). O monolito
  absorve só as funções do Notion, não o código desses apps.

---

## 6. Distribuição e migração

### 6.1 Pacote novo `felixo-notion-mcp`

| Extra | Conteúdo |
| --- | --- |
| base | núcleo, CLI, MCP local (stdio) |
| `[app]` | Django e SPA locais |
| `[servidor]` | modo hospedado: Postgres, servidor ASGI, cifragem |

Executáveis: `felixo-notion-mcp` e `notion-tasks`. Publicação por Trusted
Publishing a partir do `Felixo-Notion-MCP` (o PyPI aceita "publicador pendente"
para nome novo, cadastrado uma vez pelo mantenedor).

### 6.2 Pacotes antigos

- **`notion-automacoes` 0.6.0 (transição):** sem código próprio, depende de
  `felixo-notion-mcp` e reexpõe `notion-automacoes` e `notion-tasks` apontando para
  o código novo, com aviso no stderr. `pipx upgrade notion-automacoes` leva ao
  produto novo; um smoke com pipx nos três sistemas prova isso.
- **`notion-starter` 0.5.0:** só o aviso de incorporação no README e no PyPI; o
  código continua igual para quem o importa como biblioteca.
- **`notion-workspace-app` (final):** depende de `felixo-notion-mcp[app]`, com o
  aviso.

### 6.3 Binários nativos e a ponte de atualização

- Releases novas no `Felixo-Notion-MCP`, assets `felixo-notion-mcp-<alvo>` e
  `.sha256`, mesma matriz (`windows-x64`, `macos-x64`, `macos-arm64`,
  `linux-x64`) e mesmas garantias (SHA-256, troca atômica, `.previous`,
  relançamento pós-troca, cache de 24 h, opt-out).
- **Release-ponte `v0.5.1` no `notion-tasks-cli`**, antes do arquivamento. Amplia a
  task já aberta "publicar Release nativa com o relançamento pós-auto-update de
  macOS/Linux": o atualizador dessa versão sabe migrar para o repositório e os
  assets novos. Quem tem 0.4.x/0.5.0 recebe a 0.5.1 e, no salto seguinte, o
  produto novo **no mesmo caminho de arquivo**.
- Repositório arquivado continua servindo os downloads das Releases antigas, o
  que mantém o rollback manual.

### 6.4 Ordem obrigatória do corte

1. Monolito funcionando: CI verde, paridade e modo hospedado aceitos.
2. Releases `0.6.0`: pacote novo e binários.
3. Pacotes de transição publicados.
4. Release-ponte `v0.5.1` no `notion-tasks-cli`.
5. Issues abertas dos três módulos transferidas (`gh issue transfer`).
6. Repositórios arquivados.

Arquivar antes do passo 4 trancaria os binários antigos na versão atual.

### 6.5 Renomeações que quebram coisas locais

- **Pasta local do clone:** se mudar de `Automa-es-do-Notion` para
  `Felixo-Notion-MCP`, a memória do Claude Code deste projeto (pasta derivada do
  caminho) e a configuração do canvas "Tasks do Notion" do AI Core deixam de
  achar o projeto. Migrar a pasta de memória e a configuração do canvas no mesmo
  passo, ou manter o nome local.
- **Prompts e skills:** `AGENTS.md` e `CLAUDE.md` reescritos (sem `bootstrap.py`,
  sem módulos, roteamento por camada). Skills do AI Core e de
  `~/.config/felixo-ai-core/skills` e o prompt "Workflow 3.0" (Apêndice D)
  passam a citar o nome novo e o MCP.
- **Notion:** a coluna `Repositório` das tasks ganha a opção `Felixo-Notion-MCP`,
  e as tasks abertas dos três módulos passam a apontar para ela, **por script**.

### 6.6 Ações que só o mantenedor pode fazer

Viram tasks no Notion com passo a passo; não bloqueiam o código.

1. Renomear o repositório no GitHub (se preferir fazer pessoalmente).
2. Publicador pendente no PyPI para `felixo-notion-mcp`.
3. Criar a integração **pública** no Notion e cadastrar o redirect. A
   documentação exige revisão **só para o Marketplace**; os campos obrigatórios
   do formulário serão conferidos na tela.
4. DNS do domínio do servidor.
5. Projeto e Postgres no Railway, se o login da CLI do Railway falhar (o guia manda
   parar e pedir).
6. Texto jurídico de privacidade e termos (LGPD): o rascunho é feito pelo agente;
   a decisão é do mantenedor.
7. Opcional: pedir inclusão no diretório de conectores do Claude.

---

## 7. Testes, gate e validação real

| Camada | O que se testa |
| --- | --- |
| Unidade | detecção semântica de colunas; conversor Markdown (casos do starter e do blog); serviços com cliente falso |
| Contrato | retrato da CLI (59 subcomandos); retrato da lista de ferramentas MCP; paridade do registro; envelope de erro; formatos IPC do AI Core |
| Arquitetura | importações proibidas em `domain/`/`services/`; HTTP com o Notion só em `integrations/` |
| Segurança | IDOR entre contas; tokens só como hash e ausentes dos logs; chave em repasse nunca gravada; conformidade OAuth (401 + `resource_metadata`, PKCE, refresh rotativo, `invalid_grant`, form-urlencoded); limite de requisições |
| Integração | app ASGI completo com cliente de teste; job de CI com Postgres de verdade |
| Smoke | binário nativo nos 4 alvos; `pipx upgrade notion-automacoes` nos 3 sistemas |

- As suítes atuais migram inteiras (registradas: starter 677 testes no `IA.md`
  de 27/09/2026, CLI 370 medidos em 02/10/2026, app 279). A contagem não pode cair,
  salvo duplicatas removidas, listadas no `IA.md`.
- **Gate:** `ruff check .`, `pytest` (Ubuntu/Windows/macOS × Python 3.10–3.13),
  `npm run lint` e `npm run build`, `pip-audit`, `npm audit`.
- **Validação real**, porque o padrão não aceita "deve funcionar": medição no
  workspace real antes da troca de versão da API; conector no claude.ai web e no
  celular por OAuth e por chave; Claude Code por header; AI Core e Editor rodando;
  `pipx upgrade` e a ponte 0.5.0 → 0.5.1 → 0.6.0 exercitados.

---

## 8. Etapas

Cada etapa tem branch, plano de implementação e gate próprios. O `main` continua
publicável o tempo todo: pacotes e binários atuais seguem funcionando até o corte da
etapa 4. **A entrega só termina quando as quatro forem aceitas.**

| # | Branch / repositório | Entrega | Critério de aceite |
| --- | --- | --- | --- |
| 1 | `refactor/monolito` (hub) | histórico importado, layout por camadas, pacote único com lockfile, `start_app.py`, `scripts/`, CI em matriz, docs; repositório renomeado | todas as suítes verdes no layout novo; `notion-tasks` idêntico ao retrato |
| 2 | `feat/paridade-mcp` | `Contexto` explícito, registro, MCP/CLI/REST gerados, data sources 2025-09-03, funções do AI Core e do blog, conversor único | teste de paridade; retratos da CLI e do MCP; medição no workspace real |
| 3 | `feat/mcp-hospedado` | contas, OAuth próprio, Notion OAuth e chave colada, chaves pessoais, repasse, ASGI, Railway staging/prod, privacidade/termos | claude.ai web e celular por OAuth e por chave; Claude Code por header; testes de isolamento verdes |
| 4 | `feat/migracao-consumidores` (`Felixo-AI-Core`, `felixo-blog`) + distribuição | binário embutido no AI Core, Editor via MCP, pacotes 0.6.0 e de transição, Release-ponte, arquivamento | AI Core e Editor operando via monolito nos 3 sistemas; `pipx upgrade` e a ponte validados |

---

## 9. Riscos

| Risco | Cobertura |
| --- | --- |
| Tamanho do escopo (o maior) | quatro etapas com gate próprio e um plano por etapa |
| Versão nova da API do Notion muda formatos | caracterização e medição real antes da troca |
| Abuso de servidor aberto e custo no Railway | limites por conta e por IP; monitoramento |
| Responsabilidade por tokens de terceiros | cifragem, dados mínimos, repasse sem gravação, política de privacidade |
| Excesso de ferramentas no contexto do modelo | conjuntos `essencial`/`completo` e orçamento medido em teste |
| APIs de auth do SDK MCP evoluem | versão pinada e testes de conformidade OAuth |
| Vários agentes no AI Core | scratchpad do canvas e branch própria |
| Campos do formulário da integração pública desconhecidos | conferência na tela, como ação do mantenedor |

---

## 10. Fontes

- Repositórios lidos em 07/10/2026: hub, `notion-starter` (`42da753`),
  `notion-tasks-cli` (`73ffcd9`), `notion-workspace-app` (`0e958ba`),
  `Felixo-AI-Core`, `felixo-blog` (`ecef451`), `Felixo-System-Design` (`cc4aae7`).
- `docs/MODULARIZACAO.md`, `docs/DISTRIBUICAO.md`, `IA.md` deste repositório.
- [Notion — Authorization](https://developers.notion.com/docs/authorization)
- [Notion — Create a token](https://developers.notion.com/reference/create-a-token)
- [Claude — Authentication for connectors](https://claude.com/docs/connectors/building/authentication)
- [Claude — Building custom connectors via remote MCP servers](https://support.anthropic.com/en/articles/11503834-building-custom-connectors-via-remote-mcp-servers)
- SDK `mcp` 1.28.0 instalado: `FastMCP.add_tool`, `ToolAnnotations`,
  `mcp.server.auth.provider.OAuthAuthorizationServerProvider`,
  `mcp.server.auth.settings.AuthSettings`.
