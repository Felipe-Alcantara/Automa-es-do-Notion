# 📈 Escala — crescer sem quebrar

> **O que é**: como o projeto aguenta mais volume — mais tarefas, mais fontes de dados,
> mais agentes trabalhando ao mesmo tempo — sem deformar o núcleo nem martelar as APIs
> externas. Foca nos gargalos reais (Notion e IA são serviços de terceiros com limites)
> e em quando vale a pena adicionar cada peça.

> Veja também: [OTIMIZACAO.md](OTIMIZACAO.md) (custo/latência) e [SAAS.md](SAAS.md)
> (crescer em número de contas).

---

## 📋 Índice

- [🔭 Onde estão os gargalos](#-onde-estão-os-gargalos)
- [🧮 Estado operacional e fila de jobs](#-estado-operacional-e-fila-de-jobs)
- [👷 Workers e concorrência de agentes](#-workers-e-concorrência-de-agentes)
- [🗃️ Quando trocar SQLite por Postgres](#️-quando-trocar-sqlite-por-postgres)
- [📡 Observabilidade mínima](#-observabilidade-mínima)
- [🧗 Curva de escala](#-curva-de-escala)

---

## 🔭 Onde estão os gargalos

O projeto não é CPU-bound; ele **espera serviços externos**. Os gargalos reais:

- **API do Notion** — tem rate limit. Muitas leituras/escritas em paralelo esbarram nele.
- **IA (OpenRouter / assinaturas)** — latência e custo por chamada; é o passo mais lento
  e mais caro do fluxo.
- **Coordenação de agentes** — vários agentes mexendo nos mesmos recursos pedem
  controle de concorrência (quem está trabalhando no quê).

Escalar bem é, sobretudo, **não bater nesses limites à toa** e **não deixar dois agentes
brigarem pelo mesmo recurso**.

---

## 🧮 Estado operacional e fila de jobs

O Notion é a fonte da verdade do **conteúdo**, mas não é um bom lugar para guardar
**estado operacional** (quem está processando o quê, locks, tentativas). Para isso, o
servidor tem um banco próprio:

- **Fila de jobs** — tarefas a processar pelos agentes, com status (pendente, rodando,
  concluído, falhou).
- **Locks / idempotência** — garantir que um mesmo job não seja processado duas vezes
  por dois agentes.
- **Logs de execução** — o que cada agente fez, para auditoria e retomada.

Isso mantém o Notion limpo (só o resultado final) e evita martelar a API dele a cada
mudança de estado interno.

---

## 👷 Workers e concorrência de agentes

Conforme os agentes entram (Fase 6 do [PLANO.md](PLANO.md)), o trabalho vira assíncrono:

- **Comece simples** — processamento em background dentro do próprio servidor resolve
  bem para um único usuário.
- **Cresça para workers** — uma fila com workers separados quando houver muitos jobs
  simultâneos ou tarefas longas (um agente escrevendo um artigo demora).
- **Controle de concorrência** — um job por recurso por vez; o lock no estado
  operacional evita dois agentes editando a mesma página/tarefa.

A regra do padrão vale: só extraia workers/fila separados quando houver **necessidade
real**, não por antecipação.

---

## 🗃️ Quando trocar SQLite por Postgres

O projeto começa com **SQLite** — certo para um sistema local/pessoal de baixa
concorrência. Sinais de que chegou a hora do **Postgres**:

- vários workers escrevendo ao mesmo tempo (SQLite trava em escrita concorrente);
- múltiplas contas/usuários (cenário SaaS);
- volume de jobs/logs que pesa numa base de arquivo único;
- necessidade de operação mais robusta (réplicas, backups gerenciados).

Enquanto nenhum desses aperta, SQLite é mais simples e mais do que suficiente.

---

## 📡 Observabilidade mínima

Para crescer com segurança, é preciso enxergar o que acontece:

- **Logs úteis e neutros** — claros, sem expor segredos, que ajudem qualquer pessoa a
  entender uma falha.
- **Falhas de integração rastreáveis** — deixar evidente quando o erro veio do Notion,
  da IA ou do próprio servidor.
- **Métricas básicas** — quantos jobs por minuto, taxa de erro, latência das chamadas
  externas. Tracing entra quando o volume justificar.

---

## 🧗 Curva de escala

```text
1 usuário, poucos jobs     →  servidor único + SQLite + background simples
muitos jobs / tarefas longas →  fila + workers, locks no estado operacional
múltiplas contas           →  Postgres, isolamento por conta (ver SAAS.md)
muitos agentes em paralelo  →  controle de concorrência forte + observabilidade
```

Cada degrau adiciona uma peça **só quando a anterior aperta**. Escalar não é montar tudo
de uma vez — é remover o gargalo que dói agora.
