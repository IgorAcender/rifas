# 🧪 Modo de Teste - Sistema de Rifas

## O que é o Modo de Teste?

O Modo de Teste permite simular compras e testar todas as funcionalidades do sistema sem processar pagamentos reais. É ideal para:

- ✅ Testar notificações WhatsApp (compra, confirmação, números premiados)
- ✅ Verificar o fluxo completo de compra
- ✅ Validar números premiados e suas mensagens
- ✅ Treinar equipe sem custos reais

## Como Ativar

1. Acesse o **Admin Django** (`/admin`)
2. Entre em **Raffles > Rafles**
3. Edite a campanha desejada
4. Marque o campo **"Modo de Teste"** ✅
5. Salve

## Como Usar

### 1. Acesse a Página Pública da Campanha

Acesse normalmente: `https://seusite.com/r/slug-da-campanha/`

### 2. Faça uma Compra de Teste

1. Selecione os números
2. Preencha nome e WhatsApp
3. **Em vez do PIX**, você verá um botão: **"💳 Pagamento Teste"**
4. **Escolha se quer forçar número premiado:**
   - ✅ Toggle **LIGADO** (verde) → Força um número premiado
   - ⭕ Toggle **DESLIGADO** (cinza) → Compra normal sem prêmio
5. Clique em **"✅ Simular Pagamento Aprovado"**

### 3. O que Acontece Automaticamente

**Com toggle LIGADO (🎁 Forçar Número Premiado):**
- Criar o pedido
- Marcar como PAGO
- **Forçar um número premiado** (se disponível)
- Enviar todas as notificações WhatsApp:
  - Confirmação de compra para o cliente
  - Notificação para admins
  - **Mensagem de número premiado** 🎉

**Com toggle DESLIGADO:**
- Criar o pedido
- Marcar como PAGO
- Enviar apenas notificações de compra:
  - Confirmação de compra para o cliente
  - Notificação para admins
  - (Sem mensagem de prêmio)

## Números Premiados em Modo de Teste

### Toggle "🎁 Forçar Número Premiado"

No modal de pagamento teste, você encontra um **switch liga/desliga**:

- **✅ LIGADO (Verde):** Sistema força um número premiado na compra
- **⭕ DESLIGADO (Cinza):** Compra normal, sem forçar prêmio

### Como Funciona com Toggle LIGADO:

1. O sistema busca números premiados **não ganhos** ainda
2. Se houver número premiado disponível:
   - Troca o número reservado do usuário pelo premiado
   - Marca o prêmio como ganho
   - Dispara notificações de prêmio
3. Se não houver número premiado disponível:
   - Processa normalmente
   - Envia apenas notificações de compra

### Para Testar Números Premiados:

1. Certifique-se de que a campanha tem **Números Premiados cadastrados**
2. Configure `release_percentage_min` e `release_percentage_max`
3. Faça uma compra de teste
4. **LIGUE o toggle** 🎁 Forçar Número Premiado
5. O primeiro número premiado disponível será automaticamente atribuído

### Para Testar Compra Normal (Sem Prêmio):

1. Faça uma compra de teste
2. **DESLIGUE o toggle** 🎁 Forçar Número Premiado
3. Receberá apenas notificações de compra confirmada
4. Ideal para testar fluxo sem prêmios

## Diferenças do Modo Real

| Funcionalidade | Modo Real | Modo Teste |
|---|---|---|
| **Pagamento** | PIX via Mercado Pago | Botão "Simular Pagamento" |
| **Cobrança** | R$ reais cobrados | Nenhuma cobrança |
| **Notificações** | ✅ Enviadas | ✅ Enviadas (iguais) |
| **Número Premiado** | Aleatório (conforme %) | **Controlável via toggle** |
| **Banco de Dados** | Gravado normalmente | Gravado normalmente |
| **Toggle Prêmio** | Não existe | ✅ Liga/desliga força prêmio |

## Quando Desativar

⚠️ **Antes de ir para produção**, desmarque o campo **"Modo de Teste"** no admin.

Campanhas em modo de teste exibem o aviso:
> 🧪 Modo de Teste Ativado - Este é um ambiente de teste.

## Exemplos de Teste

### Testar Notificação de Compra Simples
1. Ative modo de teste
2. Faça uma compra teste
3. **DESLIGUE o toggle** 🎁 (cinza)
4. ✅ Receberá apenas notificação de compra confirmada

### Testar Número Premiado
1. Ative modo de teste
2. Cadastre um número premiado (ex: número 500, 10%-20%)
3. Faça uma compra teste
4. **LIGUE o toggle** 🎁 (verde)
5. ✅ O sistema vai atribuir o 500 e enviar notificação de prêmio

### Testar Múltiplos Prêmios
1. Cadastre 3 números premiados
2. Faça 3 compras de teste seguidas (toggle ligado)
3. ✅ Cada compra vai ganhar 1 dos prêmios cadastrados

### Testar Compra Normal + Compra com Prêmio
1. Primeira compra: toggle **DESLIGADO** → só notificação de compra
2. Segunda compra: toggle **LIGADO** → notificação de compra + prêmio
3. ✅ Testa ambos os fluxos na mesma campanha

## Logs e Debug

Para verificar o que aconteceu:

```bash
# Ver logs do Django
docker logs -f <nome-container>

# Verificar no Admin Django
/admin/raffles/raffleorder/ → Ver status dos pedidos
/admin/raffles/prizenumber/ → Ver quais prêmios foram ganhos
```

## Dicas

💡 **Recomendações:**
- Sempre teste com seu próprio WhatsApp primeiro
- Configure números premiados antes de testar
- Verifique se as mensagens personalizadas estão corretas
- Teste o fluxo completo antes de lançar

⚠️ **NUNCA deixe modo de teste ativo em produção com vendas reais!**

## Suporte

Se tiver problemas:
1. Verifique logs do Django
2. Confirme que Evolution API está funcionando
3. Verifique se os templates de mensagem estão configurados
4. Teste com um número premiado cadastrado primeiro
