# Instalação da Evolution API - Usando seus bancos existentes

## 📦 Seus recursos atuais (que serão compartilhados):

- **PostgreSQL**: Já configurado em `DATABASE_URL`
- **Redis**: Já configurado em `CELERY_BROKER_URL` (redis://localhost:6379/0)

## 🎯 Estratégia: Compartilhar recursos SEM conflito

A Evolution API usará:
- **PostgreSQL**: Mesmo servidor, **database diferente** (`evolution`)
- **Redis**: Mesmo servidor, **database diferente** (db=2)

Assim não há conflito com seu app Django!

## 🚀 Instalação da Evolution API

### Opção 1: Docker Compose (Recomendado)

#### 1. Crie o arquivo `docker-compose.evolution.yml`:

```yaml
version: '3.8'

services:
  evolution-api:
    image: atendai/evolution-api:latest
    container_name: evolution-api
    restart: always
    ports:
      - "8080:8080"  # Porta da Evolution API
    environment:
      # Server Configuration
      - SERVER_URL=https://seu-dominio.com  # URL pública da sua Evolution API
      - SERVER_PORT=8080

      # Authentication
      - AUTHENTICATION_API_KEY=sua-chave-secreta-aqui-minimo-32-caracteres

      # Database - Usando seu PostgreSQL existente
      - DATABASE_ENABLED=true
      - DATABASE_PROVIDER=postgresql
      - DATABASE_CONNECTION_URI=postgresql://user:password@localhost:5432/evolution
      # ⚠️ IMPORTANTE: Substitua user, password, localhost:5432 pelos dados do seu PostgreSQL
      # Mas use um DATABASE diferente (evolution) para não misturar com o Django

      # Redis - Usando seu Redis existente (DB 2)
      - REDIS_ENABLED=true
      - REDIS_URI=redis://localhost:6379/2
      # ⚠️ IMPORTANTE: Note o /2 no final - é um database diferente do seu Django (que usa /0 e /1)

      # WhatsApp Settings
      - QRCODE_COLOR=#198754
      - QRCODE_LIMIT=30

      # Logs
      - LOG_LEVEL=INFO
      - LOG_COLOR=true

      # Webhook
      - WEBHOOK_GLOBAL_ENABLED=false

    volumes:
      - evolution_instances:/evolution/instances
      - evolution_store:/evolution/store

    # Se PostgreSQL e Redis estão em containers, adicione:
    # depends_on:
    #   - postgres
    #   - redis

    # Se PostgreSQL e Redis estão no host, use network_mode
    network_mode: "host"  # Permite acessar localhost do host

volumes:
  evolution_instances:
  evolution_store:
```

#### 2. Configure as variáveis corretas:

Edite o arquivo e substitua:

```yaml
# Exemplo com PostgreSQL local:
DATABASE_CONNECTION_URI=postgresql://seu_usuario:sua_senha@localhost:5432/evolution

# Exemplo com PostgreSQL em container:
DATABASE_CONNECTION_URI=postgresql://postgres:postgres@postgres:5432/evolution

# Redis local (use DB 2 para não conflitar com Django):
REDIS_URI=redis://localhost:6379/2

# Redis em container:
REDIS_URI=redis://redis:6379/2

# API Key (gere uma chave forte):
AUTHENTICATION_API_KEY=gere-uma-chave-forte-aqui-32-chars-min
```

#### 3. Crie o database `evolution` no PostgreSQL:

```bash
# Conecte ao PostgreSQL
psql -U seu_usuario -d postgres

# Crie o database
CREATE DATABASE evolution;

# Verifique
\l

# Sair
\q
```

#### 4. Inicie a Evolution API:

```bash
docker-compose -f docker-compose.evolution.yml up -d
```

#### 5. Verifique se está rodando:

```bash
# Logs
docker-compose -f docker-compose.evolution.yml logs -f

# Status
docker-compose -f docker-compose.evolution.yml ps
```

---

### Opção 2: Instalação Manual (Sem Docker)

#### 1. Instale Node.js (v18 ou superior):

```bash
# Verificar versão
node --version

# Se não tiver, instale:
# macOS:
brew install node

# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 2. Clone a Evolution API:

```bash
cd /Users/user/Desktop/Programação/
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api
```

#### 3. Instale dependências:

```bash
npm install
```

#### 4. Configure variáveis de ambiente:

Crie o arquivo `.env`:

```bash
# Server
SERVER_URL=http://localhost:8080
SERVER_PORT=8080

# Authentication
AUTHENTICATION_API_KEY=sua-chave-secreta-aqui-minimo-32-caracteres

# Database - Compartilhando PostgreSQL
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://seu_usuario:sua_senha@localhost:5432/evolution

# Redis - Compartilhando Redis (DB 2)
REDIS_ENABLED=true
REDIS_URI=redis://localhost:6379/2

# WhatsApp
QRCODE_COLOR=#198754
QRCODE_LIMIT=30

# Logs
LOG_LEVEL=INFO
LOG_COLOR=true
```

#### 5. Crie o database no PostgreSQL:

```bash
psql -U seu_usuario -d postgres -c "CREATE DATABASE evolution;"
```

#### 6. Inicie a Evolution API:

```bash
npm run start:prod
```

---

## 🔧 Configuração no seu App Django

Depois que a Evolution API estiver rodando, configure no `.env` do Django:

```bash
# Evolution API
EVOLUTION_API_URL=http://localhost:8080  # ou https://seu-dominio.com em produção
EVOLUTION_API_KEY=a-mesma-chave-que-voce-configurou-na-evolution
EVOLUTION_INSTANCE_NAME=rifas-whatsapp
```

---

## 📱 Conectar WhatsApp à Evolution API

### 1. Criar instância:

```bash
curl -X POST http://localhost:8080/instance/create \
  -H "apikey: sua-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "rifas-whatsapp",
    "qrcode": true
  }'
