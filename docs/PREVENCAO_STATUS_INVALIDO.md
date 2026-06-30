# Prevenção de Status Inválido - Documentação do Problema Resolvido

## 🐛 Problema Original

**Data**: 2026-06-30  
**Problema**: CLI falhava com erro genérico "Falha ao falar com o Notion" quando tentava usar status que não existe no schema do database.

**Erro específico da API**:
```json
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "Invalid status option. Status option \"Em andamento\" does not exist."
}
```

## 🔍 Causa Raiz

O CLI não validava status contra as opções disponíveis no database antes de enviar para a API do Notion. Quando um status inválido era usado:

1. CLI enviava status inválido
2. API do Notion rejeitava com erro 400
3. CLI capturava erro mas mostrava mensagem genérica
4. Usuário ficava sem saber o real problema

## 🛠️ Solução Implementada

### 1. **Validação Prévia no CLI**
Adicionamos validação em todas as funções que aceitam status:

```python
def cmd_criar(args: argparse.Namespace, *, tasklist_factory: TaskListFactory) -> Any:
    """Cria uma tarefa nova.

    IMPORTANTE: Valida status contra opções disponíveis no database para evitar
    erro "Invalid status option" da API do Notion.

    Problema conhecido: CLI falhava com status inválido que não existe no schema.
    Solução: Validar status contra opções do database antes de enviar.
    """
    # Validar status contra opções disponíveis (se fornecido)
    status = _normalizar_texto(args.status)
    if status:
        opcoes = svc.listar_opcoes(tasklist=tasklist_factory())
        status_validos = opcoes.get("status", [])
        if status not in status_validos:
            raise CLIError(
                f"Status '{status}' inválido. Opções disponíveis: {', '.join(status_validos)}"
            )
    # ... resto da função
```

### 2. **Funções Afetadas**
- `cmd_criar()` - criação de tarefas
- `cmd_editar()` - edição de tarefas  
- `cmd_mover()` - mudança de status
- `cmd_concluir()` - conclusão de tarefas

### 3. **Mensagens de Erro Melhoradas**
Antes: "Falha ao falar com o Notion" (genérico)  
Depois: "Status 'Em andamento' inválido. Opções disponíveis: Entrada, Assim que possível, Concluída" (específico)

## 🧪 Testes Implementados

### Testes Unitários (`test_cli_status_validation.py`)
- ✅ Validação de status válido
- ✅ Rejeição de status inválido
- ✅ Mensagens de erro específicas
- ✅ Casos de borda (status vazio, case-sensitive)

### Testes de Integração (`test_integration_status_validation.py`)
- ✅ Fluxo completo com serviços mockados
- ✅ Prevenção de chamada à API com status inválido
- ✅ Tratamento de outros erros da API
- ✅ Testes com múltiplos status válidos

## 📊 Comparação Antes/Depois

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Feedback** | Genérico "Falha ao falar com o Notion" | Específico "Status X inválido, opções: A, B, C" |
| **Prevenção** | Erro só ocorria na API | Validação prévia no CLI |
| **Debug** | Difícil identificar problema | Mensagem clara indica solução |
| **UX** | Frustrante para usuário | Guia usuário para correção |

## 🔧 Como Funciona Agora

### Fluxo Corrigido:
1. **Usuário tenta criar tarefa com status inválido**
2. **CLI valida contra opções do database**
3. **Se inválido → Erro específico com opções disponíveis**
4. **Se válido → Prossegue com chamada à API**
5. **Outros erros da API → Tratamento normal**

### Exemplo de Uso:
```bash
# Antes (falhava silenciosamente)
python -m cli --json criar "Tarefa teste" --status "Status Inexistente"
# Erro: "Falha ao falar com o Notion"

# Agora (feedback útil)
python -m cli --json criar "Tarefa teste" --status "Status Inexistente"
# Erro: "Status 'Status Inexistente' inválido. Opções disponíveis: Entrada, Assim que possível, Concluída"
```

## 🚨 Casos Especiais Tratados

### Status `None` ou Vazio
- Não valida quando status não é fornecido
- Permite criação sem status definido

### Case-Sensitive
- Validação é case-sensitive (Notion API é case-sensitive)
- "entrada" ≠ "Entrada"

### Lista de Opções Vazia
- Trata corretamente quando database não tem opções de status
- Mensagem de erro apropriada

## 📈 Benefícios da Solução

1. **Melhor UX**: Usuário sabe exatamente o que corrigir
2. **Menos chamadas à API**: Validação local previne erros 400
3. **Debug mais fácil**: Mensagens específicas ajudam troubleshooting
4. **Código mais robusto**: Validação explícita previne erros silenciosos

## 🔮 Próximas Melhorias Possíveis

1. **Validação de outras propriedades**: `duracao`, `areas`
2. **Cache de opções**: Evitar consultas repetidas ao mesmo database
3. **Validação de schema**: Verificar se database tem as colunas esperadas
4. **Autocomplete**: Sugerir opções válidas no CLI

## 📝 Lições Aprendidas

1. **Validação local > Validação remota**: Sempre validar dados localmente antes de enviar para API
2. **Mensagens específicas > Mensagens genéricas**: Erros devem guiar o usuário para a solução
3. **Testes preventivos**: Implementar testes que detectem regressões
4. **Documentação do problema**: Registrar causas e soluções para evitar repetição

---

**Status**: ✅ **PROBLEMA RESOLVIDO**  
**Data da correção**: 2026-06-30  
**Responsável**: Correção via análise e implementação de validação  
**Testes**: ✅ Cobertura completa com testes unitários e de integração