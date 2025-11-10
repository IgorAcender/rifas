# 🚀 Configuração Evolution API no EasyPanel

## 📋 Suas Credenciais

### PostgreSQL (Compartilhado)
```
Host: acender-sorteios_acender-sorteios-postgres
Port: 5432
User: postgres
Password: e4e276191bf0755e8dec
Database Django: acender-sorteios
Database Evolution: evolution (criar novo)
```

### Redis (Compartilhado)
```
Host: acender-sorteios_acender-sorteios-redis
Port: 6379
Password: d0c0fc91e51e233d29e9
DB Django (Broker): 0
DB Django (Results): 1
DB Evolution: 2 (sem conflito)
```

---

## 🔧 Passo a Passo no EasyPanel

### 1️⃣ Criar Database "evolution" no PostgreSQL

Acesse o terminal do PostgreSQL no EasyPanel:

```bash
# Conectar ao PostgreSQL
psql -U postgres -d acender-sorteios

# Criar database evolution
CREATE DATABASE evolution;

# Verificar se foi criado
\l

# Sair
\q
```

### 2️⃣ Adicionar Evolution API como novo serviço

No EasyPanel:

1. **Criar novo App**
   - Nome: `evolution-api`
   - Tipo: `Docker`
   - Image: `atendai/evolution-api:latest`

2. **Configurar Porta**
   - Internal Port: `8080`
   - Habilitar domínio público

3. **Adicionar Variáveis de Ambiente**

Copie TODAS as variáveis do arquivo `evolution-api.env` e cole no painel de Environment Variables.

**As principais são:**

```bash
# Database (mesmo PostgreSQL, database diferente)
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://postgres:e4e276191bf0755e8dec@acender-sorteios_acender-sorteios-postgres:5432/evolution

# Redis (mesmo Redis, DB diferente)
CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=redis://:d0c0fc91e51e233d29e9@acender-sorteios_acender-sorteios-redis:6379/2

# API Key (anote esta chave!)
AUTHENTICATION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
```

4. **Deploy**
   - Clique em Deploy
   - Aguarde inicialização

### 3️⃣ Obter URL da Evolution API

Após deploy, o EasyPanel gerará uma URL tipo:
```
https://evolution-api-xxxxx.easypanel.host
```

**ANOTE ESTA URL!**

### 4️⃣ Criar Instância WhatsApp

Com a Evolution API rodando, crie a instância:

```bash
# Substituir YOUR_DOMAIN pela URL gerada
curl -X POST https://YOUR_DOMAIN/instance/create \
  -H "apikey: 429683C4C977415CAAFCCE10F7D57E11" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "rifas-whatsapp",
    "qrcode": true
  }'
```

### 5️⃣ Obter QR Code

Acesse no navegador:
```
https://YOUR_DOMAIN/instance/qrcode/rifas-whatsapp
```

Escaneie com WhatsApp:
1. Abra WhatsApp no celular
2. Menu → Aparelhos conectados
3. Conectar um aparelho
4. Escaneie o QR Code

### 6️⃣ Atualizar .env do Django

No seu app Django no EasyPanel, adicione as variáveis:

```bash
EVOLUTION_API_URL=https://evolution-api-xxxxx.easypanel.host
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
EVOLUTION_INSTANCE_NAME=rifas-whatsapp
```

### 7️⃣ Reiniciar Django App

No EasyPanel, reinicie o app Django para carregar as novas variáveis.

---

## ✅ Verificação

### 1. Verificar Evolution API rodando
```bash
curl https://YOUR_DOMAIN/
```

Deve retornar informações da API.

### 2. Verificar Instância WhatsApp
```bash
curl -H "apikey: 429683C4C977415CAAFCCE10F7D57E11" \
     https://YOUR_DOMAIN/instance/connectionState/rifas-whatsapp
```

Deve retornar: `"state": "open"`

### 3. Testar envio de mensagem

No terminal do Django (EasyPanel):
```bash
python manage.py shell

# No shell Python:
from notifications.whatsapp import send_whatsapp_message
send_whatsapp_message('5511999999999', 'Teste Evolution API!')
```

---