```

### 2. Conectar WhatsApp (obter QR Code):

```bash
curl -X GET http://localhost:8080/instance/connect/rifas-whatsapp \
  -H "apikey: sua-api-key"
```

Isso retornará um QR Code em Base64. Cole no navegador:

```
data:image/png;base64,[COLE_O_CODIGO_AQUI]
```

Ou acesse via navegador:
```
http://localhost:8080/instance/qrcode/rifas-whatsapp
```

### 3. Escaneie o QR Code com WhatsApp:

1. Abra WhatsApp no celular
2. Vá em **Aparelhos conectados**
3. Toque em **Conectar um aparelho**
4. Escaneie o QR Code

---

## 🗄️ Estrutura dos Databases

Seu setup ficará assim:

```
PostgreSQL Server (mesma instância)
├── seu_database_django      → Usado pelo Django (tabelas de rifas, users, etc)
└── evolution                 → Usado pela Evolution API (tabelas de WhatsApp)

Redis Server (mesma instância)
├── DB 0 → Celery Broker (Django)
├── DB 1 → Celery Results (Django)
└── DB 2 → Evolution API (cache e sessões)
```

**Benefícios:**
- ✅ Zero conflito entre os sistemas
- ✅ Usa mesmos recursos (economiza $$$)
- ✅ Fácil backup (mesmo PostgreSQL)
- ✅ Mesma infraestrutura

---

## 🔍 Verificar se está funcionando

### 1. Health Check:

```bash
curl http://localhost:8080/
```

Deve retornar informações da API.

### 2. Verificar instância:

```bash
curl -X GET http://localhost:8080/instance/connectionState/rifas-whatsapp \
  -H "apikey: sua-api-key"
```

Deve retornar `"state": "open"` se conectado.

### 3. Testar envio de mensagem:

```bash
curl -X POST http://localhost:8080/message/sendText/rifas-whatsapp \
  -H "apikey: sua-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "text": "Teste Evolution API!"
  }'
