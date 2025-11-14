# 🔧 Solução: "Erro ao Verificar WhatsApp"

## 🔴 Problema

Quando coloca o número, aparece:
1. ⏳ "Verificando..." (carrega por muito tempo)
2. ❌ "Erro ao verificar WhatsApp. Tente novamente."

## 🟢 O que foi Corrigido

### 1️⃣ Backend (`accounts/views.py`)
- ✅ Adicionado tratamento de exceções completo
- ✅ Validação melhor do número
- ✅ Melhor logging de erros
- ✅ Retorna HTTP 500 em caso de erro interno

### 2️⃣ Frontend (`public_view.html`)
- ✅ Verifica se a resposta é OK (status 200)
- ✅ Logs detalhados no console
- ✅ Melhor tratamento de resposta não-JSON
- ✅ Mostra erro se a requisição falhar

---

## 📊 Possíveis Causas e Soluções

### Causa 1: Banco de Dados Desconectado

**Sintoma**: "Verificando..." por muito tempo, depois erro

**Solução**:
```bash
# Verifique se o banco está rodando
python manage.py migrate

# Tente reconectar
python manage.py shell
from accounts.models import User
User.objects.count()  # Se retornar 0+ está OK
```

### Causa 2: WhatsApp Inválido

**Sintoma**: Carrega rápido mas dá erro

**Solução**: 
- Verifique o número: deve ter 10-11 dígitos
- Formato esperado: `37999999999` (sem símbolos)

### Causa 3: Timeout na API

**Sintoma**: Carrega muito tempo (>30s)

**Solução**:
```bash
# Aumente timeout no nginx/apache
# Ou verifique se o servidor está respondendo
curl -X POST http://localhost:8000/api/auth/check-whatsapp/ \
  -H "Content-Type: application/json" \
  -d '{"whatsapp": "37999999999"}'
```

### Causa 4: CSRF Token Inválido

**Sintoma**: Erro imediato

**Solução**:
- Limpe cache do navegador
- Recarregue a página
- Tente em outro navegador

---

## 🧪 Como Testar

### Teste 1: Via Terminal

```bash
curl -X POST http://localhost:8000/api/auth/check-whatsapp/ \
  -H "Content-Type: application/json" \
  -d '{"whatsapp": "37999999999"}'

# Resposta esperada:
# {"exists": false, "user": null}
```

### Teste 2: Via DevTools (F12)

1. Abra F12 → Console
2. Digite:
```javascript
fetch('/api/auth/check-whatsapp/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
    },
    body: JSON.stringify({ whatsapp: '37999999999' })
}).then(r => r.json()).then(console.log)
```

3. Veja a resposta no console

### Teste 3: Logs do Servidor

```bash
tail -f logs/django.log | grep "check_whatsapp\|Error in check"
```

---

## 📋 Checklist de Resolução

- [ ] Servidor Django está rodando?
  ```bash
  python manage.py runserver
  ```

- [ ] Banco de dados está ok?
  ```bash
  python manage.py dbshell
  SELECT COUNT(*) FROM accounts_user;
  ```

- [ ] Número tem formato correto?
  - Com DDD: 11 dígitos
  - Apenas números: `37999999999`

- [ ] CSRF Token está na página?
  ```javascript
  document.querySelector('[name="csrfmiddlewaretoken"]')
  ```

- [ ] API retorna 200 OK?
  ```bash
  # Ver no DevTools → Network
  # POST /api/auth/check-whatsapp/
  # Status: 200 OK
  ```

---

## 🚀 Melhorias Implementadas

| Item | Antes | Depois |
|------|-------|--------|
| Tratamento de erro | Genérico | Detalhado com logging |
| Validação | Mínima | Completa |
| Response check | Não | Sim (status 200) |
| Logging | Não | Sim (exc_info=True) |
| Frontend feedback | Básico | Melhorado |

---

## 📞 Se Ainda Não Funcionar

1. **Verifique os logs**:
   ```bash
   tail -100 logs/django.log
   ```

2. **Veja o console do navegador** (F12 → Console)

3. **Teste via curl**:
   ```bash
   curl -v -X POST http://localhost:8000/api/auth/check-whatsapp/ \
     -H "Content-Type: application/json" \
     -d '{"whatsapp": "37999999999"}'
   ```

4. **Reinicie o servidor**:
   ```bash
   # Ctrl+C para parar
   python manage.py runserver
   ```

---

**Data da Correção**: 14 de novembro de 2025  
**Status**: ✅ Melhorado com melhor tratamento de erros
