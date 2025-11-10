# ✅ Sistema de Indicação - 100% Funcional!

## Resumo das Implementações

### 1. ✅ Criação Automática de Código de Indicação

**Arquivo**: `raffles/models.py` - método `mark_as_paid()`

Quando um pedido é marcado como pago:
- Sistema verifica se a rifa tem indicações ativadas (`enable_referral = True`)
- Verifica se quantidade comprada >= `referral_min_purchase`
- Se elegível e ainda não tem código, cria automaticamente
- Código é único (8 caracteres: letras maiúsculas + números)

```python
# Exemplo de código gerado: "A3K9Z2L7"
```

**Log no sistema:**
```
🎁 Created referral code A3K9Z2L7 for user João Silva
```

---

### 2. ✅ Endpoint para Buscar Código do Usuário

**Rota**: `GET /api/raffles/{raffle_id}/my-referral/`

**Autenticação**: Requer Bearer token

**Resposta quando usuário TEM código**:
```json
{
  "has_referral": true,
  "code": "A3K9Z2L7",
  "link": "https://seu-site.com/r/teste/?ref=A3K9Z2L7",
  "clicks": 15,
  "successful_referrals": 3,
  "inviter_bonus": 2,
  "invitee_bonus": 1,
  "created_at": "2025-11-10T12:30:00Z"
}
```

**Resposta quando usuário NÃO tem código**:
```json
{
  "has_referral": false,
  "eligible": false,
  "total_purchased": 2,
  "min_required": 5,
  "message": "Compre pelo menos 5 números para ganhar seu link de indicação"
}
```

---

### 3. ✅ Modal Atualizado com Link de Indicação

**Arquivo**: `templates/raffles/public_view.html` - função `showSuccess()`

Após pagamento aprovado, o modal exibe:

#### Se usuário é elegível e tem código:
- ✅ Card roxo degradê com informações
- ✅ Campo de texto com link completo
- ✅ Botão "Copiar Link"
- ✅ Botão "Compartilhar" (usa Web Share API quando disponível)
- ✅ Estatísticas: cliques e indicações bem-sucedidas

#### Exemplo visual:
```
┌─────────────────────────────────────────┐
│  🎁 Ganhe 2 Números Grátis!            │
│  Indique um amigo e vocês dois ganham  │
│  números extras!                        │
│                                         │
│  Você ganha 2 e seu amigo ganha 1      │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ https://site.com/r/rifa/?ref=A... │ │
│  └───────────────────────────────────┘ │
│                                         │
│  [📋 Copiar Link]  [📤 Compartilhar]   │
│                                         │
│  15 cliques • 3 indicações bem-sucedidas│
└─────────────────────────────────────────┘
```

---

## Fluxo Completo de Uso

### Cenário 1: Primeiro comprador (João)

1. **João compra 5 números** (assumindo `referral_min_purchase = 5`)
2. **Pagamento aprovado** → MercadoPago webhook
3. **Sistema automaticamente**:
   - Marca pedido como pago
   - Envia WhatsApp com números
   - **✨ Cria código de indicação**: `A3K9Z2L7`
4. **Modal exibe**:
   - Números da sorte de João
   - Link de indicação: `https://site.com/r/teste/?ref=A3K9Z2L7`
   - Botões para copiar/compartilhar
5. **João compartilha o link** com Maria

---

### Cenário 2: Amigo indicado (Maria)

1. **Maria clica no link** de João: `/r/teste/?ref=A3K9Z2L7`
2. Sistema salva o código no localStorage
3. **Maria faz cadastro** (nome + WhatsApp)
4. **Maria compra 3 números**
5. Sistema envia código junto:
   ```json
   {
     "quantity": 3,
     "referral_code": "A3K9Z2L7"
   }
   ```
6. **Código é resgatado** (status: PENDING → REDEEMED)
7. **Pagamento aprovado** → MercadoPago webhook
8. **Sistema automaticamente aloca**:
   - ✅ **2 números grátis** para João (indicante)
   - ✅ **1 número grátis** para Maria (indicado)
