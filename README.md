# Sistema de Rifas - API REST

Sistema completo de rifas com autenticação via WhatsApp, pagamentos e notificações.

## Funcionalidades

- ✅ Autenticação via WhatsApp (sem senha para usuários)
- ✅ Admin com WhatsApp + senha
- ✅ Sistema de rifas com números aleatórios
- ✅ Números revelados apenas após pagamento
- ✅ Sistema de indicação/referral com números grátis
- ✅ Integração MercadoPago
- ✅ Notificações via Avolution WhatsApp API
- ✅ Imagens em Base64

## Stack Técnica

- Python 3.11
- Django 4.2 + Django REST Framework
- PostgreSQL
- Redis (Celery)
- Docker

## Estrutura do Projeto

```
rifas/
├── accounts/          # Autenticação WhatsApp
├── raffles/           # Sistema de rifas
├── payments/          # MercadoPago
├── notifications/     # Avolution WhatsApp API
└── config/            # Settings
```

## Deploy no Easypanel

1. Criar novo serviço no Easypanel
2. Conectar ao repositório GitHub
3. Configurar variáveis de ambiente (ver `.env.example`)
4. Deploy automático!

## Endpoints Principais

### Autenticação
- `POST /api/auth/login/` - Login via WhatsApp
- `GET /api/auth/me/` - Dados do usuário atual
- `POST /api/auth/token/refresh/` - Renovar token

### Rifas
- `GET /api/raffles/` - Listar rifas ativas
- `POST /api/raffles/{id}/buy/` - Comprar números
- `GET /api/raffles/my-orders/` - Meus pedidos

### Pagamentos
- `POST /api/payments/mercadopago/create/` - Criar pagamento
- `POST /api/payments/mercadopago/webhook/` - Webhook MercadoPago

## Credenciais Padrão (Admin)

- WhatsApp: `5511999999999`
- Senha: `admin123`

**⚠️ IMPORTANTE: Altere essas credenciais em produção!**
