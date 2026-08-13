# Padrão de relatórios — hora e duração são obrigatórias

Database de referência: [Relatórios](https://app.notion.com/p/Relat-rios-32591f95497e812bb975d9f8c8999dcc?source=copy_link)
(propriedade **Data**, uma página por dia, corpo idempotente por data — ver
[`relatorios_diarios.py`](../modules/notion-starter/src/notion_starter/services/relatorios_diarios.py)).

## A regra

Toda entrada registrada em um relatório (propriedade "O que fiz" ou corpo da
página) deve indicar **a hora**, não só o dia — e, quando o trabalho tiver mais
de um commit associado, **a duração** entre o primeiro e o último.

Isso não é estético: relatórios que só dizem "dia X" escondem se uma tarefa
levou 10 minutos ou a tarde inteira, e esse dado é o que torna o relatório útil
para medir esforço depois. O padrão nasceu observando que os agentes mais
cuidadosos já faziam isso manualmente (ex.: "Commit automático do Fetch All das
08:36") — a mudança é parar de depender de um agente lembrar, e tornar isso a
saída padrão de quem gera o relatório a partir do git.

## Como aplicar

- **Relatório construído a partir de commits** (o caso comum): use
  `notion_starter.git_historico`. `DiaDeTrabalho.duracao_por_extenso()` calcula
  a duração entre o primeiro e o último commit do dia (`"1h35"` ou `"35 min"`,
  vazio se houver só um commit) e `resumo_markdown()` já inclui hora e duração
  na linha de resumo:

  ```text
  2 commits, das 09:00 às 14:30 (duração: 5h30).
  ```

  Não reescreva esse cálculo à mão em outro lugar — se um novo caso de uso
  precisar do número puro, use `dia.duracao_minutos`.

- **Entrada escrita por um agente sem commits associados** (trabalho manual,
  investigação, decisão): registre pelo menos a hora de início e de término
  (`"14:10–14:45"`), no mesmo estilo. Sem commits não há como automatizar, mas
  o formato continua o mesmo — hora sempre, duração quando souber.

## Checklist antes de publicar um relatório

- [ ] A entrada tem hora, não só data?
- [ ] Se houve mais de um commit/etapa, a duração aparece?
- [ ] O formato segue `HH:MM` e `Xh MM` / `MM min` (não "de manhã", "~2 horas")?