## 🗄️ Estrutura Final

```
EasyPanel - Projeto: acender-sorteios
├─ PostgreSQL Container
│  ├─ Database: acender-sorteios (Django)
│  └─ Database: evolution (Evolution API)
│
├─ Redis Container
│  ├─ DB 0: Celery Broker (Django)
│  ├─ DB 1: Celery Results (Django)
│  └─ DB 2: Evolution Cache
│
├─ Django App
│  ├─ Usa: acender-sorteios + Redis DB 0/1
│  └─ Conecta: Evolution API via HTTPS
│
└─ Evolution API App (NOVO)
   ├─ Usa: evolution + Redis DB 2
   └─ Porta: 8080 (HTTPS via EasyPanel)
```

---

## 🔍 Monitoramento

### Logs da Evolution API

No EasyPanel:
1. Acesse o app `evolution-api`
2. Clique em "Logs"
3. Monitore em tempo real

### Logs do Django

Verifique se as mensagens estão sendo enviadas:
```bash
# No terminal do Django
tail -f /var/log/django.log
```

---

## 🚨 Troubleshooting

### Evolution API não inicia

**Verificar:**
- ✓ Database `evolution` foi criado?
- ✓ Variáveis de ambiente corretas?
- ✓ PostgreSQL e Redis estão acessíveis?

**Logs:**
No EasyPanel, veja os logs do container Evolution API.

### WhatsApp não conecta

**Soluções:**
1. Gerar novo QR Code (expira em 30s)
2. Verificar se WhatsApp está atualizado
3. Verificar logs da Evolution API

### Mensagens não chegam

**Checklist:**
- [ ] Evolution API está rodando?
- [ ] WhatsApp está conectado? (verificar QR Code)
- [ ] Variáveis no Django estão corretas?
- [ ] API Key é a mesma em ambos os apps?
- [ ] Instância `rifas-whatsapp` existe?

---

## 📝 Arquivo de Referência

Use o arquivo `evolution-api.env` criado como referência para todas as variáveis de ambiente.

---

## 🎯 Próximos Passos

1. **Criar database `evolution`** no PostgreSQL
2. **Adicionar Evolution API** no EasyPanel
3. **Configurar variáveis** (copiar de `evolution-api.env`)
4. **Deploy** da Evolution API
5. **Criar instância** `rifas-whatsapp`
6. **Conectar WhatsApp** (QR Code)
7. **Atualizar .env do Django** com URL e API Key
8. **Reiniciar Django app**
9. **Testar** envio de mensagem

---

## 🎉 Resultado Final

Quando um cliente comprar e pagar:
1. MercadoPago envia webhook → Django
2. Django marca como pago
3. Django chama Evolution API
4. **Cliente recebe WhatsApp automaticamente!**

**Tudo automático, zero intervenção manual!** 🚀

---

## 📞 URLs de Referência

```bash
# Evolution API (ajustar com seu domínio real)
https://evolution-api-xxxxx.easypanel.host

# QR Code
https://evolution-api-xxxxx.easypanel.host/instance/qrcode/rifas-whatsapp

# Docs Evolution
https://doc.evolution-api.com

# Django App
https://acender-sorteios-acender-sorteios.ivhjcm.easypanel.host
```

---

## ✅ Checklist Final

Setup:
- [ ] Database `evolution` criado no PostgreSQL
- [ ] Evolution API adicionada no EasyPanel
- [ ] Variáveis de ambiente configuradas
- [ ] App Evolution deployado e rodando
- [ ] URL da Evolution API anotada

WhatsApp:
- [ ] Instância `rifas-whatsapp` criada
- [ ] QR Code gerado
- [ ] WhatsApp conectado (escaneado)
- [ ] Status = "open" (verificado)

Integração:
- [ ] Variáveis no Django atualizadas
- [ ] Django app reiniciado
- [ ] Teste de envio funcionando
- [ ] Webhook MercadoPago configurado

Produção:
- [ ] Teste E2E: compra → pagamento → WhatsApp
- [ ] Monitoramento ativo
- [ ] Logs acessíveis

---

**Pronto para começar!** 🎉
