# 📱 Evolution API + WhatsApp - Sistema de Rifas

## 🎯 O que está implementado?

Este sistema envia **mensagens automáticas via WhatsApp** para compradores quando o pagamento é aprovado.

### ✅ Funcionalidades

- ✨ **Envio automático** de confirmação de pagamento
- 📱 **WhatsApp** via Evolution API (com fallback para Avolution)
- 🔢 **Números da sorte** incluídos na mensagem
- 📊 **Informações completas** (rifa, prêmio, data do sorteio, valor)
- 🔄 **Sistema de fallback** automático entre APIs
- 🗄️ **Compartilha PostgreSQL e Redis** (zero conflito com o app Django)

---

## 📚 Documentação

### 🚀 Começar Rápido
**→ [QUICK_START_EVOLUTION.md](QUICK_START_EVOLUTION.md)**
- Setup em 3 passos
- Checklist completo
- Comandos prontos para copiar

### 🔧 Instalação Completa
**→ [EVOLUTION_API_INSTALL.md](EVOLUTION_API_INSTALL.md)**
- Guia detalhado de instalação
- Docker Compose configurado
- Compartilhamento de PostgreSQL e Redis
- Configuração de segurança

### ⚙️ Configuração da API
**→ [EVOLUTION_API_SETUP.md](EVOLUTION_API_SETUP.md)**
- Como configurar variáveis de ambiente
- Endpoints da API
- Testes e debugging
- Resolução de problemas

### 📨 Sistema de Notificações
**→ [WHATSAPP_NOTIFICATION_GUIDE.md](WHATSAPP_NOTIFICATION_GUIDE.md)**
- Como funciona o envio automático
- Personalizar mensagens
- Onde está implementado
- Logs e monitoramento

---

## 🎬 Como Funciona?

```
┌─────────────────┐
│  Cliente compra │
│   números       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gera PIX no    │
│  MercadoPago    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cliente paga   │
│     o PIX       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MercadoPago    │
│ envia webhook   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django marca   │
│  como PAGO      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Evolution API  │
│ envia WhatsApp  │ ◄── AUTOMÁTICO!
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cliente recebe │
│   confirmação   │
│  com números    │
└─────────────────┘
```

---

## ⚡ Setup Rápido

### 1. Prepare o Database
```bash
./setup_evolution_database.sh
```

### 2. Configure Evolution API
```bash
# Edite docker-compose.evolution.yml com as configs geradas
vim docker-compose.evolution.yml
```

### 3. Inicie
```bash
docker-compose -f docker-compose.evolution.yml up -d
```

### 4. Conecte WhatsApp
```bash
# Acesse para ver o QR Code
open http://localhost:8080/instance/qrcode/rifas-whatsapp
```

### 5. Configure Django
```bash
# Adicione no .env
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-api-key
EVOLUTION_INSTANCE_NAME=rifas-whatsapp
```

### 6. Teste
```bash
python test_evolution.py
```

---

## 📦 Arquivos do Projeto

```
rifas/
├── 📄 README_EVOLUTION.md              ← Você está aqui
├── 🚀 QUICK_START_EVOLUTION.md         ← Começar aqui
├── 📖 EVOLUTION_API_INSTALL.md         ← Instalação detalhada
├── ⚙️  EVOLUTION_API_SETUP.md           ← Configuração da API
├── 📨 WHATSAPP_NOTIFICATION_GUIDE.md   ← Guia de notificações
│
├── 🐳 docker-compose.evolution.yml     ← Config Docker
├── 🔧 setup_evolution_database.sh      ← Script de setup
├── 🧪 test_evolution.py                ← Teste de integração
│
├── notifications/
│   ├── evolution.py                    ← Integração Evolution API
│   └── whatsapp.py                     ← Sistema com fallback
│
├── payments/
│   └── views.py                        ← Webhook que envia WhatsApp
│
└── config/
    └── settings.py                     ← Configurações do projeto
```

---

## 🗄️ Arquitetura de Bancos de Dados

