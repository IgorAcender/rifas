#!/bin/bash

# Script para corrigir migration no servidor
# Execute este script no servidor de produção

echo "=== Corrigindo Migrations ==="

# A migration 0019 foi modificada para verificar se campos já existem
# Não precisa mais fazer --fake, só aplicar normalmente

echo "Aplicando migration 0019 (com verificação de campos existentes)..."
python manage.py migrate raffles 0019

echo "=== Migrations corrigidas! ==="
echo "Campo is_test_mode adicionado com sucesso"
echo ""
echo "IMPORTANTE: Faça git pull e reinicie o container:"
echo "  git pull origin main"
echo "  docker-compose restart web"
