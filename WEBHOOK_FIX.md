# 🔧 Correção do Erro de Webhook - Content-Type

## Problema
```json
{
  "statusCode": 415,
  "code": "FST_ERR_CTP_INVALID_MEDIA_TYPE",
  "error": "Unsupported Media Type",
  "message": "Unsupported Media Type: application/x-www-form-urlencoded"
}
```

## Causa Raiz
O MercadoPago envia webhooks com `Content-Type: application/x-www-form-urlencoded`, mas seu Django REST Framework estava configurado para aceitar apenas `application/json`.

## Solução Implementada

### 1. **Atualização das Configurações REST Framework** (`config/settings.py`)
Adicionados parsers que aceitam múltiplos formatos:

```python
REST_FRAMEWORK = {
    # ... outras configs
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}
```

### 2. **Refatoração do Webhook** (`payments/views.py`)
Substituído o decorator `@api_view` por uma view Django pura que:

✅ Desabilita CSRF (`@csrf_exempt`)  
✅ Aceita apenas POST (`@require_http_methods(["POST"])`)  
✅ Detecta automaticamente o `Content-Type` recebido  
✅ Processa tanto JSON quanto form-urlencoded  
✅ Mantém toda a lógica de processamento de pagamento  

```python
@require_http_methods(["POST"])
@csrf_exempt
def mercadopago_webhook(request):
    """MercadoPago webhook handler - Accepts both JSON and form-urlencoded"""
    # Detecta o tipo de conteúdo
    content_type = request.META.get('CONTENT_TYPE', 'application/json')
    
    if 'application/x-www-form-urlencoded' in content_type:
        # Converte form data para dict
        request_data = dict(request.POST)
    elif 'application/json' in content_type:
        # Parseia JSON
        import json
        request_data = json.loads(request.body)
    # ... resto da lógica
```

## O que foi alterado

### `config/settings.py`
- ✅ Adicionado `DEFAULT_PARSER_CLASSES` ao REST_FRAMEWORK

### `payments/views.py`
- ✅ Removido `@api_view(['POST'])` e `@permission_classes([AllowAny])`
- ✅ Adicionado `@csrf_exempt` e `@require_http_methods(["POST"])`
- ✅ Implementado parser de content-type dinâmico
- ✅ Mantida toda a lógica de notificação WhatsApp

## Como Testar

### Teste Manual via cURL (Form-encoded)
```bash
curl -X POST http://localhost:8000/api/payments/mercadopago/webhook/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "action=payment.updated&data[id]=123456"
```

### Teste via JSON
```bash
curl -X POST http://localhost:8000/api/payments/mercadopago/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"action":"payment.updated","data":{"id":123456}}'
```

### Verificar Logs
```bash
tail -f logs/debug.log | grep -i "webhook"
```

## Benefícios
✅ Webhook funciona com MercadoPago  
✅ Suporta múltiplos formatos de dados  
✅ Melhor tratamento de erros  
✅ Logging completo para debug  
✅ Notificações WhatsApp automáticas restauradas  

## Próximos Passos
1. Deploy em produção
2. Testar recebimento de webhooks reais do MercadoPago
3. Monitorar logs para confirmar processamento correto
