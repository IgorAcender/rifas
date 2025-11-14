# 🎓 Guia Prático: Testando o Envio para Grupos

## 1️⃣ Encontrar o ID do Seu Grupo

### Opção A: Usar a Evolution API (Recomendado)

**Passo 1**: Abra uma ferramenta como Insomnia, Postman ou Terminal

**Passo 2**: Faça uma requisição GET:
```bash
curl -X GET "https://seu-evolution-api.com/chats/your-instance-name" \
  -H "apikey: sua-api-key"
```

**Passo 3**: Procure pela resposta os grupos. Você verá algo assim:
```json
{
  "data": {
    "chats": [
      {
        "id": "120363123456789@g.us",
        "name": "Meu Grupo de Rifas",
        "isGroup": true
      },
      {
        "id": "5511999999999@s.whatsapp.net",
        "name": "João",
        "isGroup": false
      }
    ]
  }
}
```

**Passo 4**: Copie o `id` do grupo (aquele com `@g.us`)

---

## 2️⃣ Testar o Envio

### Via Interface (Interface Web)

1. **Acesse o Admin**
   - URL: `https://seu-site.com/admin/`
   - Faça login

2. **Vá para WhatsApp Manager**
   - Menu lateral: **WhatsApp**
   - Clique em **WhatsApp Manager**

3. **Role até "Enviar Mensagem de Teste"**
   - Você verá um formulário

4. **Preencha os campos**
   ```
   Número do WhatsApp ou ID do Grupo: 120363123456789@g.us
   Mensagem: Teste de mensagem para o grupo! 🎉
   ```

5. **Clique em "📤 Enviar Mensagem"**

6. **Espere a resposta**
   - ✅ Verde: Enviado com sucesso
   - ❌ Vermelho: Falha no envio

---

## 3️⃣ Exemplos de IDs de Grupo

Todos estes formatos são válidos:

```
120363123456789@g.us                          ✅ Formato padrão
120363123456789-1234567890@g.us               ✅ Formato com timestamp
120363999888777666555444@g.us                 ✅ Números grandes
```

---

## 4️⃣ Teste: Números Individuais

Se quiser testar com um número individual:

```
5511999999999              ✅ Com código do Brasil
5511 99999999              ✅ Com espaço
(11) 99999999              ✅ Com formatação
+5511999999999             ✅ Com +
11999999999                ✅ Sem código (adiciona 55)
```

---

## 5️⃣ Troubleshooting

### ❌ "Número de telefone ou ID do grupo é obrigatório"

**Solução**: Deixou o campo vazio
- Verifique se digitou algo
- Copie o ID corretamente

---

### ❌ "Número de telefone inválido"

**Solução**: Formato inválido para número
- Certifique-se de que tem apenas dígitos e caracteres de formatação
- Para grupo, use o formato com `@g.us`

---

### ❌ "Falha ao enviar mensagem"

**Causas possíveis**:
1. WhatsApp não está conectado
2. ID do grupo está incorreto
3. API não tem permissão

**Soluções**:
1. Clique em **"Atualizar Status"** para verificar
2. Se desconectado, clique em **"Mostrar QR Code"** para reconectar
3. Verifique o ID do grupo na Evolution API

---

### ❌ "Mensagem não chegou ao grupo"

**Causas possíveis**:
1. ID do grupo incorreto
2. WhatsApp sem permissão no grupo
3. Rede com problema

**Soluções**:
1. Verifique o ID na Evolution API
2. Abra o grupo no WhatsApp Web e verifique se consegue enviar manualmente
3. Reinicie a instância (clique em **"Reiniciar Instância"**)

---

## 6️⃣ Verificação Passo a Passo

### Checklist Antes de Enviar

- [ ] WhatsApp está conectado (status mostra "Conectado")
- [ ] Tenho o ID do grupo correto (termina com `@g.us`)
- [ ] O WhatsApp está no grupo
- [ ] Tenho permissão para enviar mensagens no grupo

### Checklist Após Enviar

- [ ] Recebeu mensagem verde "Mensagem enviada com sucesso!"
- [ ] Mensagem chegou ao grupo no WhatsApp
- [ ] Mensagem aparece com a hora correta

---

## 7️⃣ Exemplo Real

### Cenário: Enviar teste de sorteio para grupo de players

**Passo 1**: Obtenha o ID do grupo
```
ID: 120363111222333@g.us
Nome: "Grupo de Rifas - Novembro"
```

**Passo 2**: Acesse Admin → WhatsApp Manager

**Passo 3**: Preencha o formulário
```
Número do WhatsApp ou ID do Grupo: 120363111222333@g.us

Mensagem:
🎉 TESTE - SORTEIO DE RIFAS 🎉

Olá grupo! 

Este é um teste de mensagem automática. 
Em breve teremos sorteios com prêmios incríveis!

Não perca! 🎁🍀
```

**Passo 4**: Clique em "Enviar Mensagem"

**Resultado Esperado**:
```
✅ Mensagem enviada com sucesso para o grupo!
```

E a mensagem chega ao grupo em segundos! ✨

---

## 8️⃣ API de Teste (Curl)

Se preferir testar via terminal:

```bash
# Variáveis
GROUP_ID="120363123456789@g.us"
API_URL="https://seu-evolution-api.com"
INSTANCE_NAME="seu-instancia"
API_KEY="sua-api-key"

# Enviar mensagem
curl -X POST "$API_URL/message/sendText/$INSTANCE_NAME" \
  -H "Content-Type: application/json" \
  -H "apikey: $API_KEY" \
  -d "{
    \"number\": \"$GROUP_ID\",
    \"text\": \"Teste para grupo! 🎉\"
  }"
```

---

## 9️⃣ Próximos Passos

Após confirmar que o envio funciona:

1. **Usar em Notificações**: Configure grupos para receber notificações de prêmios
2. **Automação**: Crie fluxos que enviam para grupos automaticamente
3. **Relatórios**: Monitore entrega de mensagens para grupos

---

## 🔟 FAQ

**P: Posso enviar para múltiplos grupos?**
R: Não na interface, mas você pode fazer loop na API

**P: Qual é a frequência máxima de mensagens?**
R: Evolution API limita conforme seu plano

**P: Grupos privados funcionam?**
R: Sim, desde que o WhatsApp tenha acesso

**P: Posso usar figuras nos grupos?**
R: Sim, use `send_media_message()` em vez de `send_text_message()`

---

## 📞 Suporte

Se tiver problemas:
1. Consulte `CORRECAO_ENVIO_GRUPOS.md` (detalhes técnicos)
2. Consulte `COMO_USAR_ID_GRUPO.md` (mais documentação)
3. Verifique os logs: `/logs/`

---

**Sucesso! Agora você sabe como enviar mensagens para grupos! 🚀**
