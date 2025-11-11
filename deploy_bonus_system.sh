#!/bin/bash
# Script para fazer deploy do sistema de bônus

echo "🚀 Iniciando deploy do sistema de bônus..."

# 1. Fazer pull do código
echo "📥 Fazendo pull do repositório..."
git pull origin main

# 2. Rodar migrations
echo "🔄 Aplicando migrations..."
python3 manage.py migrate raffles

# 3. Coletar arquivos estáticos (se necessário)
echo "📦 Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput

# 4. Reiniciar servidor (ajuste conforme seu setup)
echo "♻️  Reiniciando servidor..."
# Se usar gunicorn:
# sudo systemctl restart gunicorn
# Se usar supervisor:
# sudo supervisorctl restart rifas

echo "✅ Deploy concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Acesse o admin: https://vip.institutoacender.com.br/admin-login"
echo "2. Edite uma campanha"
echo "3. Procure pelas seções 'Bonus de Compra' e 'Premio Milestone'"
echo "4. Ative os bônus desejados"