9. **Ambos recebem WhatsApp** confirmando números

---

## Configuração por Rifa

Cada rifa pode ter configurações diferentes:

```python
raffle = Raffle.objects.get(slug='minha-rifa')

# Ativar sistema de indicações
raffle.enable_referral = True

# Mínimo de 3 números para poder indicar
raffle.referral_min_purchase = 3

# Indicante ganha 2 números grátis
raffle.inviter_bonus = 2

# Indicado ganha 1 número grátis
raffle.invitee_bonus = 1

raffle.save()
```

---

## Rastreamento de Números

Os números agora têm origem rastreada no campo `source`:

### Na área do cliente:

```
Número 0042
[Vendido]
🎁 Bonus Indicante
```

```
Número 0137
[Vendido]
🎁 Bonus Indicado
```

---

## Verificar se Está Funcionando

### 1. Verificar no banco de dados:

```python
from raffles.models import Referral, RaffleNumber

# Ver códigos criados
Referral.objects.filter(raffle_id=1).values('code', 'inviter__name', 'status', 'clicks')

# Ver números bônus alocados
RaffleNumber.objects.filter(
    raffle_id=1,
    source__in=['referral_inviter', 'referral_invitee']
).values('number', 'user__name', 'source')
```

### 2. Testar o endpoint:

```bash
# Obter token
curl -X POST https://seu-site.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"whatsapp":"5511999999999","name":"João"}'

# Buscar código de indicação
curl -X GET https://seu-site.com/api/raffles/1/my-referral/ \
  -H "Authorization: Bearer SEU_TOKEN"
```

### 3. Observar logs:

Após uma compra paga, você verá:
```
✅ Payment approved for order 17
💰 Order 17 marked as paid
🔢 Allocated numbers: [123, 456, 789]
🎁 Created referral code A3K9Z2L7 for user João Silva
📤 Attempting to send WhatsApp to 5511999999999
✅ WhatsApp sent successfully to 5511999999999
```

---

## Estatísticas Disponíveis

O endpoint `/api/raffles/{id}/my-referral/` retorna:

- **`clicks`**: Quantas pessoas clicaram no link
- **`successful_referrals`**: Quantas pessoas completaram compra

Isso permite mostrar ao usuário:
```
15 cliques • 3 indicações bem-sucedidas
```

---

## Compatibilidade

### Navegadores modernos:
- ✅ Web Share API (compartilhamento nativo)
- ✅ Clipboard API (copiar com um clique)

### Navegadores antigos:
- ✅ Fallback com `document.execCommand('copy')`
- ✅ Alerta de confirmação

---

## Próximos Passos (Opcionais)

1. **Dashboard de indicações** - Mostrar estatísticas detalhadas
2. **QR Code** - Gerar QR Code do link de indicação
3. **Ranking** - Top indicadores do mês
4. **Prêmios especiais** - Bônus extras para quem indicar X pessoas
5. **Notificações** - Avisar quando alguém usa seu código

---

## Troubleshooting

### Problema: Código não é criado automaticamente
**Solução**: Verificar se `enable_referral = True` e se quantidade >= `referral_min_purchase`

### Problema: Link não aparece no modal
**Solução**: Verificar se o token JWT está válido e se o endpoint está respondendo

### Problema: Números bônus não são alocados
**Solução**: Verificar logs para erro em `allocate_bonus_numbers()`. Pode ser falta de números disponíveis.

---

## Resumo Final

✅ **Backend completo** - Criação, resgate e alocação de bônus
✅ **API REST** - Endpoint para buscar código
✅ **Frontend integrado** - Modal exibe link com botões
✅ **WhatsApp funcionando** - Mensagens chegando corretamente
✅ **100% Automático** - Zero intervenção manual necessária

**O sistema está PRONTO para produção!** 🚀