### PostgreSQL (Compartilhado)
```
┌─────────────────────────────┐
│   PostgreSQL Server         │
├─────────────────────────────┤
│ ► seu_database_django       │ ← Django (rifas, users, etc)
│ ► evolution                 │ ← Evolution API (WhatsApp)
└─────────────────────────────┘
```

### Redis (Compartilhado)
```
┌─────────────────────────────┐
│   Redis Server              │
├─────────────────────────────┤
│ DB 0 → Celery Broker        │ ← Django
│ DB 1 → Celery Results       │ ← Django
│ DB 2 → Evolution Cache      │ ← Evolution API
└─────────────────────────────┘
```

**✅ Zero conflito entre sistemas!**

---

## 🔑 Variáveis de Ambiente

### Django (.env)
```bash
# Evolution API
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-api-key-de-32-caracteres
EVOLUTION_INSTANCE_NAME=rifas-whatsapp

# Avolution API (Fallback - opcional)
AVOLUTION_API_URL=https://api.avolution.com.br
AVOLUTION_API_KEY=sua-avolution-key
AVOLUTION_INSTANCE_ID=sua-instance
```

### Evolution API (docker-compose.evolution.yml)
```yaml
environment:
  - AUTHENTICATION_API_KEY=mesma-chave-do-django
  - DATABASE_CONNECTION_URI=postgresql://user:pass@host:5432/evolution
  - REDIS_URI=redis://localhost:6379/2
  - SERVER_URL=http://localhost:8080
```

---

## 📱 Exemplo de Mensagem

Quando o pagamento for aprovado, o cliente recebe:

```
🎉 Pagamento Confirmado!

Olá João Silva!

Seu pagamento foi aprovado com sucesso!

━━━━━━━━━━━━━━━━━━━
🎫 Rifa: iPhone 15 Pro Max
🏆 Prêmio: iPhone 15 Pro Max 256GB
📅 Data do sorteio: 25/12/2024 às 20:00

🔢 Seus números da sorte:
0001, 0042, 0123, 0456, 0789

💰 Valor pago: R$ 50,00
📦 Pedido: #123
━━━━━━━━━━━━━━━━━━━

✅ Seus números estão reservados e concorrendo ao prêmio!

Boa sorte! 🍀✨
```

---

## 🧪 Testando

### Teste da Integração
```bash
python test_evolution.py
```

### Teste Manual
```bash
# Django shell
python manage.py shell

# Importar e testar
from notifications.whatsapp import send_whatsapp_message
send_whatsapp_message('5511999999999', 'Teste!')
```

### Teste Completo (E2E)
1. Acesse sistema como cliente
2. Compre números de uma rifa
3. Gere pagamento PIX
4. Pague (ambiente de teste MercadoPago)
5. Aguarde webhook
6. **Mensagem chega no WhatsApp automaticamente!** ✅

---

## 🔧 Comandos Úteis

```bash
# Verificar status Evolution API
curl http://localhost:8080/

# Ver logs
docker-compose -f docker-compose.evolution.yml logs -f

# Reiniciar
docker-compose -f docker-compose.evolution.yml restart

# Parar
docker-compose -f docker-compose.evolution.yml down

# Atualizar
docker-compose -f docker-compose.evolution.yml pull
docker-compose -f docker-compose.evolution.yml up -d

# Verificar conexão WhatsApp
curl -X GET http://localhost:8080/instance/connectionState/rifas-whatsapp \
  -H "apikey: SUA-API-KEY"
```

---

## 🚨 Troubleshooting

### Mensagens não chegam

**Checklist:**
- [ ] Evolution API está rodando? (`docker ps`)
- [ ] WhatsApp está conectado? (verificar QR Code)
- [ ] API Key está correta no `.env`?
- [ ] Instância existe? (`rifas-whatsapp`)
- [ ] Webhook MercadoPago configurado?
- [ ] Número tem código do país? (55...)

**Ver logs:**
```bash
# Django
tail -f logs/django.log

# Evolution API
docker-compose -f docker-compose.evolution.yml logs -f
```

### WhatsApp desconecta

Evolution API mantém sessão. Se desconectar:
```bash
# Reconectar (gera novo QR Code)
curl -X GET http://localhost:8080/instance/connect/rifas-whatsapp \
  -H "apikey: SUA-API-KEY"
```

