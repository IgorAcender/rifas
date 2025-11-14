# 🚀 COMEÇAR AQUI - Instruções Rápidas

## ⚡ Em 2 Minutos

### Passo 1: Obter ID do Grupo

Via terminal (usando curl):
```bash
curl -X GET "https://seu-evolution-api.com/chats/instance-name" \
  -H "apikey: sua-api-key" | grep "@g.us"
```

Você verá algo como: `120363123456789@g.us`

### Passo 2: Testar no Admin

1. Acesse: `Admin → WhatsApp Manager`
2. Role para: "Enviar Mensagem de Teste"
3. Cole no campo: `120363123456789@g.us`
4. Escreva uma mensagem
5. Clique: "📤 Enviar Mensagem"

### Passo 3: Verificar

- ✅ Se receber "Mensagem enviada com sucesso para o grupo!" - PRONTO!
- ❌ Se receber erro - veja troubleshooting abaixo

---

## 🆘 Se Não Funcionar

### ❌ "Falha ao enviar mensagem"

**Solução**:
1. Clique em "Atualizar Status" para verificar conexão
2. Se desconectado, clique em "Mostrar QR Code" para reconectar
3. Tente novamente

### ❌ "Número de telefone ou ID do grupo é obrigatório"

**Solução**: Deixou o campo vazio
- Copie o ID novamente
- Cole com cuidado

### ❌ ID do grupo não funciona

**Solução**: ID pode estar incorreto
- Verifique com curl novamente
- Certifique-se que termina com `@g.us`

---

## 📖 Próximas Leituras

| Documento | Quando Ler |
|-----------|-----------|
| `README_GRUPOS.txt` | Depois de testar |
| `GUIA_PRATICO_GRUPOS.md` | Se quiser mais exemplos |
| `COMO_USAR_ID_GRUPO.md` | Se tiver dúvida sobre ID |
| `CORRECAO_ENVIO_GRUPOS.md` | Se quiser entender o código |

---

## ✨ Resumo

- ✅ Antes: Grupos não funcionavam
- ✅ Agora: Grupos funcionam perfeitamente!
- ✅ Números também continuam funcionando

---

**Pronto para testar?** 🎉

Vá agora em `Admin → WhatsApp Manager` e experimente!
