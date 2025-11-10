#!/bin/bash

# Script para configurar database Evolution no PostgreSQL existente

echo "================================"
echo "Setup Evolution API Database"
echo "================================"
echo ""

# Carregar variáveis do .env se existir
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Extrair informações de DATABASE_URL
if [ ! -z "$DATABASE_URL" ]; then
    echo "📦 DATABASE_URL encontrado: $DATABASE_URL"

    # Parse DATABASE_URL (formato: postgres://user:pass@host:port/dbname)
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

    echo ""
    echo "📊 Configurações detectadas:"
    echo "   Host: $DB_HOST"
    echo "   Port: $DB_PORT"
    echo "   User: $DB_USER"
    echo ""
else
    echo "⚠️  DATABASE_URL não encontrado no .env"
    echo ""
    echo "Por favor, informe as credenciais do PostgreSQL:"
    read -p "Host (localhost): " DB_HOST
    DB_HOST=${DB_HOST:-localhost}

    read -p "Port (5432): " DB_PORT
    DB_PORT=${DB_PORT:-5432}

    read -p "User (postgres): " DB_USER
    DB_USER=${DB_USER:-postgres}

    read -sp "Password: " DB_PASS
    echo ""
fi

# Nome do database para Evolution
EVOLUTION_DB="evolution"

echo ""
echo "🔧 Criando database '$EVOLUTION_DB'..."
echo ""

# Tentar criar database
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $EVOLUTION_DB;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database 'evolution' criado com sucesso!"
else
    echo "⚠️  Database 'evolution' já existe ou erro ao criar."
    echo "   (Isso é normal se já foi criado antes)"
fi

# Verificar se foi criado
echo ""
echo "🔍 Verificando databases existentes..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "\l" | grep evolution

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database 'evolution' está disponível!"

    # Gerar string de conexão para Evolution API
    CONNECTION_STRING="postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$EVOLUTION_DB"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📝 String de conexão para Evolution API:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "DATABASE_CONNECTION_URI=$CONNECTION_STRING"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ Use essa string no docker-compose.evolution.yml"
    echo "   ou no .env da Evolution API"
    echo ""
else
    echo ""
    echo "❌ Erro: Database 'evolution' não foi encontrado"
    echo "   Verifique as credenciais e tente novamente"
    exit 1
fi

# Verificar Redis
echo ""
echo "🔍 Verificando Redis..."
redis-cli ping > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Redis está rodando!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📝 String de conexão Redis para Evolution API:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "REDIS_URI=redis://localhost:6379/2"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "ℹ️  Usando DB 2 do Redis (seu Django usa 0 e 1)"
    echo ""
else
    echo "⚠️  Redis não está rodando ou não está acessível"
    echo "   Inicie o Redis antes de continuar"
fi

# Gerar API Key
echo ""
echo "🔐 Gerando API Key para Evolution API..."
API_KEY=$(openssl rand -hex 32)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 API Key gerada:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "AUTHENTICATION_API_KEY=$API_KEY"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Use essa chave tanto na Evolution API"
echo "   quanto no .env do Django (EVOLUTION_API_KEY)"
echo ""

# Resumo final
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 RESUMO - Configurações Evolution API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "PostgreSQL:"
echo "  DATABASE_CONNECTION_URI=$CONNECTION_STRING"
echo ""
echo "Redis:"
echo "  REDIS_URI=redis://localhost:6379/2"
echo ""
echo "Autenticação:"
echo "  AUTHENTICATION_API_KEY=$API_KEY"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Próximos passos:"
echo ""
echo "1. Configure essas variáveis no docker-compose.evolution.yml"
echo "   ou no .env da Evolution API"
echo ""
echo "2. No .env do Django, adicione:"
echo "   EVOLUTION_API_KEY=$API_KEY"
echo ""
echo "3. Inicie a Evolution API:"
echo "   docker-compose -f docker-compose.evolution.yml up -d"
echo ""
echo "4. Ou se instalação manual:"
echo "   cd /path/to/evolution-api && npm run start:prod"
echo ""
echo "✅ Setup concluído!"
echo ""
