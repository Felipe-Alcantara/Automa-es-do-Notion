# Diagnóstico do Problema do CLI Notion (registro histórico)

> Este documento registra o diagnóstico original de 2026-06-30. O problema foi
> corrigido desde então; para a instalação e os comandos atuais, consulte
> [`DISTRIBUICAO.md`](DISTRIBUICAO.md) e o [README da raiz](../README.md).

## 🐛 Problema Identificado

O CLI (`notion-automacoes --json tasks criar`) falhava com "Falha ao falar com o Notion", mas:
- **Leitura funciona**: `listar`, `opcoes`, `databases` funcionam
- **API direta funciona**: Testes com `requests` criam páginas normalmente
- **Services funcionam**: `editar_tarefa()` via código Python funciona

## 🔍 Causa Raiz

### 1. **Validação de Status Inválido**
O erro principal estava em tentar usar status "Em andamento" que **não existe** no schema do database:
```python
# ERRO: Status não existe no database
editar_tarefa(task_id, status="Em andamento")

# CORRETO: Status válido do database
editar_tarefa(task_id, status="Urgente")
```

### 2. **Diagnóstico da API**
O script `scripts/diagnostico_notion.py` confirmou:
- ✅ **Token válido**: Automações do notion (bot)
- ✅ **Database acessível**: "Tarefas — HOME (pessoal)"
- ✅ **Leitura funcionando**: Query retorna resultados
- ✅ **Escrita funcionando**: API direta cria páginas
- ✅ **Permissões OK**: Token tem acesso completo

### 3. **Problema Específico do CLI**
O CLI falha na **validação de entrada** ou na **construção do payload**. A API direta funciona porque:
- Usa status válido do database
- Constrói payload corretamente
- Não passa por validações extras do CLI

## 🛠️ Solução Implementada

### 1. **Atualização da Task Existente**
Usamos o service diretamente para atualizar a task "Separar responsabilidades":
```python
from server.services.tarefas import editar_tarefa

resultado = editar_tarefa(
    "<page_id>",
    nome="Separar responsabilidades - PROPOSTA DE MODULARIZAÇÃO",
    status="Urgente"  # Status válido do database
)
```

### 2. **Adição de Conteúdo via API Direta**
Adicionamos conteúdo técnico completo usando API direta:
```python
import requests

payload = {
    "children": [
        {
            "type": "heading_2",
            "heading_2": {"rich_text": [{"text": {"content": "Análise Técnica Completa"}}]}
        },
        {
            "type": "paragraph", 
            "paragraph": {"rich_text": [{"text": {"content": "conteúdo completo..."}}]}
        }
    ]
}

requests.patch(f"https://api.notion.com/v1/blocks/{task_id}/children", json=payload)
```

## 📋 Status Atual

### ✅ **Concluído**
1. **Diagnóstico completo** da conexão Notion
2. **Task atualizada** com novo nome e status
3. **Conteúdo adicionado** com proposta de modularização
4. **Documentação criada** deste diagnóstico

### ✅ **Resolvido**
1. O CLI valida status contra o schema antes da escrita.
2. As mensagens de erro informam a opção inválida e os valores disponíveis.
3. A prevenção e a regressão estão cobertas pela suíte automatizada do módulo.

## 🔧 Recomendações Técnicas

### Para o CLI
```python
# Antes de criar/editar, validar status
status_validos = obter_opcoes_status()  # Do database
if status not in status_validos:
    raise CLIError(f"Status '{status}' inválido. Use: {', '.join(status_validos)}")
```

### Para o Database
- Manter lista centralizada de status válidos
- Validar entrada contra schema atual
- Melhorar feedback de erro para usuário

## 📊 Resumo Técnico

| Componente | Status | Problema | Solução |
|------------|--------|----------|---------|
| **Token Notion** | ✅ Funciona | - | - |
| **API Direta** | ✅ Funciona | - | - |
| **Services** | ✅ Funciona | Status inválido | Usar status do database |
| **CLI** | ✅ Corrigido | Validação/erro | Validar opções antes da escrita |
| **Database** | ✅ Acessível | - | - |

## 🎯 Próximos Passos

1. Manter a validação alinhada ao schema real do database.
2. Reaplicar o gate do módulo ao alterar a borda da CLI.
3. Usar a distribuição pública `notion-automacoes` nos novos exemplos.

---

**Conclusão**: O problema não era de conexão/permissões, mas de **validação de entrada**. A API funciona perfeitamente quando usada corretamente.
