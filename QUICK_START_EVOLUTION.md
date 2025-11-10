# 🚀 Quick Start - Evolution API

Guia rápido para configurar Evolution API usando seus bancos PostgreSQL e Redis existentes.

## ⚡ 3 Passos Rápidos

### 1️⃣ Prepare o Database

```bash
# Execute o script de setup
./setup_evolution_database.sh
```

Isso vai:
- ✅ Criar database `evolution` no seu PostgreSQL
- ✅ Gerar string de conexão
- ✅ Gerar API Key segura
- ✅ Verificar Redis

**Anote as informações geradas!**

---

### 2️⃣ Configure Docker Compose

Edite o arquivo `docker-compose.evolution.yml` e atualize:

```yaml
environment:
  # Cole a API Key gerada pelo script
  - AUTHENTICATION_API_KEY=cole-a-chave-gerada-aqui

  # Cole a string de conexão PostgreSQL gerada pelo script
  - DATABASE_CONNECTION_URI=postgresql://user:pass@host:5432/evolution

  # Redis já está configurado (DB 2)
  - REDIS_URI=redis://localhost:6379/2
```

**OU** crie um arquivo `.env.evolution`:

```bash
EVOLUTION_API_KEY=sua-chave-gerada
EVOLUTION_DATABASE_URL=postgresql://user:pass@host:5432/evolution
EVOLUTION_REDIS_URL=redis://localhost:6379/2
EVOLUTION_SERVER_URL=http://localhost:8080
```

---

### 3️⃣ Inicie a Evolution API

```bash
# Com Docker Compose
docker-compose -f docker-compose.evolution.yml up -d

# Verificar logs
docker-compose -f docker-compose.evolution.yml logs -f

# Parar
docker-compose -f docker-compose.evolution.yml down
```

---

## 📱 Conectar WhatsApp (após iniciar)

### Criar instância:

```bash
curl -X POST http://localhost:8080/instance/create \
  -H "apikey: SUA-API-KEY-AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "rifas-whatsapp",
    "qrcode": true
  }'
```

### Obter QR Code:

**Opção 1: Via navegador**
```
http://localhost:8080/instance/qrcode/rifas-whatsapp
```

**Opção 2: Via curl**
```bash
curl -X GET http://localhost:8080/instance/connect/rifas-whatsapp \
  -H "apikey: SUA-API-KEY-AQUI"
```

### Escanear QR Code:

1. Abra WhatsApp no celular
2. Aparelhos conectados → Conectar aparelho
3. Escaneie o QR Code

---

## ⚙️ Configurar no Django

Adicione no `.env` do seu projeto Django:

```bash
# Evolution API
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=a-mesma-api-key-da-evolution
EVOLUTION_INSTANCE_NAME=rifas-whatsapp
```

---

## 🧪 Testar

```bash
# No diretório do projeto Django
python test_evolution.py
```

Escolha opção 3 para testar conexão + enviar mensagem.

---

## ✅ Checklist

- [ ] Script `setup_evolution_database.sh` executado
- [ ] Database `evolution` criado
- [ ] API Key gerada e configurada
- [ ] `docker-compose.evolution.yml` configurado
- [ ] Evolution API iniciada (`docker-compose up -d`)
- [ ] Instância `rifas-whatsapp` criada
- [ ] WhatsApp conectado (QR Code escaneado)
- [ ] Variáveis no `.env` do Django configuradas
- [ ] Teste executado com sucesso

---

## 🆘 Problemas Comuns

### Evolution API não inicia

```bash
# Ver logs
docker-compose -f docker-compose.evolution.yml logs -f

# Verificar se porta 8080 está livre
lsof -i :8080
```

### Erro de conexão com PostgreSQL

Verifique se:
- PostgreSQL está rodando
- Database `evolution` existe
- Credenciais estão corretas
- Host/porta estão acessíveis

```bash
# Testar conexão manualmente
psql -h localhost -U seu_usuario -d evolution
```

### Erro de conexão com Redis

```bash
# Testar Redis
redis-cli ping

# Deve retornar: PONG
```

### WhatsApp não conecta

- Aguarde até 30 segundos após gerar QR Code
- Se expirar, gere novo QR Code
- Verifique se WhatsApp está atualizado no celular

---

## 📊 Verificar Status

```bash
# Health check
curl http://localhost:8080/

# Status da instância
curl -X GET http://localhost:8080/instance/connectionState/rifas-whatsapp \
  -H "apikey: SUA-API-KEY"

# Deve retornar: "state": "open"
```

---

## 🔄 Comandos Úteis

```bash
# Reiniciar Evolution API
docker-compose -f docker-compose.evolution.yml restart

# Ver logs em tempo real
docker-compose -f docker-compose.evolution.yml logs -f evolution-api

# Parar Evolution API
docker-compose -f docker-compose.evolution.yml down

# Parar e remover volumes (⚠️ apaga dados!)
docker-compose -f docker-compose.evolution.yml down -v

# Atualizar para versão mais recente
docker-compose -f docker-compose.evolution.yml pull
docker-compose -f docker-compose.evolution.yml up -d
```

---

## 📝 Estrutura de Arquivos

```
/Users/user/Desktop/Programação/rifas/
├── setup_evolution_database.sh      # Script de setup
├── docker-compose.evolution.yml     # Config Docker
├── test_evolution.py                # Teste de integração
├── EVOLUTION_API_INSTALL.md        # Guia completo
├── EVOLUTION_API_SETUP.md          # Guia da API
├── WHATSAPP_NOTIFICATION_GUIDE.md  # Guia de notificações
└── .env                            # Configure aqui (Django)
```

---

## 🎯 Próximo Passo

Depois de tudo configurado e testado:

1. Faça uma compra de teste no seu sistema
2. Pague via PIX
3. Aguarde aprovação do MercadoPago
4. **Mensagem chegará automaticamente no WhatsApp!** 🎉

---

## 📚 Mais Informações

- **Instalação completa**: [EVOLUTION_API_INSTALL.md](EVOLUTION_API_INSTALL.md)
- **Configuração da API**: [EVOLUTION_API_SETUP.md](EVOLUTION_API_SETUP.md)
- **Sistema de notificações**: [WHATSAPP_NOTIFICATION_GUIDE.md](WHATSAPP_NOTIFICATION_GUIDE.md)
- **Documentação oficial**: https://doc.evolution-api.com

---

## 💡 Dica Pro

Para produção, use HTTPS:

1. Configure domínio (ex: `evolution.seusite.com`)
2. Configure SSL/TLS (Let's Encrypt)
3. Use Nginx como reverse proxy
4. Atualize `SERVER_URL` para `https://evolution.seusite.com`

---

**Está tudo pronto para usar!** 🚀
