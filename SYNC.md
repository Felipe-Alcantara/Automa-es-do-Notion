# Sincronização dos módulos

Use `sync` (alias/script) para atualizar os módulos locais com as últimas mudanças do GitHub.

## Instalação (escolha uma opção)

### Windows — PowerShell

Adicione ao seu perfil do PowerShell (`$PROFILE`):

```powershell
# Abra o arquivo:
notepad $PROFILE

# Adicione esta linha:
function sync { & "E:\Programação\Github\Automa-es-do-Notion\sync.ps1" }

# Salve. Próxima vez que abrir PowerShell, o comando 'sync' está disponível.
```

Ou rode manualmente:

```powershell
E:\Programação\Github\Automa-es-do-Notion\sync.ps1
```

### macOS / Linux — Bash/Zsh

Adicione ao seu `~/.bashrc` ou `~/.zshrc`:

```bash
alias sync="cd /path/to/Automa-es-do-Notion && bash sync.sh"
```

Depois recarregue:

```bash
source ~/.bashrc
# ou
source ~/.zshrc
```

## Uso

```bash
sync
```

Isso:
1. Roda `python bootstrap.py` (clona ou faz `git pull` em cada módulo)
2. Roda `python check-dev.py` (valida se tudo está OK)
3. Mostra o status final

## O que ele sincroniza?

Os três módulos em `modules/`:
- notion-starter
- notion-tasks-cli
- notion-workspace-app

Se algum deles tem commits novos no GitHub, `git pull --ff-only` traz para seu PC.
