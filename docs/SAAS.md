# 💼 De projeto pessoal a SaaS

> **O que é**: um exercício de "e se" — o que mudaria para este projeto virar um produto
> que outras pessoas usam. Hoje ele é de **uso pessoal** (single-user), porém
> **hospedado num servidor**. Esta página mapeia o salto de "meu Notion do meu jeito"
> para "um serviço com várias contas", sem fingir que é trivial.

> Veja também: [ESCALA.md](ESCALA.md) (crescer em volume) e [PLANO.md](PLANO.md)
> (a decisão de alcance está lá: pessoal, hospedado, sem multiusuário por ora).

---

## 📋 Índice

- [⚖️ O ponto de partida honesto](#️-o-ponto-de-partida-honesto)
- [🧱 O que precisa mudar](#-o-que-precisa-mudar)
- [🔐 Modelo de conexão com o Notion](#-modelo-de-conexão-com-o-notion)
- [💳 Modelos de cobrança](#-modelos-de-cobrança)
- [🤖 Custo de IA e assinaturas](#-custo-de-ia-e-assinaturas)
- [🚦 Caminho gradual](#-caminho-gradual)

---

## ⚖️ O ponto de partida honesto

O projeto foi desenhado para **uma pessoa**. Isso é uma vantagem: sem multiusuário, sem
isolamento de dados entre contas, sem cobrança — a complexidade fica baixa e o foco
continua no valor. Virar SaaS **não é o objetivo declarado**; é um caminho possível,
documentado aqui para quem quiser explorar.

A boa notícia: a arquitetura por camadas (cliente isolado, casos de uso finos,
integrações encapsuladas) é exatamente a base que torna esse salto viável sem reescrever
o núcleo.

---

## 🧱 O que precisa mudar

Os pontos que um produto multiusuário exige e que hoje, por ser pessoal, não existem:

| Área | Hoje (pessoal) | SaaS (multiusuário) |
|---|---|---|
| **Identidade** | sem login | contas, autenticação, sessão |
| **Isolamento** | um workspace | dados isolados por conta (multi-tenant) |
| **Segredos** | um token no `.env` | token de cada usuário guardado com segurança, por conta |
| **Autorização** | tudo é seu | escopo/permissão por usuário e por recurso |
| **Cobrança** | nenhuma | planos, limites, faturamento |
| **Operação** | um servidor simples | observabilidade, backups, suporte, SLA |

Cada linha dessa tabela é uma decisão de produto, não só técnica.

---

## 🔐 Modelo de conexão com o Notion

Num produto, cada usuário precisa conectar **o próprio Notion**. Dois caminhos:

- **Token de integração por usuário** — cada pessoa cria a própria integração e cola o
  token. Simples, mas transfere fricção para o usuário (criar integração, compartilhar
  páginas).
- **OAuth público do Notion** — o usuário autoriza o app com alguns cliques; o app
  recebe e guarda o token de acesso. Bem mais amigável, porém exige cadastrar a
  integração pública e tratar refresh/expiração.

Em qualquer caso, a regra do projeto continua valendo, agora por conta: **segredo nunca
no repositório nem em log**, guardado de forma segura e isolado por usuário.

---

## 💳 Modelos de cobrança

Esboços possíveis, do mais simples ao mais elaborado:

- **Grátis com limites** — número de tarefas/sincronizações por mês; bom para entrada.
- **Assinatura por plano** — mensal/anual, com limites maiores e mais fontes de dados.
- **Cobrança por uso** — repassa o custo real (chamadas de IA, sincronizações), útil
  quando o uso varia muito entre usuários.
- **Traga sua própria chave** — o usuário usa a própria conta de IA; você cobra só pela
  plataforma. Reduz seu risco de custo (ver próxima seção).

---

## 🤖 Custo de IA e assinaturas

A camada de IA não precisa ser só "pague por token no OpenRouter". O projeto prevê
**múltiplos modos de provedor**, e isso muda a economia do SaaS:

- **OpenRouter (pague por uso)** — flexível, multi-modelo; o custo escala com o uso.
- **Assinaturas / ferramentas próprias** — Codex, Claude Code Pro, Cursor e afins.
  Aqui o usuário já paga uma assinatura fixa; o produto apenas **aponta para a conta
  dele**, em vez de consumir tokens cobrados de você.

Para um SaaS, isso abre o modelo **"traga sua própria assinatura/chave"**: o usuário
liga a conta que já tem (OpenRouter, Claude Code Pro, Cursor…), e o seu serviço cobra
pela plataforma, não pela inferência. Reduz drasticamente o risco de custo variável e
respeita quem já paga por uma ferramenta. O detalhe de como cada provedor é selecionado
está em [PLANO.md](PLANO.md) (camada de IA) e em [OTIMIZACAO.md](OTIMIZACAO.md) (custo).

---

## 🚦 Caminho gradual

Nada disso precisa acontecer de uma vez. Uma ordem segura:

```text
1. Pessoal hospedado        →  estado atual previsto (uma conta, um servidor)
2. Multiconta interno       →  poucas contas confiáveis, sem cobrança
3. Conexão self-service     →  OAuth do Notion, cada um liga o próprio workspace
4. Limites e planos         →  cobrança simples, "traga sua própria IA"
5. Operação de produto      →  observabilidade, backups, suporte
```

A regra de ouro do padrão de qualidade vale o tempo todo: **não melhorar uma parte
piorando arquitetura, segurança ou previsibilidade**. Cada degrau só compensa quando o
anterior estiver sólido.
