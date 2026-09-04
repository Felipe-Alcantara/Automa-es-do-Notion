# Distribuição da CLI única

Este documento descreve a distribuição planejada do ecossistema sem exigir clone,
Git ou Node na máquina de quem usa o produto.

## Instalação do usuário

O nome técnico candidato para a distribuição é `notion-automacoes`. A publicação
no PyPI só deve ser feita depois da confirmação do nome disponível, ownership e
metadados legais.

Quando essa confirmação estiver registrada, a instalação completa será uma única
linha:

```bash
pipx install "notion-automacoes[app]"
# ou
uv tool install "notion-automacoes[app]"
```

O extra `app` instala Django, MCP e a aplicação local; a SPA React já vem
compilada dentro do wheel Python. Portanto, o usuário não precisa de checkout,
`pip install` de URL Git, `npm`, `node` ou `--break-system-packages`.

Verificação inicial, sem token:

```bash
notion-automacoes --version
notion-automacoes doctor
```

Configuração e uso:

```bash
notion-automacoes auth adicionar pessoal --token ntn_... --database <id> --ativar
notion-automacoes tasks listar
notion-automacoes app start
notion-automacoes mcp start
notion-automacoes update
```

O comando histórico continua válido:

```bash
notion-tasks listar
```

Perfis ficam na pasta de configuração do usuário e não são removidos por
upgrade/uninstall do pacote. A CLI nunca imprime o token.

## Contrato dos pacotes

Os três projetos usam a versão coerente `0.3.0`:

1. `notion-starter` — biblioteca base publicada primeiro;
2. `notion-workspace-app` — API Django, MCP, launcher e bundle da SPA;
3. `notion-automacoes` — fachada CLI e alias compatível `notion-tasks`.

O CLI depende de `notion-starter>=0.3.0,<0.4.0`, sem `Requires-Dist` apontando
para Git. O app declara runtime em `pyproject.toml`; ferramentas de teste ficam
no extra `dev`. O extra `app` do CLI é opcional para permitir a publicação
sequencial dos pacotes, mas é a instalação recomendada para o produto completo.

## Release e smoke

Cada módulo tem um workflow `release.yml` que:

- constrói sdist e wheel;
- valida metadados com `twine check`;
- instala o wheel em Ubuntu, Windows e macOS, nos Python 3.10 e 3.13;
- roda `--version`, `--help`, `doctor` e os imports/entry points pertinentes;
- publica com Trusted Publishing do GitHub Actions, sem token PyPI no repositório.

No app, o job de build roda `npm ci` e `npm run build` antes de `python -m build`.
O resultado entra em `server/static/frontend/` no wheel, mas o artefato gerado
continua ignorado no checkout para não virar fonte paralela.

O primeiro release não inclui binários nativos: o contrato é Python 3.10+ com
`pipx`/`uv`. Binários só entram após uma decisão separada que defina plataformas,
assinatura, tamanho, política de update, rollback e manutenção.

## Estado desta entrega

O empacotamento, a fachada, os smoke tests e os workflows foram preparados e
validados localmente. A publicação efetiva permanece pendente da confirmação
irreversível de nome/ownership/metadados legais e da configuração de Trusted
Publishing nos três projetos.
