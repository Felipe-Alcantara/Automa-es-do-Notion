# Sincronização dos módulos

Use `python sync.py` (ou o alias `sync`) para atualizar os módulos locais com as últimas mudanças do GitHub.

## Uso rápido

```bash
python sync.py
```

Isso:
1. Executa `python bootstrap.py` — faz `git pull --ff-only` em cada módulo
2. Executa `python check-dev.py` — valida se o workspace está OK

Saída: 0 (tudo OK) ou 1 (algo falta/falhou).

## Alias (opcional)

Se quiser abreviar para apenas `sync`, configure **uma vez** no seu shell:

### Windows — PowerShell

Abra seu perfil:

```powershell
notepad $PROFILE
```

Adicione:

```powershell
function sync { python "E:\Programação\Github\Automa-es-do-Notion\sync.py" }
```

Salve. Na próxima sessão do PowerShell:

```powershell
sync
```

### macOS / Linux — Bash/Zsh

Adicione ao `~/.bashrc` ou `~/.zshrc`:

```bash
alias sync="python /path/to/Automa-es-do-Notion/sync.py"
```

Recarregue:

```bash
source ~/.bashrc
# ou
source ~/.zshrc
```

Depois:

```bash
sync
```

## O que ele sincroniza?

Os três módulos em `modules/`:
- notion-starter
- notion-tasks-cli
- notion-workspace-app

Se algum tem commits novos no GitHub, `git pull --ff-only` traz para seu PC.
