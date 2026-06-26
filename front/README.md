# Front React

SPA do Ciclo 2 para operar tarefas do Notion pelo contrato REST em `docs/CONTRATOS.md`.

## Rodar localmente

```bash
cd front
npm install
npm run dev
```

O Vite exige Node 20.19+ ou 22.12+. Ele sobe em `http://localhost:5173` e proxia
`/api` para `http://127.0.0.1:8000`.

O app usa o Notion como fonte de verdade por meio da API Django. Se a API falhar,
o front mostra erro; mock so roda quando voce ativar explicitamente:

```bash
VITE_MOCK_API=true npm run dev
```

## Funcionalidades

- Visualizacoes em grade, lista e kanban.
- Busca, filtros persistentes por status/duracao/area e ordenacao. Os filtros de
  status/duracao/area sao enviados para a API e aplicados no Notion; busca textual
  e ordenacao sao de apresentacao no navegador.
- Modal de criacao/edicao usando `POST /api/tarefas`, `PATCH /api/tarefas/{id}` e
  `GET /api/opcoes`.
- Estados de carregamento, vazio e erro com feedback acessivel.
