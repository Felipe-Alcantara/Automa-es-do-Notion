# 🤝 Contribuindo com o Automações do Notion

Obrigado por querer contribuir! Este projeto reúne automações locais para operar o
Notion com API Django, SPA React, CLI/MCP para IA e integrações como inventário
GitHub. Issues, correções de documentação, novos helpers, exemplos, testes e
melhorias de UX são bem-vindos.

> Contribuições aqui devem preservar os contratos existentes, a documentação viva e o
> gate de qualidade descrito em [`docs/QUALIDADE.md`](docs/QUALIDADE.md).

---

## 📋 Índice

- [Como Contribuir](#-como-contribuir)
- [Ambiente de Desenvolvimento](#-ambiente-de-desenvolvimento)
- [Padrões de Qualidade](#-padrões-de-qualidade)
- [Padrões de Linguagem](#-padrões-de-linguagem-documentação-e-logs)
- [Fluxo de Pull Request](#-fluxo-de-pull-request)
- [Código de Conduta](#-código-de-conduta)

---

## 🚀 Como Contribuir

1. **Faça um fork** do repositório.
2. **Crie uma branch** descritiva (`fix/...`, `feat/...`, `docs/...`).
3. **Faça suas mudanças** seguindo os padrões abaixo.
4. **Rode os testes e o lint** antes de abrir o PR.
5. **Abra um Pull Request** explicando o que mudou e por quê.

Não tem certeza por onde começar? Abra uma issue descrevendo a ideia — a gente
conversa antes de você investir tempo no código.

---

## 🛠️ Ambiente de Desenvolvimento

```bash
# Clone e instale com as dependências de desenvolvimento
git clone https://github.com/Felipe-Alcantara/Automa-es-do-Notion.git
cd Automa-es-do-Notion
pip install -e ".[dev]"

# Rode a suíte de testes (HTTP é mockado — não precisa de token nem rede)
python3 scripts/quality_check.py
```

Requer Python 3.10+. Para validar a SPA, rode também `npm install` dentro de `front/`.
Copie `.env.example` para `.env` apenas se for rodar exemplos contra um workspace real
do Notion — nunca versione o `.env`.

---

## ✅ Padrões de Qualidade

- **Entenda o padrão existente antes de alterar.** O projeto separa core
  (`src/notion_starter`), API (`server/api`), casos de uso (`server/services`),
  integrações (`server/integrations`), CLI/MCP e SPA React. Preserve essas fronteiras.
- **Prefira a solução mais simples** que resolva o problema real, sem adicionar
  dependências ou camadas sem justificativa.
- **Preserve contratos.** API REST, CLI JSON, ferramentas MCP, objetos do core e
  formatos de erro devem permanecer estáveis; mudança quebradora precisa ser explícita
  e documentada.
- **Tipos e validação.** Use tipagem (`TypedDict`/`dataclass`) e valide entradas
  externas, como o restante do código já faz.
- **Não exponha segredos.** Nada de tokens, IDs reais ou URLs privadas no código,
  nos testes ou na documentação.
- **Teste o comportamento.** Bugs corrigidos viram caso de regressão; HTTP é
  sempre mockado com `responses`.
- **Rode o gate completo.** Use `python3 scripts/quality_check.py` antes de abrir PR;
  ele cobre Python e front. Para isolar falhas, use `--python-only` ou `--front-only`.
- **Atualize a documentação viva** (`README.md` e `IA.md`) no mesmo passo quando a
  mudança alterar comportamento, estrutura ou comandos.

---

## ✍️ Padrões de Linguagem (Documentação e Logs)

Como o projeto é open source, documentação e logs são lidos por um público amplo.

- **Escreva para qualquer leitor** — linguagem geral e acessível, sem jargão interno.
- **Sem valores hardcoded** — use placeholders genéricos em vez de caminhos,
  tokens ou IDs reais.
- **Enquadre o trabalho futuro como convite à contribuição** em vez de uma lista
  de tarefas interna.

| ❌ Evite (tom interno) | ✅ Prefira (tom open source) |
|------------------------|------------------------------|
| "Features futuras para implementar" | "Melhorias que o projeto poderia expandir" |
| "TODO: ainda falta fazer" | "Ideias para quem quiser contribuir" |

---

## 🔄 Fluxo de Pull Request

Um bom PR responde claramente:

- **O que mudou?**
- **Por que mudou?**
- **Como foi validado?** (ex.: `python3 scripts/quality_check.py`)
- **Qual risco sobrou?**

Mantenha o PR focado: evite misturar refatoração ampla com novas funcionalidades.
Use commits pequenos no formato `tipo: descrição` (`feat`/`fix`/`docs`/`refactor`/`chore`).

---

## 💬 Código de Conduta

Seja respeitoso e acolhedor. Este é um espaço para aprender e construir juntos —
contribuições de pessoas de todos os níveis de experiência são bem-vindas.

---

⭐ Se este projeto te ajudou, considere deixar uma estrela no GitHub!
