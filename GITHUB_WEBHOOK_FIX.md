# 🚨 Webhook GitHub → EasyPanel: Erro 415

## O Problema Real

```
GitHub envia webhook em format-urlencoded
           ↓
EasyPanel (Fastify) rejeita
           ↓
❌ HTTP 415 - Unsupported Media Type
           ↓
Deploy automático não funciona!
```

**Error:**
```json
{
  "statusCode": 415,
  "code": "FST_ERR_CTP_INVALID_MEDIA_TYPE",
  "error": "Unsupported Media Type",
  "message": "Unsupported Media Type: application/x-www-form-urlencoded"
}
```

---

## 🔍 O Que Está Acontecendo

1. **GitHub** envia webhook do repositório
2. **GitHub** usa `Content-Type: application/x-www-form-urlencoded`
3. **EasyPanel** (Fastify) está configurado só para aceitar `application/json`
4. **EasyPanel** rejeita com 415
5. **Deploy automático falha**

---

## ✅ Como Corrigir no EasyPanel

### Opção 1: Configurar Fastify para aceitar form-urlencoded (RECOMENDADO)

Se você tem acesso ao código do EasyPanel ou webhooks handler:

```javascript
// Adicionar ao handler de webhook do EasyPanel
app.post('/webhook', {
  bodyParser: {
    onProtoPoisoning: 'ignore',
    contentTypeParser: {
      'application/x-www-form-urlencoded': async (request, payload) => {
        return await request.body()
      }
    }
  }
}, async (request, reply) => {
  // seu código aqui
})
```

### Opção 2: Mudar GitHub para enviar JSON (MAIS FÁCIL)

No **GitHub** → Settings → Webhooks → seu webhook:

1. Clique em "Edit"
2. Procure por "Content type"
3. Mude de `application/x-www-form-urlencoded` para `application/json`
4. Clique "Save"
5. Clique "Redeliver" para testar

---

## 🔧 Passo a Passo no GitHub

### Localizar o Webhook:

```
1. Abra: https://github.com/IgorAcender/rifas/settings/hooks
2. Procure pelo webhook do EasyPanel
3. Clique no webhook (pode aparecer como "Push events" ou com URL do EasyPanel)
```

### Alterar Content Type:

```
1. No webhook, role para baixo até "Content type"
2. Mude: application/x-www-form-urlencoded → application/json
3. Clique "Update webhook"
```

### Testar:

```
1. Role para cima até "Recent Deliveries"
2. Clique em qualquer delivery com ❌ (erro)
3. Clique "Redeliver"
4. Verifique se agora retorna ✅ 200 OK
```

---

## 📋 Checklist

- [ ] Acessou https://github.com/IgorAcender/rifas/settings/hooks
- [ ] Encontrou o webhook do EasyPanel
- [ ] Mudou Content type para `application/json`
- [ ] Clicou "Update webhook"
- [ ] Testou "Redeliver"
- [ ] Resultado: ✅ 200 OK

---

## 🚀 Depois da Correção

```
Push para GitHub
       ↓
GitHub envia webhook (JSON)
       ↓
EasyPanel recebe (✅ 200 OK)
       ↓
Deploy automático inicia
       ↓
Sua aplicação atualiza automaticamente!
```

---

## 📸 Screenshots de Referência

### GitHub Webhook Settings:
- Settings → Code and automation → Webhooks
- Procure por seu webhook
- Edite a opção "Content type"

### EasyPanel Webhook:
- No seu app → Settings → Webhooks
- Deve estar apontando para sua URL GitHub Actions ou EasyPanel

---

## ℹ️ Informações Adicionais

**Por que GitHub usa form-urlencoded por padrão?**
- Compatibilidade com sistemas legados
- Menor payload
- Segurança

**Por que EasyPanel (Fastify) rejeita?**
- Fastify é minimalista
- Aceita apenas JSON por padrão
- Precisa configuração extra para form-urlencoded

**Solução ideal:** Mudar para JSON no GitHub (mais moderno e suportado universalmente)

---

## 🎯 Resumo

**O Problema:** GitHub envia form-urlencoded, EasyPanel espera JSON

**A Solução:** Mudar GitHub para enviar JSON

**Tempo:** 2 minutos

**Resultado:** Deploy automático funcionando! ✨

