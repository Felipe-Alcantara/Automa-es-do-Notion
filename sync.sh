#!/bin/bash
# Sincroniza os módulos do ecossistema e verifica o workspace.
# Uso: ./sync.sh

set -e

echo ""
echo "============================================================"
echo "Sincronizando modulos..."
echo "============================================================"

python bootstrap.py

echo ""
echo "============================================================"
echo "Verificando workspace..."
echo "============================================================"

python check-dev.py

echo ""
echo "============================================================"
echo "Tudo sincronizado e pronto!"
echo "============================================================"
