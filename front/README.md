# Front React

SPA do Ciclo 2 para operar tarefas do Notion pelo contrato REST em `docs/CONTRATOS.md`.

## Rodar localmente

```bash
cd front
npm install
npm run dev
```

O Vite sobe em `http://localhost:5173` e proxia `/api` para `http://127.0.0.1:8000`.

Enquanto a API v2 da Frente A nao estiver completa, o front usa mock automaticamente
quando o backend falha ou uma rota do contrato ainda nao existe. Para forcar o mock:

```bash
VITE_MOCK_API=true npm run dev
```

## Funcionalidades

- Visualizacoes em grade, lista e kanban.
- Busca, filtros persistentes por status/duracao/area e ordenacao.
- Modal de criacao/edicao usando `POST /api/tarefas`, `PATCH /api/tarefas/{id}` e
  `GET /api/opcoes`.
- Estados de carregamento, vazio e erro com feedback acessivel.
