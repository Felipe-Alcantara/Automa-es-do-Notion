# Análise de Modularização: Automações do Notion

## Contexto do Projeto Atual

O repositório "Automações do Notion" começou como um `notion-starter-boilerplate` e evoluiu para incluir múltiplas responsabilidades:
1. **Core Python** (`src/notion_starter/`) - Cliente Notion tipado com helpers
2. **Servidor Django** (`server/`) - API REST completa com services
3. **SPA React** (`front/`) - Interface web para tarefas e exploração
4. **CLI para IA** (`cli/`) - Interface JSON estável para agentes
5. **Servidor MCP** (`server/mcp_server.py`) - Integração com Felixo-AI-Core
6. **Inventário GitHub** (`server/services/inventario_github.py`) - Sincronização com GitHub

## Problemas Identificados

1. **Acoplamento excessivo**: O cliente Notion básico está acoplado a Django e React
2. **Escopo amplo demais**: Um único repositório tenta servir como boilerplate, app local, ferramenta CLI e servidor MCP
3. **Complexidade de manutenção**: A estrutura `server/` tem todas as camadas (API, services, integrations) que dependem do core
4. **Dificuldade de reuso**: Para usar apenas o cliente Notion, precisa-se do Django e dependências do servidor

## Princípios de Separação (Baseados no Padrão de Qualidade)

- **Bordas finas**: API deve apenas validar HTTP, regra em services
- **Trabalho direto no main**: Por padrão, evitar branches complexos
- **Gate obrigatório antes de entregar**: `quality_check.py` deve passar
- **Documentação viva atualizada no mesmo commit**
- **Não versione segredos, IDs reais ou artefatos locais**

## Proposta de Arquitetura Modular

### Módulo 1: `notion-py-starter` (Biblioteca Core)
**Foco**: Cliente Python puro para API do Notion
**Conteúdo atual**:
- `src/notion_starter/` (client.py, properties.py, content.py, tasks.py, etc.)
- Testes unitários relacionados
- `pyproject.toml` simplificado (só `requests` como dependência)

**Benefícios**:
- Pode ser publicado no PyPI como `notion-starter`
- Reutilizável em outros projetos Python
- Mantém a filosofia atual de "ferramenta antes da solução específica"
- Alinhado com a origem do projeto como boilerplate open-source

### Módulo 2: `notion-api-server` (Servidor Django)
**Foco**: API REST completa com serviços e integrações
**Conteúdo atual**:
- `server/` (Django completo: api/, services/, integrations/, core/)
- MCP server como parte do servidor
- Dependências Django específicas

**Benefícios**:
- Foco claro: servir como backend para frontend e integrações
- Dependências Python otimizadas para servidor
- Pode evoluir independentemente do core
- Mantém a stack Django + SQLite conforme decisões fixadas

### Módulo 3: `notion-tasks-ui` (SPA React)
**Foco**: Interface web para gerenciamento de tarefas
**Conteúdo atual**:
- `front/` (React + Vite + Tailwind)
- Configuração Vite atual
- Assets e componentes específicos

**Benefícios**:
- Frontend independente do backend
- Pode consumir qualquer servidor que siga o contrato da API
- Mais fácil de customizar para diferentes casos de uso
- Mantém o foco na experiência do usuário

### Módulo 4: `notion-cli-tools` (Ferramentas CLI)
**Foco**: CLI para automações e integração com IA
**Conteúdo atual**:
- `cli/` (interface JSON estável)
- `examples/` (scripts executáveis)
- Scripts de qualidade

**Benefícios**:
- Instalação minimalista para automações locais
- Pode virar pacote CLI global (`pip install notion-cli`)
- Mantém a filosofia de "entrada única" via menu (`start_app.py`)
- Integração MCP pode ser módulo opcional

## Organização do Monorepo vs Multi-repo

### Opção A: Monorepo com estrutura clara
```
automações-do-notion/
├── packages/
│   ├── notion-starter/          (Módulo 1)
│   ├── notion-api-server/       (Módulo 2)
│   ├── notion-tasks-ui/         (Módulo 3)
│   └── notion-cli-tools/        (Módulo 4)
├── docs/                        (Documentação unificada)
└── scripts/                     (Scripts de qualidade/CI)
```