```

---

## 🔐 Segurança em Produção

### 1. Use HTTPS:

Configure um reverse proxy (Nginx) para Evolution API:

```nginx
server {
    listen 443 ssl;
    server_name evolution.seu-dominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Gere API Key forte:

```bash
# Gerar chave aleatória de 32 caracteres
openssl rand -hex 32
```

Use essa chave em `AUTHENTICATION_API_KEY` e `EVOLUTION_API_KEY`.

---

## 📊 Monitoramento

### Verificar uso do PostgreSQL:

```sql
-- Conectar ao database evolution
\c evolution

-- Ver tabelas criadas pela Evolution
\dt

-- Ver tamanho do database
SELECT pg_size_pretty(pg_database_size('evolution'));
```

### Verificar uso do Redis:

```bash
redis-cli

# Selecionar DB 2 (Evolution)
SELECT 2

# Ver chaves
KEYS *

# Info
INFO keyspace
```

---

## 🚨 Troubleshooting

### Evolution API não conecta ao PostgreSQL:

```bash
# Verifique se PostgreSQL aceita conexões
psql -U seu_usuario -d evolution

# Se erro de conexão, edite pg_hba.conf:
# Adicione: host    all    all    127.0.0.1/32    md5
```

### Evolution API não conecta ao Redis:

```bash
# Teste conexão Redis
redis-cli ping

# Deve retornar PONG

# Verifique se Redis permite conexões
# Em redis.conf: bind 127.0.0.1 ::1
```

### Porta 8080 já em uso:

```bash
# Verificar o que está usando a porta
lsof -i :8080

# Ou use outra porta na Evolution API
# Altere SERVER_PORT no .env
```

---

## 💡 Exemplo Completo - Docker Compose com Rede

Se quiser Evolution API + PostgreSQL + Redis tudo no Docker:

```yaml
version: '3.8'

services:
  evolution-api:
    image: atendai/evolution-api:latest
    container_name: evolution-api
    restart: always
    ports:
      - "8080:8080"
    environment:
      - SERVER_URL=https://seu-dominio.com
      - SERVER_PORT=8080
      - AUTHENTICATION_API_KEY=sua-chave-secreta
      - DATABASE_ENABLED=true
      - DATABASE_PROVIDER=postgresql
      - DATABASE_CONNECTION_URI=postgresql://postgres:postgres@postgres:5432/evolution
      - REDIS_ENABLED=true
      - REDIS_URI=redis://redis:6379/2
      - LOG_LEVEL=INFO
    volumes:
      - evolution_instances:/evolution/instances
      - evolution_store:/evolution/store
    depends_on:
      - postgres
      - redis
    networks:
      - evolution-network

  postgres:
    image: postgres:15-alpine
    container_name: postgres
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=evolution
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - evolution-network

  redis:
    image: redis:7-alpine
    container_name: redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - evolution-network

volumes:
  evolution_instances:
  evolution_store:
  postgres_data:
  redis_data:

networks:
  evolution-network:
    driver: bridge
```

Neste caso, seu Django também precisa se conectar ao PostgreSQL e Redis via `localhost:5432` e `localhost:6379`.

---

## ✅ Checklist Final

- [ ] PostgreSQL rodando e acessível
- [ ] Database `evolution` criado
- [ ] Redis rodando e acessível
- [ ] Evolution API instalada (Docker ou Manual)
- [ ] API Key configurada
- [ ] Evolution API iniciada
- [ ] Instância criada (`rifas-whatsapp`)
- [ ] WhatsApp conectado (QR Code escaneado)
- [ ] Variáveis configuradas no Django `.env`
- [ ] Teste de envio funcionando
- [ ] Mensagem recebida no WhatsApp

## 🎉 Pronto!

Agora você tem:
- **Django App** → PostgreSQL DB (seu_database) + Redis DB 0 e 1
- **Evolution API** → PostgreSQL DB (evolution) + Redis DB 2

Tudo compartilhado, sem conflitos! 🚀
