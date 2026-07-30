# 🐙 Database GITHUB — importar e manter seus repositórios no Notion

> **O que é**: guia de uso do recurso que sincroniza os seus repositórios do
> GitHub para uma database do Notion — uma página por repositório, com
> propriedades ricas e o README numa subpágina. Cobre a carga inicial e a
> atualização recorrente (repos novos, propriedades mudadas, README alterado).

Este recurso **já existe** no ecossistema, exposto pela CLI `notion-tasks`. Não é
preciso desenvolver nada para usá-lo. O código vive em `notion-tasks-cli`
(`services/inventario_github.py` + `integrations/github.py`); veja o roteamento no
[`AGENTS.md`](../AGENTS.md).

## O que a sincronização faz

Para cada repositório das contas informadas, faz **upsert** (cria ou atualiza) uma
página na database, casando por **URL** (então renomear o repo não duplica):

- **Propriedades**: nome, conta, descrição, URL, homepage, linguagem, tópicos,
  licença, estrelas, forks, issues abertas, tamanho, flags (privado/fork/arquivado)
  e datas (criado, atualizado, último push).
- **README**: exportado como Markdown → blocos numa **subpágina `README`** dentro
  da página do repositório (mantém a linha da database limpa). Só é reescrito
  quando o conteúdo muda, detectado por um **hash** gravado na própria página —
  execuções repetidas não duplicam nem reescrevem à toa.

Erros por repositório não interrompem os demais: são acumulados e reportados no fim.

## Uso rápido

Pré-requisitos no ambiente ou `.env`: `NOTION_TOKEN` e o ID da database GITHUB
(`NOTION_DATABASE_ID` ou `--database`). Opcional: `GITHUB_CONTAS` (CSV) para não
repetir `--contas`.

```bash
# Sincronizar (repos novos + propriedades + README mudado)
notion-tasks atualizar-github --contas minha-conta,outra-conta

# Vários perfis de uma vez — aceita login, @handle ou URL do perfil
notion-tasks atualizar-github --contas https://github.com/conta-um,outra-conta

# Um repositório específico, sem importar a conta inteira — aceita "owner/repo"
# ou a URL completa do repositório
notion-tasks atualizar-github --contas dono/projeto
notion-tasks atualizar-github --contas https://github.com/dono/projeto

# Usando GITHUB_CONTAS e NOTION_DATABASE_ID do .env
notion-tasks atualizar-github

# Só as propriedades, sem mexer nas subpáginas README (mais rápido)
notion-tasks atualizar-github --sem-readme

# Manter só os repositórios ativos (ignora os arquivados no GitHub)
notion-tasks atualizar-github --sem-arquivados

# Incremental: pula os que não mudaram desde o último sync (updated_at)
notion-tasks atualizar-github --apenas-mudancas

# Apontar a database explicitamente
notion-tasks atualizar-github --database <database_id>
```

As flags combinam. O resumo reporta **criados / atualizados / pulados / READMEs /
erros**, então dá para ver quanto o modo incremental economizou.

### Vários perfis de uma vez, com verificação de duplicatas

Passe vários perfis em `--contas` (CSV) — cada um pode ser o login (`conta-um`),
`@conta-um`, a URL do perfil (`https://github.com/conta-um`) **ou um repositório
específico** (`dono/projeto` / `https://github.com/dono/projeto`). A distinção é
automática: uma entrada com `owner/repo` traz só aquele repositório (via
`GitHubClient.detalhar_repo`), sem listar o resto da conta — útil quando você só
quer inventariar um projeto pontual de outra pessoa/organização. A sincronização:

- **Não duplica**: repositórios são casados por URL; um repo que apareça em mais de
  uma conta, listado avulso ou que já exista na database, vira *upsert* (atualiza,
  não cria linha nova).
- **É resiliente por conta**: se um perfil falhar (não existe, rate limit), os
  outros continuam e o erro entra no resumo.
- **Inclui privados** do usuário autenticado quando há `GITHUB_TOKEN` cujo login
  bate com a conta consultada.

Pelo menu, é a opção **Usar o Notion (CLI) → atualizar-github** em
`python start_app.py`, que pergunta as contas e usa o `.env`.

A saída é um resumo: repositórios encontrados, páginas criadas/atualizadas, READMEs
escritos/atualizados e erros. Rode com `--json` para consumir o envelope estável.

## Rotina de atualização

O comando é **idempotente**: rode sempre que quiser trazer repositórios novos e
refletir mudanças. Não precisa limpar a database antes. Para automatizar, agende o
comando (cron/Agendador de Tarefas) apontando para as suas contas.

## Perguntas comuns

- **Já tenho a database populada** — o comando reusa: casa por URL, atualiza as
  existentes e adiciona só o que falta.
- **Faltou a coluna de hash do README** — databases criados antes desse recurso não
  a têm; o comando **cria a coluna automaticamente** na primeira sincronização com
  README.
- **Quero criar a database do zero** — a estrutura (schema) está em
  `services.inventario_github.construir_schema` / `garantir_database`. Hoje a
  criação é chamada via serviço; expor isso num subcomando da CLI é uma boa
  contribuição (veja o `IA.md`).

## Referências

- [`AGENTS.md`](../AGENTS.md) — roteamento (o comando vive em `notion-tasks-cli`).
- `notion-tasks guia` — guia de todos os comandos, escrito para IAs e humanos.
