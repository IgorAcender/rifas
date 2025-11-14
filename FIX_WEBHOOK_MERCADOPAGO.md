# 🔧 Fix: Webhook MercadoPago - AssertionError Corrigido

## ❌ Erro Encontrado

```
AssertionError: .accepted_renderer not set on Response
```

Aparecia ao receber webhooks do MercadoPago.

---

## 🔍 Causa Raiz

A função `mercadopago_webhook()` estava:
- Retornando `Response` do Django REST Framework
- Mas NÃO estava decorada com `@api_view`
- Isso causa conflito porque DRF precisa de renderer configurado

---

## ✅ Solução Implementada

Mudei todos os `Response()` para `JsonResponse()`:

**Antes:**
```python
from rest_framework.response import Response

def mercadopago_webhook(request):
    ...
    return Response(status=status.HTTP_200_OK)  # ❌ Erro!
```

**Depois:**
```python
from django.http import JsonResponse

def mercadopago_webhook(request):
    ...
    return JsonResponse({'status': 'ok'}, status=200)  # ✅ OK!
```

---

## 📁 Arquivo Modificado

`payments/views.py`

Alterações:
- ✅ Linha ~145: Adicionado `from django.http import JsonResponse`
- ✅ Linhas ~170-240: Trocado todos `Response()` por `JsonResponse()`

---

## 🚀 Por Que Funciona

- `JsonResponse` é uma view Django **comum** (não precisa de renderer)
- Retorna JSON simples sem decoradores especiais
- Compatível com webhooks externos como MercadoPago
- Sem conflitos com DRF

---

## 🧪 Resultado

```
Antes: ❌ AssertionError: .accepted_renderer not set
Depois: ✅ Webhook processado normalmente
```

O webhook do MercadoPago agora funciona sem erros!

---

## 📊 Contexto Técnico

| Aspecto | Response (DRF) | JsonResponse (Django) |
|--------|---------------|--------------------|
| Decorador necessário | @api_view | Nenhum |
| Renderer necessário | Sim (obrigatório) | Não (automático) |
| Uso em webhooks | ❌ Problemático | ✅ Recomendado |

---

## ✨ Resumo

- ❌ Problema: DRF Response sem renderer configurado
- ✅ Solução: Trocado para JsonResponse (Django padrão)
- 🚀 Resultado: Webhook funciona perfeitamente!
