#!/usr/bin/env python3
"""
Script de análise de dependências para modularização do Automações do Notion.
Analisa imports entre módulos para propor separação limpa.
"""

import ast
from collections import defaultdict
from pathlib import Path


def extrair_imports(arquivo: Path) -> dict:
    """Extrai todos os imports de um arquivo Python."""
    imports = {
        'stdlib': set(),
        'third_party': set(),
        'local': set(),
        'relative': set()
    }

    try:
        with open(arquivo, encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if mod.startswith('.'):
                        imports['relative'].add(mod)
                    else:
                        categorizar_import(mod, imports)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if module.startswith('.'):
                    imports['relative'].add(module)
                else:
                    categorizar_import(module, imports)

    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  Erro parse {arquivo}: {e}")

    return imports

def categorizar_import(module: str, imports: dict):
    """Categoriza import como stdlib, third_party ou local."""
    # Primeira parte do módulo
    first_part = module.split('.')[0]

    # Módulos locais do projeto

    if module.startswith(('src.', 'notion_starter', 'server.', 'cli.')):
        imports['local'].add(module)
    elif first_part in {'os', 'sys', 'json', 'typing', 'pathlib', 'datetime',
                        'collections', 'itertools', 'functools', 're'}:
        imports['stdlib'].add(module)
    else:
        imports['third_party'].add(module)

def analisar_dependencias(diretorio: Path):
    """Analisa dependências em todos os arquivos Python do diretório."""
    resultados = {
        'arquivos': 0,
        'deps_python': defaultdict(set),
        'deps_django': defaultdict(set),
        'deps_externas': defaultdict(set)
    }

    for arquivo in diretorio.rglob("*.py"):
        if 'test_' in arquivo.name or '__pycache__' in str(arquivo):
            continue

        rel_path = arquivo.relative_to(diretorio)
        print(f"  Analisando: {rel_path}")

        imports = extrair_imports(arquivo)

        # Contar dependências por tipo
        resultados['arquivos'] += 1

        # Python puro (sem Django ou server)
        if any(d.startswith('src.notion_starter') or
               d.startswith('notion_starter') for d in imports['local']):
            resultados['deps_python']['notion_starter'].add(str(rel_path))

        # Django específico
        if any('django' in d for d in imports['third_party']):
            resultados['deps_django']['django'].add(str(rel_path))

        # Outras dependências externas
        for dep in imports['third_party']:
            if dep not in {'django', 'requests', 'mcp'}:
                resultados['deps_externas'][dep].add(str(rel_path))

    return resultados

def main():
    raiz = Path(__file__).parent

    print("=== ANÁLISE DE DEPENDÊNCIAS PARA MODULARIZAÇÃO ===")
    print(f"Diretório: {raiz}")

    # Analisar cada módulo separadamente
    modulo1 = raiz / "src" / "notion_starter"
    modulo2 = raiz / "server"
    modulo3 = raiz / "cli"
    modulo4 = raiz / "front"

    print("\n1. MÓDULO CORE (notion_starter):")
    if modulo1.exists():
        deps1 = analisar_dependencias(modulo1)
        print(f"   Arquivos: {deps1['arquivos']}")
        print(f"   Dependências Python: {len(deps1['deps_python'])}")
        print(f"   Dependências Django: {len(deps1['deps_django'])}")
        print(f"   Dependências externas: {len(deps1['deps_externas'])}")

    print("\n2. MÓDULO SERVIDOR (server):")
    if modulo2.exists():
        deps2 = analisar_dependencias(modulo2)
        print(f"   Arquivos: {deps2['arquivos']}")
        print(f"   Dependências Python: {len(deps2['deps_python'])}")
        print(f"   Dependências Django: {len(deps2['deps_django'])}")
        print(f"   Dependências externas: {len(deps2['deps_externas'])}")
        if deps2['deps_django']:
            print(f"   - Django usado em: {list(deps2['deps_django']['django'])[:5]}")

    print("\n3. MÓDULO CLI (cli):")
    if modulo3.exists():
        deps3 = analisar_dependencias(modulo3)
        print(f"   Arquivos: {deps3['arquivos']}")
        print(f"   Dependências Python: {len(deps3['deps_python'])}")
        print(f"   Dependências Django: {len(deps3['deps_django'])}")
        print(f"   Dependências externas: {len(deps3['deps_externas'])}")

    # Frontend tem análise diferente
    print("\n4. MÓDULO FRONTEND (front):")
    if modulo4.exists():
        arquivos_front = list(modulo4.rglob("*"))
        python_files = [f for f in arquivos_front if f.suffix == '.py']
        js_files = [f for f in arquivos_front if f.suffix in {'.js', '.jsx', '.ts', '.tsx'}]

        print(f"   Total arquivos: {len(arquivos_front)}")
        print(f"   Arquivos Python: {len(python_files)}")
        print(f"   Arquivos JS/TS: {len(js_files)}")

        # Verificar package.json
        package_json = modulo4 / "package.json"
        if package_json.exists():
            import json
            with open(package_json) as f:
                package = json.load(f)
            deps = package.get('dependencies', {})
            dev_deps = package.get('devDependencies', {})
            print(f"   Dependências npm: {len(deps)}")
            print(f"   Dev dependências: {len(dev_deps)}")

    print("\n=== PROPOSTA DE SEPARAÇÃO ===")

    print("\nMODULO 1: notion-starter-python")
    print("  Conteúdo: src/notion_starter/")
    print("  Dependências: requests, typing_extensions (Python < 3.11)")
    print("  Testes: tests/test_*.py (exceto Django/MCP)")
    print("  Saída: PyPI package 'notion-starter'")

    print("\nMODULO 2: notion-django-server")
    print("  Conteúdo: server/ (exceto mcp_server.py)")
    print("  Dependências: Django, notion-starter (como dep externa)")
    print("  Testes: tests Django específicos")
    print("  Saída: Standalone Django app")

    print("\nMODULO 3: notion-mcp-server")
    print("  Conteúdo: server/mcp_server.py + CLI MCP related")
    print("  Dependências: mcp, notion-starter")
    print("  Saída: MCP server standalone")

    print("\nMODULO 4: notion-react-ui")
    print("  Conteúdo: front/")
    print("  Dependências: React, Vite, Tailwind")
    print("  Saída: SPA standalone")

    print("\nMODULO 5: notion-cli-tools")
    print("  Conteúdo: cli/, examples/, scripts/, start_app.py")
    print("  Dependências: notion-starter, rich, questionary")
    print("  Saída: CLI package global")

    print("\n=== ESTRATÉGIA DE MIGRAÇÃO ===")
    print("1. Extrair notion-starter para repo próprio")
    print("2. Configurar como dependência nos outros módulos")
    print("3. Separar Django como app independente")
    print("4. CLI pode referenciar ambas dependências")
    print("5. Frontend mantém contrato de API estável")

if __name__ == "__main__":
    main()