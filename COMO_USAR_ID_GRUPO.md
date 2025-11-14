# Como Usar ID do Grupo para Enviar Mensagens de Teste

## O que foi corrigido?

Agora você pode enviar mensagens de teste diretamente para **grupos do WhatsApp**, não apenas para números individuais.

## Como Obter o ID do Grupo

### Método 1: Usar a Evolution API (Recomendado)

1. No painel de administração, vá para **WhatsApp Manager**
2. Faça uma chamada para a Evolution API para listar seus chats:
   ```
   GET https://seu-evolution-api.com/chats/your-instance-name
   Headers: apikey: sua-api-key
   ```

3. Localize seu grupo na resposta. O ID terá este formato:
   ```
   120363xxx-1234567890@g.us
   ```

### Método 2: Copiar do WhatsApp (Manual)

Infelizmente, o WhatsApp não exibe o ID do grupo diretamente. Você pode:

1. Usar a Evolution API para descobrir
2. Usar um cliente REST como **Insomnia** ou **Postman** para fazer a chamada
3. Procurar no banco de dados (se estiver desenvolvendo localmente)

### Método 3: Usando o WhatsApp Web

1. Abra o WhatsApp Web (web.whatsapp.com)
2. Clique no grupo desejado
3. Abra o console do navegador (F12)
4. Execute este comando JavaScript:
   ```javascript
   Store.Chat.findBySender(/* copie de Store.Chat._models[0].id */)
   ```

Pode ser complexo, então a **Evolution API** é o melhor método.

## Formatos Aceitos

### Para Números Individuais

Todos estes formatos funcionam:

```
5511999999999           ✅ (com código do Brasil)
5511 99999999           ✅ (com espaço)
+5511999999999          ✅ (com +)
(11) 99999999           ✅ (com formatação)
11 99999999             ✅ (sem código, adiciona 55 automaticamente)
11999999999             ✅ (sem código)
```

### Para Grupos

Use o formato exato retornado pela Evolution API:

```
120363xxx-1234567890@g.us         ✅ (formato correto)
120363xxxxxxxxx@g.us               ✅ (formato alternativo)
```

## Testando

1. Vá para **Admin > WhatsApp Manager**
2. Role para a seção **"Enviar Mensagem de Teste"**
3. Cole o número ou ID do grupo
4. Digite sua mensagem
5. Clique em **"Enviar Mensagem"**

A resposta será:
- ✅ "Mensagem enviada com sucesso para o número!" (para números)
- ✅ "Mensagem enviada com sucesso para o grupo!" (para grupos)
- ❌ "Falha ao enviar mensagem..." (se houver erro)

## Troubleshooting

### "Número de telefone ou ID do grupo é obrigatório"
- Você deixou o campo vazio
- Preecha com um número ou ID de grupo válido

### "Número de telefone inválido" (apenas para números)
- O valor não contém apenas números e caracteres especiais esperados
- Verifique se digitou corretamente

### "Falha ao enviar mensagem"
- O WhatsApp não está conectado
- Clique em **"Atualizar Status"** para verificar a conexão
- Se desconectado, clique em **"Mostrar QR Code"** para reconectar

### Mensagem não chega ao grupo
- O ID do grupo pode estar incorreto
- Verifique usando a Evolution API se o grupo está cadastrado
- O WhatsApp pode não estar conectado ou com permissão de enviar

## Próximos Passos

Após confirmar que o envio de teste funciona, você pode:

1. Configurar templates de mensagens
2. Automatizar o envio de notificações para grupos
3. Usar o sistema em produção

Para dúvidas, consulte a [Documentação da Evolution API](https://doc.evolution-api.com/)
