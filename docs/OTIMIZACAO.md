# ⚡ Otimização — latência e custo

> **O que é**: como deixar o sistema mais rápido e mais barato. Os dois custos dominantes
> são as **chamadas ao Notion** (limitadas por rate limit) e as **chamadas de IA**
> (lentas e cobradas). Quase toda otimização aqui é "chamar menos e chamar melhor".

> Veja também: [ESCALA.md](ESCALA.md) (volume) e [SAAS.md](SAAS.md) (economia de produto).

---

## 📋 Índice

- [🎯 Princípio geral](#-princípio-geral)
- [🗂️ Otimizar as chamadas ao Notion](#️-otimizar-as-chamadas-ao-notion)
- [🤖 Otimizar o custo de IA](#-otimizar-o-custo-de-ia)
- [🧊 Cache em camadas](#-cache-em-camadas)
- [♻️ Idempotência e reprocessamento](#️-idempotência-e-reprocessamento)
- [✅ Lista de verificação](#-lista-de-verificação)

---

## 🎯 Princípio geral

Não otimize no escuro. **Meça primeiro**: descubra qual passo domina a latência e o custo
(quase sempre é a IA, seguida das chamadas ao Notion) e ataque esse. Microotimização de
código que não está no caminho quente é esforço desperdiçado.

---

## 🗂️ Otimizar as chamadas ao Notion

O Notion tem rate limit, então cada chamada conta:

- **Pagine sob demanda** — só busque todas as páginas quando realmente precisar de todas.
  Para a tela inicial, a primeira página costuma bastar.
- **Filtre no servidor do Notion** — peça já filtrado (por status, por data) em vez de
  trazer tudo e filtrar localmente. Menos dados, menos páginas.
- **Não releia o que não mudou** — guarde resultados estáveis (schema de um database,
  opções de um select) em cache; eles mudam raramente.
- **Agrupe quando der** — evite N chamadas quando uma consulta filtrada resolve.
- **Respeite o rate limit** — retry com backoff e tratamento de 429 (Fase 1 do
  [PLANO.md](PLANO.md)) evitam tomar bloqueio por insistência.

---

## 🤖 Otimizar o custo de IA

A IA é o passo mais caro. As maiores economias vêm de **escolher o provedor e o modelo
certos para cada tarefa**:

- **Modelo proporcional à tarefa** — usar um modelo barato para classificar/resumir e
  reservar os caros para o que exige raciocínio. O catálogo do OpenRouter já lista preço
  por modelo, o que ajuda a decidir.
- **Provedor por contexto** — o projeto suporta **dois mundos de IA**:
  - **OpenRouter (pague por uso)** — flexível, multi-modelo, ótimo para volume variável;
  - **Assinaturas / ferramentas próprias** — Codex, Claude Code Pro, Cursor, Gemini CLI,
    Copilot CLI e afins, onde já existe uma assinatura fixa. Apontar para a conta do
    usuário, em vez de gastar tokens cobrados à parte, pode zerar o custo marginal de
    inferência.
  - A camada de IA é **plugável** (ver [PLANO.md](PLANO.md), Fase 5): a escolha do
    provedor fica num lugar só, então dá para rotear cada tarefa para o mais econômico.
- **Mande só o contexto necessário** — prompts enxutos custam menos. Resuma o estado
  antes de enviar, em vez de despejar páginas inteiras.
- **Reaproveite resultados** — resumos e priorizações que não mudaram não precisam ser
  recalculados; guarde-os.

---

## 🧊 Cache em camadas

O que vale a pena guardar, e por quanto tempo:

| O que | Muda com que frequência | Estratégia |
|---|---|---|
| Schema / opções de um database | raramente | cache longo, invalidar ao detectar mudança |
| Catálogo de modelos do OpenRouter | ~diário | cache com validade (o Openia usa 24h) |
| Lista de tarefas exibida no front | a cada edição | cache curto, invalidar ao escrever |
| Resumos/priorizações de IA | quando a tarefa muda | guardar junto da tarefa, recomputar só no que mudou |

Cache é otimização: a falha em ler/gravar o cache nunca deve quebrar o fluxo principal.

---

## ♻️ Idempotência e reprocessamento

Operações que podem rodar de novo (retry, reprocessamento de um job, webhook) precisam
ser **idempotentes**: repetir não deve criar duplicata nem corromper estado. Isso é
otimização **e** correção — evita o custo de limpar bagunça depois. A validação de schema
antes de escrever e um identificador estável por item ajudam a manter a escrita segura
sob repetição.

---

## ✅ Lista de verificação

Antes de dizer que "está otimizado":

- [ ] O passo dominante de custo/latência foi **medido**, não chutado.
- [ ] As chamadas ao Notion paginam sob demanda e filtram no servidor.
- [ ] O modelo de IA é proporcional à dificuldade da tarefa.
- [ ] Há um caminho para usar **assinaturas** quando fizer sentido, não só pague-por-uso.
- [ ] O que muda raramente está em cache, com invalidação clara.
- [ ] Escritas reprocessáveis são idempotentes.
- [ ] Nenhuma "otimização" piorou a clareza do código sem ganho medido.
