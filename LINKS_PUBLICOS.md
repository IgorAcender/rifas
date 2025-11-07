# 🎉 Sistema de Links Públicos para Rifas

## ✅ Implementação Concluída!

Agora você pode compartilhar suas rifas com links públicos e bonitos!

## 📋 O que foi adicionado:

### 1. **Campo Slug nas Rifas**
- ✅ Cada rifa agora tem um slug único gerado automaticamente
- ✅ URLs amigáveis como: `https://seu-site.com/r/iphone-15-pro/`

### 2. **Página Pública de Vendas**
- ✅ Design moderno e responsivo
- ✅ Grid de números disponíveis/vendidos
- ✅ Seleção interativa de números
- ✅ Botão de compra via WhatsApp
- ✅ Compartilhamento fácil do link
- ✅ Estatísticas em tempo real

### 3. **Painel Admin Atualizado**
- ✅ Botão "Copiar Link de Vendas" em cada rifa ativa
- ✅ Botão "Ver Página" para visualizar a página pública
- ✅ Links funcionam com um clique!

## 🚀 Como usar:

### Passo 1: Rodar as migrações
```bash
python manage.py migrate
```

### Passo 2: Gerar slugs para rifas existentes (opcional)
```bash
python manage.py shell < generate_slugs.py
```

### Passo 3: Configurar o WhatsApp
Edite o arquivo `templates/raffles/public_view.html` na linha 454:
```javascript
const whatsappNumber = '5511999999999'; // Coloque seu WhatsApp aqui
```

### Passo 4: Testar!
1. Acesse `/campanhas/`
2. Clique em "Copiar Link de Vendas" em uma rifa ativa
3. Cole o link no navegador ou compartilhe!

## 📱 Link de Exemplo:
```
https://seu-dominio.com/r/rifa-iphone-15/
```

## 🎨 Recursos da Página Pública:

- **Header bonito** com gradiente e emoji
- **Grid de números** com cores intuitivas:
  - 🟢 Verde = Disponível
  - 🔵 Azul = Selecionado
  - ⚪ Cinza = Vendido
- **Seleção múltipla** de números
- **Cálculo automático** do total
- **Botão de compra** que abre o WhatsApp com mensagem pré-formatada
- **Copiar link** com um clique
- **100% responsivo** para mobile e desktop

## ⚙️ Customizações:

### Mudar número do WhatsApp:
`templates/raffles/public_view.html` - linha 454

### Mudar cores/design:
`templates/raffles/public_view.html` - seção `<style>`

### Personalizar mensagem do WhatsApp:
`templates/raffles/public_view.html` - função `proceedToBuy()`

## 🔗 URLs do Sistema:

| Rota | Descrição | Autenticação |
|------|-----------|--------------|
| `/r/<slug>/` | Página pública da rifa | ❌ Não |
| `/campanhas/` | Lista de campanhas | ✅ Sim |
| `/criar-campanha/` | Criar nova campanha | ✅ Sim |
| `/admin-login/` | Login admin | ❌ Não |

## 🎯 Próximos passos sugeridos:

1. ✅ Configurar o número do WhatsApp
2. ✅ Testar a página pública
3. ✅ Compartilhar o link nas redes sociais
4. 🔜 Integrar gateway de pagamento (MercadoPago/PagSeguro)
5. 🔜 Adicionar QR Code para facilitar vendas
6. 🔜 Sistema de indicação com links únicos

## 💡 Dicas:

- Use slugs curtos e memoráveis
- Compartilhe o link em stories, posts e grupos
- Configure o WhatsApp Business para melhor atendimento
- Monitore as estatísticas no painel admin

---

**Desenvolvido com ❤️ para facilitar suas vendas de rifas!**
