# Distribuição da CLI única

> **Estado em 2026-09-08:** a versão `0.3.0` está publicada no PyPI. Este é o
> contrato atual para usar, desenvolver e verificar a distribuição sem exigir
> clone, Git ou Node na máquina de quem usa o produto.

## Instalação do usuário

O nome público da distribuição é `notion-automacoes`. A instalação completa é
uma única linha:

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
upgrade ou desinstalação do pacote. A CLI nunca imprime o token. Para conferir
uma instalação sem chamar operações de escrita:

```bash
notion-automacoes --version
notion-automacoes --help
notion-automacoes doctor
notion-automacoes auth listar
```

## Contrato dos pacotes

Os três projetos usam a versão publicada coerente `0.3.0`:

1. `notion-starter` — biblioteca base publicada primeiro;
2. `notion-workspace-app` — API Django, MCP, launcher e bundle da SPA;
3. `notion-automacoes` — fachada CLI e alias compatível `notion-tasks`.

| Pacote | Papel | Publicação |
| --- | --- | --- |
| `notion-starter` | cliente Notion e serviços compartilhados | [PyPI](https://pypi.org/project/notion-starter/) |
| `notion-automacoes` | CLI única e perfis | [PyPI](https://pypi.org/project/notion-automacoes/) |
| `notion-workspace-app` | app local, API, SPA e MCP | [PyPI](https://pypi.org/project/notion-workspace-app/) |

O CLI depende de `notion-starter>=0.3.0,<0.4.0`, sem `Requires-Dist` apontando
para Git. O app declara runtime em `pyproject.toml`; ferramentas de teste ficam
no extra `dev`. O extra `app` do CLI é opcional para permitir a publicação
sequencial dos pacotes, mas é a instalação recomendada para o produto completo.

## Release Python, binários nativos e smoke

Cada módulo tem um workflow `release.yml` que:

- constrói sdist e wheel;
- valida metadados com `twine check`;
- instala o wheel em Ubuntu, Windows e macOS, nos Python 3.10 e 3.13;
- roda `--version`, `--help`, `doctor` e os imports/entry points pertinentes;
- publica com Trusted Publishing do GitHub Actions, sem token PyPI no repositório.

No app, o job de build roda `npm ci` e `npm run build` antes de `python -m build`.
O resultado entra em `server/static/frontend/` no wheel, mas o artefato gerado
continua ignorado no checkout para não virar fonte paralela.

O primeiro release não inclui binários nativos: o contrato publicado continua
Python 3.10+ com `pipx`/`uv`. A decisão posterior de distribuição já definiu o
contrato do mecanismo nativo abaixo; os binários só entram quando as tasks de
empacotamento PyInstaller e assinatura concluírem seus artefatos.

## Contrato de binários nativos, atualização e rollback

O módulo `notion-tasks-cli` implementa o mecanismo em
`cli/atualizacao_nativa.py`, sem alterar o pacote Python `0.3.0`. A Release
estável consulta a API de Releases do GitHub e só considera o alvo detectado
na máquina:

| Alvo | Asset do executável | Asset do checksum |
| --- | --- | --- |
| Windows x64 | `notion-automacoes-windows-x64.exe` | `notion-automacoes-windows-x64.exe.sha256` |
| macOS Intel | `notion-automacoes-macos-x64` | `notion-automacoes-macos-x64.sha256` |
| macOS Apple Silicon | `notion-automacoes-macos-arm64` | `notion-automacoes-macos-arm64.sha256` |
| Linux x64 | `notion-automacoes-linux-x64` | `notion-automacoes-linux-x64.sha256` |

O updater rejeita tags inválidas, drafts e pré-releases, exige o par de assets
do alvo, baixa para o mesmo diretório do executável e confere SHA-256 antes de
qualquer troca. Em macOS/Linux a troca usa `os.replace` e guarda a versão
anterior em `<executável>.previous`, restaurando-a se a operação falhar. No
Windows, onde o executável em uso fica bloqueado, um processo filho espera o
processo pai terminar, faz a mesma troca e relança os argumentos originais.

Em um binário PyInstaller, comandos normais verificam a Release
automaticamente (no máximo uma vez por 24 horas, com cache local). A opção
`NOTION_AUTOMACOES_NO_UPDATE=1` desabilita a verificação automática. O comando
`notion-automacoes update --dry-run` mostra o plano sem baixar; em uma instalação
Python, `update` mantém o comportamento compatível de apenas sugerir o comando
`pipx`, `uv` ou `pip`.

O rollback de produto é deliberadamente manual: cada publicação deve manter no
GitHub pelo menos as duas Releases estáveis mais recentes com seus quatro pares
de assets. Para reverter, escolha a Release anterior, baixe o asset do sistema,
confira a assinatura e o `.sha256`, encerre o programa e substitua o executável
pela versão escolhida. O updater automático nunca faz downgrade; o backup
`.previous` é uma recuperação local adicional, não substitui a Release
anterior.

Os binários nativos ainda não foram publicados nesta versão. A aceitação física
da matriz Windows/macOS Intel/macOS ARM/Linux — incluindo assinatura, execução
do helper Windows e rollback de uma Release real — depende das tasks irmãs de
PyInstaller e assinatura e permanece explicitamente pendente.

## Empacotamento PyInstaller e publicação controlada

O workflow `native-release.yml` do `notion-tasks-cli` constrói os quatro assets
com os nomes estáveis acima, gera um `.sha256` irmão e roda um smoke diretamente
no executável. O builder recebe a tag (`v0.4.0` ou posterior), portanto a versão
embutida no binário não depende do fallback da instalação Python.

O workflow publica os binários primeiro como artefatos da execução. A anexação à
GitHub Release ocorre apenas por `workflow_dispatch`, com `publicar_release=true`
e aprovação do ambiente protegido `native-release`. Essa barreira é intencional:
o processo de assinatura Windows Authenticode e macOS notarization deve concluir
antes da aprovação. A task de empacotamento não altera a Release `0.3.0`.

Para quem usa, a instalação nativa será: baixar o asset da sua plataforma na
Release estável, validar a assinatura e o `.sha256`, conceder permissão de
execução no macOS/Linux quando necessário e colocar o executável no `PATH`. O
binário roda sem Python instalado; o smoke do workflow executa a própria cópia
produzida, mas a aceitação final em máquinas limpas/VMs por plataforma continua
pendente até haver os assets assinados.

## Evidências da publicação

Os workflows de release foram executados a partir da tag `v0.3.0` e passaram nos
três repositórios:

- [`notion-starter` — release 0.3.0](https://github.com/Felipe-Alcantara/notion-starter/actions/runs/33908422673)
- [`notion-workspace-app` — release 0.3.0](https://github.com/Felipe-Alcantara/notion-workspace-app/actions/runs/33908594676)
- [`notion-tasks-cli` — release 0.3.0](https://github.com/Felipe-Alcantara/notion-tasks-cli/actions/runs/33908824167)

Cada workflow constrói wheel e sdist, executa `twine check`, faz smoke em
Ubuntu, Windows e macOS com Python 3.10 e 3.13 e publica via Trusted Publishing.
No app, a SPA é compilada antes do empacotamento e o wheel a serve sem
Node/npm.

## Titularidade e limites

Os metadados dos três pacotes e os respectivos arquivos `LICENSE` identificam
`Felipe Alcantara` como titular. Colaboradores podem contribuir com código e
documentação sem alterar essa titularidade. O primeiro release é Python puro;
binários nativos continuam fora do contrato até uma decisão própria sobre
assinatura, atualização, rollback e manutenção.

## Desenvolvimento

Para alterar o código, use o hub e seus clones de desenvolvimento:

```bash
python bootstrap.py
python check-dev.py
```

Depois, edite o módulo correspondente, rode o gate local dele e faça commit/push
no repositório do módulo. O fluxo detalhado está em [`AGENTS.md`](../AGENTS.md) e
em [`docs/QUALIDADE.md`](QUALIDADE.md).
