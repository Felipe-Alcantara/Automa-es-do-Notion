import os
import sys
from pathlib import Path

import requests

# Buscar configuração
raiz = Path(__file__).parent.parent
env_file = raiz / ".env"

print(f"Carregando .env de: {env_file}")

# Carregar .env manualmente
if env_file.exists():
    with open(env_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value

# Obter variáveis
token = os.environ.get('NOTION_TOKEN')
database_id = os.environ.get('NOTION_DATABASE_ID')

print(f"\nToken (início): {token[:10]}..." if token else "Token: NÃO ENCONTRADO")
print(f"Database ID: {database_id}")

# Teste 1: Verificar se o token funciona (users/me)
def test_token():
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28'
    }
    try:
        response = requests.get('https://api.notion.com/v1/users/me', headers=headers, timeout=10)
        print("\nTeste 1 - users/me:")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Usuário: {data.get('name', 'N/A')}")
            print(f"  Tipo: {data.get('type', 'N/A')}")
            return True
        else:
            print(f"  Erro: {response.text}")
            return False
    except Exception as e:
        print(f"  Exceção: {e}")
        return False

# Teste 2: Verificar acesso ao database (leitura)
def test_database_read():
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28'
    }
    try:
        response = requests.get(
            f'https://api.notion.com/v1/databases/{database_id}',
            headers=headers,
            timeout=10
        )
        print("\nTeste 2 - get database:")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            titulo = ''
            if 'title' in data and isinstance(data['title'], list):
                titulo = ''.join([t.get('plain_text', '') for t in data['title']])
            print(f"  Título: {titulo}")
            print(f"  URL: {data.get('url', 'N/A')}")
            return True
        else:
            print(f"  Erro: {response.text}")
            return False
    except Exception as e:
        print(f"  Exceção: {e}")
        return False

# Teste 3: Tentar criar página (escrita)
def test_database_write():
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Tarefa": {
                "title": [
                    {
                        "text": {"content": "Teste de criação via API direta"}
                    }
                ]
            },
            "Etapa": {
                "status": {"name": "Entrada"}
            }
        }
    }

    try:
        response = requests.post('https://api.notion.com/v1/pages',
                                headers=headers,
                                json=payload,
                                timeout=10)
        print("\nTeste 3 - criar página:")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Sucesso! ID: {data.get('id', 'N/A')}")
            return True, data.get('id')
        else:
            print(f"  Erro: {response.text}")
            return False, None
    except Exception as e:
        print(f"  Exceção: {e}")
        return False, None

# Teste 4: Verificar se database está compartilhada
def test_database_query():
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    payload = {"page_size": 1}

    try:
        response = requests.post(f'https://api.notion.com/v1/databases/{database_id}/query',
                                headers=headers,
                                json=payload,
                                timeout=10)
        print("\nTeste 4 - query database:")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Resultados: {len(data.get('results', []))}")
            return True
        else:
            print(f"  Erro: {response.text}")
            return False
    except Exception as e:
        print(f"  Exceção: {e}")
        return False

# Teste 5: Verificar permissões do token
def test_token_capabilities():
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28'
    }
    try:
        response = requests.get('https://api.notion.com/v1/users', headers=headers, timeout=10)
        print("\nTeste 5 - listar usuários (perm):")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  Token tem acesso à API (básico)")
            return True
        else:
            print(f"  Erro: {response.text}")
            return False
    except Exception as e:
        print(f"  Exceção: {e}")
        return False

if __name__ == "__main__":
    if not token:
        print("ERRO: Token não encontrado!")
        sys.exit(1)

    if not database_id:
        print("AVISO: Database ID não encontrado, testando apenas token")

    print("\n" + "="*60)
    print("DIAGNÓSTICO DA CONEXÃO NOTION")
    print("="*60)

    # Executar testes
    token_ok = test_token()

    if database_id:
        db_readable = test_database_read()
        db_queryable = test_database_query()

        if db_readable:
            writable, created_id = test_database_write()
        else:
            writable = False
            created_id = None
            print("\nDatabase não legível, pulando teste de escrita")
    else:
        db_readable = db_queryable = writable = False
        created_id = None

    token_caps = test_token_capabilities()

    print("\n" + "="*60)
    print("RESUMO DO DIAGNÓSTICO")
    print("="*60)
    print(f"✅ Token válido: {'SIM' if token_ok else 'NÃO'}")
    print(f"✅ Database legível: {'SIM' if db_readable else 'NÃO'}")
    print(f"✅ Database consultável: {'SIM' if db_queryable else 'NÃO'}")
    print(f"✅ Escrita permitida: {'SIM' if writable else 'NÃO'}")
    print(f"✅ Permissões do token: {'OK' if token_caps else 'LIMITADO'}")

    if created_id:
        print(f"\n📝 Página criada com ID: {created_id}")

    # Recomendações
    print("\n" + "="*60)
    print("RECOMENDAÇÕES")
    print("="*60)

    if db_readable and not writable:
        print("⚠️  Database está legível mas não permite escrita.")
        print("   Possíveis causas:")
        print("   1. Database não compartilhada com a integração")
        print("   2. Permissões da integração são somente leitura")
        print("   3. Database está em workspace diferente")
        print("\n   SOLUÇÃO:")
        print("   - Acesse o Notion")
        print("   - Abra a database")
        print("   - Clique em ••• → Conexões")
        print("   - Adicione a integração 'Automações do Notion'")
        print("   - Garanta permissão de 'Edição' (não só 'Visualização')")

    elif not db_readable:
        print("❌ Database não acessível.")
        print("   Possíveis causas:")
        print("   1. Database ID incorreto")
        print("   2. Database não compartilhada")
        print("   3. Token sem acesso ao workspace")

    elif writable:
        print("✅ Tudo funcionando! O CLI deveria funcionar.")
        print("   O problema pode estar no código do CLI.")

    print("\nPróximos passos:")
    print("1. Verificar compartilhamento da database")
    print("2. Testar com outra database (backup)")
    print("3. Verificar logs detalhados do CLI")