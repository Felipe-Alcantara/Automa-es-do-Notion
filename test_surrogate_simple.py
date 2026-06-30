import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from notion_starter.utils import has_invalid_surrogates, safe_json_dumps, sanitize_text
import json

# Teste simples do utilitário
def run_tests():
    print("1. Testando detecao de surrogates invalidos...")

    # Testar has_invalid_surrogates
    # NOTA: \\ud800 em string literal não é um surrogate real, é uma sequência de 6 caracteres
    surrogate_real = "texto com " + chr(0xD800)  # Este é um surrogate real

    test_cases = [
        ("texto normal", False),
        (surrogate_real, True),  # Com surrogate real
        ("texto com \\ud800", False),  # Esta é apenas a string literal "\\ud800"
        ("texto normal com acentos", False),
    ]

    all_passed = True
    for text, expected in test_cases:
        result = has_invalid_surrogates(text)
        if result == expected:
            print(f"  OK: {repr(text)[:20]}")
        else:
            print(f"  ERRO: {repr(text)[:20]} -> esperado: {expected}, obtido: {result}")
            all_passed = False

    print("\n2. Testando safe_json_dumps...")
    # Usar surrogate real
    problem_data = {"text": "conteudo com " + chr(0xD800) + " problema"}
    try:
        result = safe_json_dumps(problem_data, ensure_ascii=False)
        print(f"  OK: Funcionou com {len(result)} caracteres")

        # Verificar se pode ser codificado para UTF-8
        result.encode('utf-8')
        print("  OK: Codificacao UTF-8 funciona")
    except Exception as e:
        print(f"  ERRO: {e}")
        all_passed = False

    print("\n3. Testando sanitize_text...")
    problematic = "texto com " + chr(0xD800) + " surrogate"
    sanitized = sanitize_text(problematic)
    if not has_invalid_surrogates(sanitized):
        print(f"  OK: Texto sanitizado: {repr(sanitized)[:40]}")
    else:
        print(f"  ERRO: Texto ainda invalido")
        all_passed = False

    print("\n" + "="*50)
    if all_passed:
        print("SUCESSO: Todos os testes passaram!")
        print("Agora o sistema previne erro 'invalid high surrogate in string'")
    else:
        print("ALGUNS TESTES FALHARAM")

    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)