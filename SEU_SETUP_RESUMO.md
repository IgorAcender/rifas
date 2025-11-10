# 🎯 RESUMO - Seu Setup Evolution API

## 📦 Suas Credenciais Atuais

### PostgreSQL
```
Host: acender-sorteios_acender-sorteios-postgres
Port: 5432
User: postgres
Password: e4e276191bf0755e8dec

Databases:
├─ acender-sorteios (Django - já existe)
└─ evolution (Evolution API - CRIAR)
```

### Redis
```
Host: acender-sorteios_acender-sorteios-redis
Port: 6379
Password: d0c0fc91e51e233d29e9

Databases:
├─ DB 0: Django Celery Broker
├─ DB 1: Django Celery Results
└─ DB 2: Evolution API (SEM CONFLITO)
```

### API Key Evolution
```
429683C4C977415CAAFCCE10F7D57E11
```
**Use esta chave tanto na Evolution quanto no Django!**

---

## 🚀 5 Passos para Configurar

### 1️⃣ Criar Database "evolution"

No terminal PostgreSQL do EasyPanel:
```sql
CREATE DATABASE evolution;
\l
```

Ou execute o arquivo:
```bash
psql -U postgres -d acender-sorteios -f create_evolution_database.sql
```

### 2️⃣ Adicionar Evolution API no EasyPanel

**Criar novo App:**
- Nome: `evolution-api`
- Tipo: Docker
- Image: `atendai/evolution-api:latest`
- Port: `8080`

**Copiar variáveis de `evolution-api.env`:**

As 3 mais importantes:
```bash
DATABASE_CONNECTION_URI=postgresql://postgres:e4e276191bf0755e8dec@acender-sorteios_acender-sorteios-postgres:5432/evolution

CACHE_REDIS_URI=redis://:d0c0fc91e51e233d29e9@acender-sorteios_acender-sorteios-redis:6379/2

AUTHENTICATION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
```

**Deploy!**

### 3️⃣ Conectar WhatsApp

Após deploy, acesse:
```
https://[SUA-URL-GERADA-PELO-EASYPANEL]/instance/qrcode/rifas-whatsapp
```

Mas ANTES, crie a instância:
```bash
curl -X POST https://[SUA-URL]/instance/create \
  -H "apikey: 429683C4C977415CAAFCCE10F7D57E11" \
  -H "Content-Type: application/json" \
  -d '{"instanceName": "rifas-whatsapp", "qrcode": true}'
```

Depois escaneie o QR Code com WhatsApp.

### 4️⃣ Atualizar Django .env

Adicione no seu app Django (EasyPanel):
```bash
EVOLUTION_API_URL=https://[URL-DA-EVOLUTION-GERADA-PELO-EASYPANEL]
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
EVOLUTION_INSTANCE_NAME=rifas-whatsapp
```

**Reinicie o Django app** para carregar as variáveis.

### 5️⃣ Testar

No shell do Django:
```python
python manage.py shell

from notifications.whatsapp import send_whatsapp_message
send_whatsapp_message('5511999999999', 'Teste!')
```

---

## 📁 Arquivos Criados para Você

```
✅ evolution-api.env              → Variáveis prontas para copiar no EasyPanel
✅ .env.django.updated           → Seu .env do Django atualizado
✅ create_evolution_database.sql → Script SQL para criar database
✅ EASYPANEL_SETUP.md            → Guia completo passo a passo
✅ SEU_SETUP_RESUMO.md           → Este arquivo (resumo)
```

---

## 🔄 Fluxo Automático

```
Cliente paga PIX
      ↓
MercadoPago webhook → Django
      ↓
Django marca como PAGO
      ↓
Django → Evolution API
      ↓
Evolution API → WhatsApp Cliente
      ↓
✅ Cliente recebe confirmação com números!
```

**TUDO AUTOMÁTICO!**

---

## 🎯 Checklist Rápido

Antes de começar:
- [ ] Arquivo `evolution-api.env` aberto
- [ ] Acesso ao EasyPanel pronto
- [ ] Terminal PostgreSQL acessível

Setup:
- [ ] Database `evolution` criado
- [ ] Evolution API adicionada no EasyPanel
- [ ] Todas as variáveis de `evolution-api.env` copiadas
- [ ] App deployado e rodando

WhatsApp:
- [ ] Instância criada via curl
- [ ] QR Code acessado no navegador
- [ ] WhatsApp escaneado e conectado

Django:
- [ ] 3 variáveis adicionadas (EVOLUTION_*)
- [ ] App reiniciado
- [ ] Teste de envio funcionou

---

## 🆘 Se algo der errado

### Evolution API não inicia
→ Ver logs no EasyPanel
→ Verificar se variáveis estão corretas
→ Verificar se database `evolution` existe

### Mensagem não chega
→ Verificar se Evolution está rodando
→ Verificar se WhatsApp está conectado
→ Verificar API Key (mesma em ambos os apps)
→ Ver logs do Django

### QR Code não aparece
→ Criar instância primeiro (curl)
→ Depois acessar URL do QR Code
→ QR Code expira em 30 segundos (gerar novo se necessário)

---

## 📝 Informações Importantes

**PostgreSQL:**
- Mesma instância, databases separados ✅
- Django: `acender-sorteios`
- Evolution: `evolution`

**Redis:**
- Mesma instância, DBs diferentes ✅
- Django: DB 0 e 1
- Evolution: DB 2

**API Key:**
- `429683C4C977415CAAFCCE10F7D57E11`
- Usar em AMBOS os apps!

**URLs:**
- Django: `https://acender-sorteios-acender-sorteios.ivhjcm.easypanel.host`
- Evolution: A ser gerada pelo EasyPanel após deploy

---

## 🎉 Resultado Final

Seu sistema ficará assim:

```
EasyPanel - Projeto acender-sorteios
│
├─ PostgreSQL Container
│  ├─ acender-sorteios (Django)
│  └─ evolution (Evolution API)
│
├─ Redis Container
│  ├─ DB 0 (Django Celery)
│  ├─ DB 1 (Django Celery)
│  └─ DB 2 (Evolution API)
│
├─ Django App (existente)
│  └─ Envia via Evolution API
│
└─ Evolution API App (NOVO)
   └─ Envia mensagens WhatsApp
```

**✅ Compartilhado, sem conflitos, eficiente!**

---

## 📚 Próximo Passo

Leia: **[EASYPANEL_SETUP.md](EASYPANEL_SETUP.md)** para instruções detalhadas.

Ou comece executando:
```sql
CREATE DATABASE evolution;
```

**Boa sorte!** 🚀