### Opção B: Multi-repo independente
- Repo 1: `notion-starter` (PyPI package)
- Repo 2: `notion-api-server` (standalone Django app)
- Repo 3: `notion-tasks-ui` (React SPA)
- Repo 4: `notion-cli` (CLI tools)
- Repo 5: `automações-do-notion` (orquestração/docs)

## Linha do Tempo de Migração

### Fase 1: Extrair o core (2-3 semanas)
1. Criar repo `notion-starter` com conteúdo de `src/notion_starter/`
2. Configurar publicação PyPI
3. Atualizar referências nos outros módulos

### Fase 2: Separar frontend (1-2 semanas)
1. Criar repo `notion-tasks-ui`
2. Configurar proxy de desenvolvimento para API
3. Manter contrato de API estável

### Fase 3: Isolar servidor (2-3 semanas)
1. Criar repo `notion-api-server` 
2. Configurar dependências Django otimizadas
3. Manter integração com core extraído

### Fase 4: CLI como pacote (1 semana)
1. Criar repo `notion-cli-tools`
2. Configurar como pacote instalável
3. Manter compatibilidade com `start_app.py`

## Considerações Técnicas

### Contratos Mantidos
- `docs/CONTRATOS.md`: deve ser o guia entre módulos
- Formato da API REST: mantido entre servidor e frontend
- Objeto `Tarefa`: padrão entre todos os módulos
- Formato de erro unificado

### Dependências
- Core: apenas `requests` (Python 3.10+)
- Servidor: Django 5+, SQLite, extras para MCP/GitHub
- Frontend: React 18+, Vite, Tailwind
- CLI: depende do core, sem Django

### Qualidade por Módulo
Cada módulo deve ter seu próprio gate de qualidade:
- Core: ruff + pytest (migração mantida)
- Servidor: roda migrações Django, testes específicos
- Frontend: lint + build Vite
- CLI: testes de integração

### Integração com Ecossistema Vitis Souls
1. **Core como base**: pode ser usado por outros produtos da Vitis Souls
2. **Servidor como microserviço**: integra com outros serviços
3. **Interface reutilizável**: padrão UI para gestão de conteúdo
4. **CLI como ferramenta interna**: para automações internas

## Benefícios da Separação

### Para Desenvolvimento
- **Maior foco**: cada time ou contribuidor trabalha no seu módulo
- **Builds mais rápidos**: testes e lint específicos por módulo
- **Releases independentes**: versões podem evoluir separadamente
- **Múltiplos mantenedores**: especialização por área

### Para o Usuário Final
- **Instalação leve**: só o necessário para cada caso de uso
- **Menor superfície de ataque**: menos código desnecessário
- **Atualizações mais seguras**: mudanças em um módulo não quebram outros

### Para o Projeto Vitis Souls
- **Componentes reutilizáveis**: cada módulo pode ser usado isoladamente
- **Arquitetura moderna**: alinhada com microserviços e componentes
- **Escalabilidade**: pode adicionar módulos futuros
- **Governança clara**: responsabilidades bem definidas

## Próximos Passos

1. **Criar análise de dependências**: mapear imports entre módulos
2. **Definir interfaces estáveis**: contratos entre módulos
3. **Configurar workspace monorepo**: se for caminho escolhido
4. **Estabelecer CI/CD por módulo**: pipelines independentes
5. **Documentar processo de contribuição**: para cada módulo

## Decisão Recomendada

**Monorepo com estrutura de pacotes** (Opção A) por:
1. Manter histórico Git unificado
2. Facilitar refatoração cruzada
3. Compartilhar configuração de qualidade
4. Manter documentação centralizada
5. Preservar a identidade do projeto

A separação deve preservar a filosofia atual de "entrada única" via `start_app.py`, que pode se tornar um meta-pacote que instala e orquestra os módulos necessários.