# 🐛 Guia de Troubleshooting - Webhook MercadoPago

## Se ainda tiver problemas, verifique:

### 1. ❌ Status 415 com FormParser configurado?

**Causa:** Pode ser proxy/servidor frontend rejeitando

**Solução:**
```bash
# Verificar Nginx/Apache headers
curl -v https://seu-dominio.com/api/payments/mercadopago/webhook/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "test=1"
```

Se retornar 415, verifique:
- Nginx: `client_max_body_size`
- Apache: `mod_rewrite` rules
- Cloudflare: WAF rules

---

### 2. ❌ Status 200 mas WhatsApp não enviado?

**Verifique logs:**
```bash
# Procurar por erros de WhatsApp
grep -i "whatsapp\|evolution" logs/debug.log | tail -20

# Procurar por erros gerais
grep "ERROR" logs/debug.log | tail -20
```

**Causas comuns:**
- ❌ `EVOLUTION_API_KEY` vazio
- ❌ `EVOLUTION_INSTANCE_NAME` errado
- ❌ WhatsApp desconectado
- ❌ Número do usuário inválido

---

### 3. ❌ Erro: "No payment_id in webhook data"?

**Causa:** MercadoPago mudou formato de envio

**Debug:**
```python
# Adicione ao webhook para debugar:
import json
logger.info(f"Raw request body: {request.body}")
logger.info(f"Request POST: {request.POST}")
logger.info(f"Content-Type: {request.META.get('CONTENT_TYPE')}")
```

**Solução:** Verifique URL de webhook no MercadoPago:
```
https://seu-dominio.com/api/payments/mercadopago/webhook/
```

---

### 4. ❌ ALLOWED_HOSTS error?

**Erro:** `Invalid HTTP_HOST header: 'example.com'`

**Solução em settings.py:**
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
# Adicione seu domínio em .env:
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com,www.seu-dominio.com
```

---

### 5. ❌ CSRF token missing?

**Erro:** 403 Forbidden CSRF

**Solução:** Webhook já tem `@csrf_exempt` - se ainda der erro:
```python
# Verifique middleware em config/settings.py
'django.middleware.csrf.CsrfViewMiddleware',  # Deve estar aqui

# Webhook tem @csrf_exempt
@csrf_exempt  # ← Deve estar presente
@require_http_methods(["POST"])
def mercadopago_webhook(request):
```

---

### 6. ❌ Timeout ao conectar MercadoPago?

**Causa:** Firewall ou DNS

**Debug:**
```bash
# Testar conectividade com MercadoPago
curl -I https://api.mercadopago.com/v1/payments/123456 \
  -H "Authorization: Bearer $MERCADOPAGO_ACCESS_TOKEN"

# Testar DNS
nslookup api.mercadopago.com
```

---

### 7. ❌ "Invalid Media Type" em produção mas OK local?

**Causa:** Proxy/CDN alterando headers

**Verifique:**
```bash
# Proxy altera Content-Type?
curl -X POST https://seu-dominio.com/api/payments/mercadopago/webhook/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "action=payment.updated&data[id]=123" \
  -v 2>&1 | grep -i "content-type"

# Verificar headers recebidos no Django
# Adicione ao webhook:
logger.info(f"Headers: {dict(request.META)}")
```

---

## 📊 Checklist de Validação

```
🔧 Configuração:
  [ ] FormParser adicionado a DEFAULT_PARSER_CLASSES
  [ ] @csrf_exempt no webhook
  [ ] Domínio em ALLOWED_HOSTS
  [ ] MERCADOPAGO_ACCESS_TOKEN configurado

🔐 Segurança:
  [ ] Webhook URL está públeca (sem autenticação)
  [ ] CSRF desabilitado apenas para webhook
  [ ] Rate limiting está OK? (nenhum, MercadoPago é confiável)

📱 WhatsApp:
  [ ] EVOLUTION_API_URL configurado
  [ ] EVOLUTION_API_KEY válido
  [ ] EVOLUTION_INSTANCE_NAME correto
  [ ] WhatsApp conectado (QR code scaneado)

🔍 Logs:
  [ ] DEBUG = True em desenvolvimento
  [ ] Logs salvando em arquivo
  [ ] Nenhum erro 500 no webhook

✅ Testes:
  [ ] python3 test_webhook_fix.py retorna sucesso
  [ ] Curl form-urlencoded retorna 200
  [ ] Curl JSON retorna 200
```

---

## 📞 Suporte

Se ainda tiver problemas:

1. **Verifique logs completos:**
```bash
tail -100 logs/debug.log | grep -A5 "Webhook"
```

2. **Teste com MercadoPago Sandbox:**
```
https://sandbox.mercadopago.com/
```

3. **Ative DEBUG em settings.py:**
```python
DEBUG = True
```

4. **Verifique Webhook Settings no MercadoPago:**
```
Dashboard → Configurações → Webhooks
URL deve ser: https://seu-dominio.com/api/payments/mercadopago/webhook/
Topics: payment
```

---

## 🆘 Emergency Debug

Ativa logging máximo:
```python
# Adicione ao webhook temporariamente:
import sys
import traceback

@require_http_methods(["POST"])
@csrf_exempt
def mercadopago_webhook(request):
    try:
        # seu código aqui
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        traceback.print_exc()
        raise
```

Então rode:
```bash
python manage.py runserver 2>&1 | grep -i "erro\|error"
```

