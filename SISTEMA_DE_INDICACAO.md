# Sistema de Indicação - Como Funciona

## Status: ✅ FUNCIONANDO (após correções)

## Configuração por Rifa

Cada rifa pode ter suas próprias configurações de indicação:

### Campos no modelo `Raffle`:

1. **`enable_referral`** (Boolean, padrão: `True`)
   - Ativa ou desativa o sistema de indicações para esta rifa

2. **`referral_min_purchase`** (Integer, padrão: `1`)
   - Quantidade mínima de números que o cliente precisa comprar para poder indicar amigos
   - Se for `0`, não há mínimo
   - Exemplo: se for `5`, só quem comprar 5 ou mais números pode gerar link de indicação

3. **`inviter_bonus`** (Integer, padrão: `2`)
   - Quantidade de números grátis que o INDICANTE recebe quando o amigo completa a compra

4. **`invitee_bonus`** (Integer, padrão: `1`)
   - Quantidade de números grátis que o INDICADO recebe ao completar a compra

## Fluxo Completo

### 1. Cliente faz uma compra e atinge o mínimo

```
Cliente A compra 5 números (assumindo referral_min_purchase = 5)
↓
Pagamento aprovado
↓
Sistema verifica: quantidade >= referral_min_purchase?
✅ SIM → Mostra botão "Indicar Amigo" no modal de confirmação
```

### 2. Cliente A clica em "Indicar Amigo"

**IMPORTANTE**: Ainda falta implementar a criação automática do código de indicação!

Por enquanto, você precisa criar manualmente via:
- Admin Django
- API: `POST /api/raffles/referrals/`

```json
{
  "raffle": 1
}
```

Isso gera um código único (ex: `ABC12DEF`) para o Cliente A.

### 3. Cliente A compartilha o link

Link gerado: `https://seu-site.com/r/teste/?ref=ABC12DEF`

O sistema já detecta o código na URL e salva no localStorage.

### 4. Cliente B (indicado) acessa o link e compra

```
Cliente B acessa o link com ?ref=ABC12DEF
↓
Código salvo no localStorage do navegador
↓
Cliente B faz login/cadastro
↓
Cliente B escolhe números e clica em "Comprar"
↓
Sistema envia:
{
  "quantity": 3,
  "referral_code": "ABC12DEF"  ← Incluído automaticamente
}
↓
Serializer verifica o código e marca como "resgatado"
↓
Código fica vinculado ao pedido (campo referral_code)
↓
Status do pedido: PENDING (aguardando pagamento)
```

### 5. Pagamento aprovado pelo MercadoPago

```
Webhook recebe: payment_data["status"] = "approved"
↓
Sistema chama: order.mark_as_paid()
↓
mark_as_paid() executa:
  1. Marca números como VENDIDOS
  2. Verifica se tem referral_code no pedido
  3. SE TEM:
     - Busca o Referral pelo código
     - Chama: referral.allocate_bonus_numbers()
↓
allocate_bonus_numbers() aloca:
  - 2 números grátis para Cliente A (inviter_bonus)
  - 1 número grátis para Cliente B (invitee_bonus)

Status dos números:
  - source = "referral_inviter" (indicante)
  - source = "referral_invitee" (indicado)
```

## Tipos de Número

Os números têm um campo `source` que indica a origem:

```python
class RaffleNumber.Source:
    PURCHASE = 'purchase'              # Compra normal
    REFERRAL_INVITER = 'referral_inviter'   # Bônus do indicante
    REFERRAL_INVITEE = 'referral_invitee'   # Bônus do indicado
```

Isso permite identificar facilmente:
- Quantos números foram comprados
- Quantos números foram ganhos por indicação

## O que foi corrigido

### ❌ Problema 1: Números não eram alocados
**Antes**: `allocate_bonus_numbers()` nunca era chamado

**Agora**: Chamado automaticamente em `mark_as_paid()` quando há referral_code

### ❌ Problema 2: Código não era salvo no pedido
**Antes**: Não havia campo para guardar o código

**Agora**:
- Campo `referral_code` adicionado ao modelo `RaffleOrder`
- Serializer salva o código quando pedido é criado
- View de compra passa o código via context

