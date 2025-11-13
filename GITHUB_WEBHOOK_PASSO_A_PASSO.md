# 🔧 Guia Prático: Corrigir Webhook GitHub em 2 Minutos

## Passo 1: Acessar Settings do Repositório

```
https://github.com/IgorAcender/rifas/settings/hooks
```

Ou manualmente:
1. Vá para: https://github.com/IgorAcender/rifas
2. Clique em "Settings" (engrenagem no topo direito)
3. No menu esquerdo: "Webhooks"

---

## Passo 2: Encontrar o Webhook do EasyPanel

Você deve ver uma lista de webhooks. Procure por um que:
- Tem a URL do EasyPanel
- Mostra ❌ com erro 415

**Exemplo de URL:**
```
https://acender-sorteios-acender-sorteios.ivhjcm.easypanel.host/...
```

---

## Passo 3: Clicar no Webhook

Clique no webhook problemático para abri-lo.

---

## Passo 4: Localizar "Content type"

Role a página até encontrar a seção "Content type":

```
Content type: ⭕ application/x-www-form-urlencoded
              ⭕ application/json
```

Ele está marcado em `form-urlencoded`.

---

## Passo 5: Mudar para JSON

Clique no radio button `application/json`:

```
Content type: ⭕ application/x-www-form-urlencoded
              🔘 application/json  ← CLIQUE AQUI
```

---

## Passo 6: Salvar

Role até o botão "Update webhook" no final da página e clique.

---

## Passo 7: Testar

### Opção A: Redeliver (Reenviar webhook anterior)
1. Procure "Recent Deliveries" no topo
2. Clique em qualquer entrega com ❌ (erro)
3. Clique no botão 🔄 "Redeliver"
4. Aguarde 5 segundos
5. Atualize a página
6. Se virar ✅, funcionou!

### Opção B: Fazer novo push
1. Faça qualquer commit e push
2. Volte para Webhooks
3. Verifique em "Recent Deliveries"
4. Deve aparecer ✅ 200 OK

---

## ✅ Resultado Esperado

Antes:
```
❌ 415 - Unsupported Media Type
Resent
Time: 2 minutes ago
```

Depois:
```
✅ 200 OK
Delivered
Time: just now
```

---

## 🚀 Depois: Deploy Automático Funciona!

```
Push para GitHub
       ↓
✅ Webhook recebido (200 OK)
       ↓
EasyPanel recebe configuração
       ↓
Deploy automático inicia
       ↓
Seu código atualiza em produção!
```

---

## 📸 Capturas de Tela (Descrição)

### Tela 1: Lista de Webhooks
- Mostra vários webhooks
- Procure por um com URL do EasyPanel

### Tela 2: Webhook Detalhes
- Scroll até encontrar "Content type"
- Radio button para mudar

### Tela 3: Sucesso!
- Recent Deliveries mostra ✅ 200 OK
- Deploy automático funciona

---

## ⚠️ Se Ainda Não Funcionar

1. **Verifique se é o webhook certo**
   - Deve ter URL do EasyPanel
   - Deve estar em "Push events"

2. **Verifique Recent Deliveries**
   - Clique em um com ✅ ou ❌
   - Veja Request/Response completo

3. **Tente fazer novo push**
   - Mudar um arquivo
   - Fazer commit
   - Push para main
   - Voltar e verificar

4. **Se tiver erro 500 no Response**
   - O EasyPanel pode ter outro erro
   - Verifique logs do EasyPanel

---

## 🎯 Próximas Ações

Após webhook funcionar (✅ 200 OK):

1. [ ] Confirmar que deploy automático inicia
2. [ ] Verificar logs do EasyPanel
3. [ ] Fazer teste E2E: push → deploy → verificar site
4. [ ] Se tudo OK, problema resolvido!

---

**Pronto! Em 2 minutos seu webhook funciona! ✨**

