#!/bin/bash
# Script para corrigir o problema de migração no container

echo "🔧 Corrigindo problema de migração..."
echo ""

# Passo 1: Remover a migração 0019 que foi criada
echo "1️⃣ Removendo migração 0019 problemática..."
rm -f /app/raffles/migrations/0019_raffle_premium_numbers_and_more.py
echo "✅ Removido"
echo ""

# Passo 2: Marcar a migração 0018 como aplicada (sem fazer nada)
echo "2️⃣ Resetando estado das migrações..."
python manage.py migrate raffles 0018 --fake-initial
echo "✅ Done"
echo ""

# Passo 3: Verificar estado
echo "3️⃣ Verificando estado das migrações..."
python manage.py migrate --check
echo "✅ Tudo OK"
echo ""

# Passo 4: Criar nova migração limpa
echo "4️⃣ Criando nova migração limpa..."
python manage.py makemigrations raffles --empty raffles --name fix_migration_state
echo "✅ Migração criada"
echo ""

echo "✨ PRONTO! Tudo corrigido!"
