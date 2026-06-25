# 🤖 Camada de IA — OpenRouter e provedores plugáveis

> **O que é**: a camada de inteligência artificial do projeto, plugável por design.
> Suporta dois mundos: **OpenRouter (pague por uso)** e **assinaturas** que a pessoa
> já paga (Codex, Claude Code Pro, Cursor; futuramente Gemini CLI e Copilot CLI).
> Espelha os padrões do [Openia](https://github.com/Felipe-Alcantara/Openia).
>
> **Documento vivo**: evolui junto com `README.md`, `IA.md` e [PLANO.md](PLANO.md)
> (Fase 5). Entregue pelo **Agente 3 (IA / OpenRouter)** na Onda 2.

---

## 📋 Índice

- [Arquitetura](#arquitetura)
- [ProvedorIA — o contrato](#provedoria--o-contrato)
- [ProvedorOpenRouter](#provedoropenrouter)
- [Catálogo de modelos](#catálogo-de-modelos)
- [Caso de uso: NL → tasklist (copiloto)](#caso-de-uso-nl--tasklist-copiloto)
- [Configuração (chaves)](#configuração-chaves)
- [Extensão: adicionando provedores](#extensão-adicionando-provedores)

---

## Arquitetura

```text
┌──────────────────────────────────────────────────────────────┐
│  services/ia.py — caso de uso (NL → AcaoSugerida → execução) │
│  Consome apenas o protocolo ProvedorIA                       │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│  integrations/openrouter.py                                   │
│   • ProvedorIA (protocolo)                                    │
│   • ProvedorOpenRouter (implementação — chat completions)     │
│   • Catálogo de modelos (cache 24h, agrupamento, preço)       │
│   • Chave lida de OPENROUTER_API_KEY (sem segredo no repo)    │
└──────────────────────────────────────────────────────────────┘
```

A fronteira de camadas é respeitada: `services/ia.py` **não conhece HTTP** nem
o OpenRouter — só consome o protocolo `ProvedorIA`. `integrations/openrouter.py`
**não conhece a tasklist** — só entrega texto a partir de um prompt.

---

## ProvedorIA — o contrato

```python
class ProvedorIA(Protocol):
    def completar(self, prompt: str, *, modelo: str | None = None) -> str: ...
```

Qualquer provedor (OpenRouter, assinatura, mock de teste) implementa este
protocolo. A camada de serviço nunca sabe qual provedor está por trás.

---

## ProvedorOpenRouter

Implementação concreta que chama a API de chat completions do OpenRouter
(`/api/v1/chat/completions`). Usa `requests` (consistente com o `NotionClient`).

```python
provedor = ProvedorOpenRouter(modelo_padrao="openai/gpt-4.1-nano")
resposta = provedor.completar("Resuma esta tarefa.", modelo="anthropic/claude-sonnet-4")
```

- `modelo_padrao`: usado quando nenhum modelo é passado na chamada.
- `timeout`: tempo máximo de espera (padrão: 60 s).
- A chave é resolvida de `OPENROUTER_API_KEY` no momento da chamada.

---

## Catálogo de modelos

Espelha o `openia/models.py`: busca, cache e agrupamento por empresa.

```python
from integrations.openrouter import carregar_modelos, empresas, modelos_da_empresa

modelos = carregar_modelos()               # cache 24 h; fallback se sem rede
emps = empresas(modelos)                   # ["anthropic", "google", "openai", ...]
openai = modelos_da_empresa(modelos, "openai")  # ordenados por preço desc
```

- **`Modelo`**: `id`, `empresa`, `nome`, `preco_saida` (USD/token de saída).
- **Cache**: JSON local com TTL de 24 h. Se vencido e sem rede, usa o vencido.
  Falha ao gravar não quebra o fluxo.
- A API pública (`/api/v1/models`) não exige chave para listar.

---

## Caso de uso: NL → tasklist (copiloto)

O primeiro caso de uso da IA: **linguagem natural → operação de tasklist**, no
modo **copiloto que sugere e a pessoa confirma**.

```python
from services.ia import interpretar_comando, executar_acao

# 1. IA interpreta a frase e devolve uma sugestão (sem tocar no Notion)
acao = interpretar_comando("cria uma tarefa pra revisar o artigo amanhã", provedor=provedor)
# → AcaoSugerida(operacao="criar_tarefa", parametros={"nome": "...", "prazo": "..."}, descricao="...")

# 2. A camada que chamou apresenta a sugestão ao usuário para confirmação

# 3. Se confirmado, executa (delega para services.tarefas)
tarefa = executar_acao(acao, tasklist=tasklist)
```

**Operações suportadas**: `listar_tarefas`, `criar_tarefa`, `mover_status`,
`concluir_tarefa`.

**Guarda-corpos**:
- Nenhuma escrita no Notion sem confirmação explícita.
- A IA não acessa o Notion diretamente — apenas interpreta texto.
- O provedor é injetável; testes usam mock, sem rede.

---

## Configuração (chaves)

A chave do OpenRouter é lida exclusivamente de variáveis de ambiente:

```bash
# No .env (já ignorado pelo git) ou exportada no shell
OPENROUTER_API_KEY=sk-or-...
```

Nunca aparece em código, log, repr ou commit. Se o `.env` ainda não foi lido
pelo Django, o adaptador tenta carregá-lo via `core.config.carregar_env_file()`.

---

## Extensão: adicionando provedores

Para adicionar um novo provedor (ex.: modo assinatura), basta implementar
`ProvedorIA`:

```python
class ProvedorAssinatura:
    def completar(self, prompt: str, *, modelo: str | None = None) -> str:
        # delega para a CLI da assinatura (ex.: claude, codex)
        ...
```

Registrar de forma declarativa (Open/Closed): adicionar é registrar mais um,
sem mexer no núcleo. Esse é o mesmo padrão do Openia (`interfaces/registry.py`).

Provedores futuros previstos: Codex (OpenAI), Claude Code Pro (Anthropic),
Cursor, Gemini CLI (Google), Copilot CLI (GitHub).