### Database/Redis não conecta

```bash
# Testar PostgreSQL
psql -U seu_usuario -d evolution

# Testar Redis
redis-cli -n 2 ping
```

---

## 🔐 Segurança em Produção

### 1. Use HTTPS
```yaml
# docker-compose.evolution.yml
environment:
  - SERVER_URL=https://evolution.seusite.com
```

### 2. Gere API Key forte
```bash
openssl rand -hex 32
```

### 3. Configure Firewall
- Bloqueie porta 8080 externamente
- Use reverse proxy (Nginx)

### 4. SSL/TLS
```nginx
# /etc/nginx/sites-available/evolution
server {
    listen 443 ssl;
    server_name evolution.seusite.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
    }
}
```

---

## 📊 Monitoramento

### Health Check
```bash
# Criar script de monitoramento
#!/bin/bash
STATUS=$(curl -s http://localhost:8080/ | grep -c "Evolution")
if [ $STATUS -eq 0 ]; then
    echo "Evolution API está DOWN!"
    # Enviar alerta
fi
```

### Logs importantes
```bash
# WhatsApp conectado
"Evolution API instance rifas-whatsapp connected"

# Mensagem enviada
"WhatsApp message sent successfully to 5511999999999"

# Erro
"Error sending WhatsApp to..."
```

---

## 🎓 Recursos Adicionais

- **Documentação Evolution API**: https://doc.evolution-api.com
- **GitHub Evolution API**: https://github.com/EvolutionAPI/evolution-api
- **MercadoPago Docs**: https://www.mercadopago.com.br/developers
- **WhatsApp Business API**: https://business.whatsapp.com

---

## 💡 Melhorias Futuras

### Já implementado ✅
- [x] Envio automático após pagamento
- [x] Fallback entre APIs
- [x] Mensagem personalizada
- [x] Compartilhamento de recursos

### Sugestões 💭
- [ ] Enviar imagem do prêmio
- [ ] Lembrete 1 dia antes do sorteio
- [ ] Notificação para todos quando finalizar rifa
- [ ] Mensagem de parabéns para o ganhador
- [ ] Status de entrega do prêmio
- [ ] Botões interativos (WhatsApp Business)
- [ ] Chatbot para dúvidas

---

## 🆘 Suporte

### Problemas com Evolution API
1. Verifique logs: `docker-compose logs -f`
2. Consulte: [EVOLUTION_API_INSTALL.md](EVOLUTION_API_INSTALL.md)
3. GitHub Issues: https://github.com/EvolutionAPI/evolution-api/issues

### Problemas com Integração
1. Execute: `python test_evolution.py`
2. Verifique: [EVOLUTION_API_SETUP.md](EVOLUTION_API_SETUP.md)
3. Verifique: [WHATSAPP_NOTIFICATION_GUIDE.md](WHATSAPP_NOTIFICATION_GUIDE.md)

---

## ✅ Checklist Final

Antes de colocar em produção:

- [ ] PostgreSQL configurado e database `evolution` criado
- [ ] Redis configurado (DB 2 para Evolution)
- [ ] Evolution API rodando e acessível
- [ ] WhatsApp conectado e online
- [ ] Variáveis de ambiente configuradas (Django + Evolution)
- [ ] API Key segura gerada e configurada
- [ ] Teste de envio funcionando
- [ ] Webhook MercadoPago configurado (HTTPS em produção)
- [ ] Teste E2E: compra → pagamento → WhatsApp ✅
- [ ] Logs configurados para monitoramento
- [ ] HTTPS configurado (produção)
- [ ] Backup automático dos databases

---

## 🎉 Está Pronto!

Seu sistema está completamente configurado para:

✅ Receber pagamentos via MercadoPago
✅ Alocar números automaticamente
✅ **Enviar WhatsApp automaticamente com os números**
✅ Sistema redundante com fallback
✅ Compartilhar recursos (PostgreSQL + Redis)

**Não precisa fazer NADA manualmente** - tudo é automático! 🚀

---

## 📞 Contato

Para dúvidas sobre o sistema de rifas, consulte os guias neste README.

**Happy coding!** 💻✨