### ❌ Problema 3: Backend não recebia o código
**Antes**: Frontend não enviava o código na requisição

**Agora**:
- View `/api/raffles/{id}/buy/` espera `referral_code` no request.data
- Código é passado via context para o serializer

## O que ainda falta implementar

### 1. Criação automática de código após compra ❌

Quando um cliente completa uma compra com quantidade >= `referral_min_purchase`,
o sistema deveria:

```python
# Pseudo-código
if order.status == 'paid' and order.quantity >= raffle.referral_min_purchase:
    # Verifica se já tem código
    existing_referral = Referral.objects.filter(
        inviter=order.user,
        raffle=order.raffle
    ).first()

    if not existing_referral:
        # Cria novo código
        Referral.objects.create(
            inviter=order.user,
            raffle=order.raffle
            # code é gerado automaticamente
        )
```

### 2. Endpoint para obter código do usuário ❌

```
GET /api/raffles/{raffle_id}/my-referral-code/
```

Retorna:
```json
{
  "code": "ABC12DEF",
  "link": "https://seu-site.com/r/teste/?ref=ABC12DEF",
  "clicks": 5,
  "redeemed": 2
}
```

### 3. UI melhorada no modal ❌

Após pagamento aprovado, mostrar:
- Botão para copiar link de indicação
- QR Code do link
- Contador de cliques/indicações

## Exemplo de uso

### Configurar rifa:

```python
raffle = Raffle.objects.get(slug='minha-rifa')
raffle.enable_referral = True
raffle.referral_min_purchase = 3  # Mínimo 3 números para indicar
raffle.inviter_bonus = 2           # Indicante ganha 2 números
raffle.invitee_bonus = 1           # Indicado ganha 1 número
raffle.save()
```

### Testar o fluxo:

```bash
# 1. Cliente A compra 3 números (atinge mínimo)
# 2. Criar código manualmente (por enquanto)
POST /api/raffles/referrals/
{
  "raffle": 1
}
# Resposta: { "code": "ABC12DEF", ... }

# 3. Cliente B acessa: /r/minha-rifa/?ref=ABC12DEF
# 4. Cliente B compra 2 números
# 5. Pagamento aprovado
# 6. Sistema aloca automaticamente:
#    - Cliente A recebe 2 números grátis
#    - Cliente B recebe 1 número grátis
```

## Verificar se funcionou

```python
from raffles.models import RaffleNumber, Referral

# Ver indicações da rifa
referrals = Referral.objects.filter(
    raffle_id=1,
    status='redeemed'
)

for ref in referrals:
    print(f"Indicante: {ref.inviter.name}")
    print(f"Indicado: {ref.invitee.name}")
    print(f"Números do indicante alocados: {ref.inviter_numbers_allocated}")
    print(f"Números do indicado alocados: {ref.invitee_numbers_allocated}")
    print("---")

# Ver números bônus
bonus_numbers = RaffleNumber.objects.filter(
    raffle_id=1,
    source__in=['referral_inviter', 'referral_invitee']
)

print(f"\nTotal de números bônus: {bonus_numbers.count()}")
for num in bonus_numbers:
    print(f"Número {num.number:04d} - {num.user.name} - {num.get_source_display()}")
```

## Próximos passos

1. ✅ Corrigir alocação de números (FEITO)
2. ✅ Adicionar campo referral_code (FEITO)
3. ✅ Integrar com webhook de pagamento (FEITO)
4. ❌ Criar código automaticamente após compra
5. ❌ Endpoint para obter código do usuário
6. ❌ Melhorar UI do modal de confirmação
7. ❌ Adicionar analytics de indicações no dashboard

## Logs para debug

Quando uma indicação é processada, você verá nos logs:

```
✅ Payment approved for order 15
👤 User: João Silva (ID: 5)
📱 WhatsApp: 5511999999999
💰 Order 15 marked as paid
🔢 Allocated numbers: [123, 456, 789]
📤 Attempting to send WhatsApp to 5511999999999
✅ WhatsApp sent successfully to 5511999999999
```

Se houver indicação:
```
INFO: Allocating bonus numbers for referral ABC12DEF
INFO: Allocated 2 numbers for inviter (User ID: 1)
INFO: Allocated 1 number for invitee (User ID: 5)
```
