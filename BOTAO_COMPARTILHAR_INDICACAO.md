# ✅ Botão de Compartilhar Link de Indicação - Implementado!

## O que foi adicionado

Nova seção **"Compartilhar Link de Indicação"** que aparece na área do cliente (`/minha-area/`) **SOMENTE** quando o usuário comprou 10 ou mais bilhetes em uma campanha.

---

## Condição para Aparecer

### Regra:
```
Total de bilhetes comprados NAQUELA CAMPANHA ESPECÍFICA >= 10
```

**IMPORTANTE:** A verificação é feita **por campanha**, não no total geral!

### Como é calculado:
```python
# Para CADA código de indicação, verifica se o usuário comprou 10+ bilhetes NAQUELA rifa específica
for referral in all_referral_codes:
    total_tickets = RaffleOrder.objects.filter(
        user=request.user,
        raffle=referral.raffle,  # ← Filtra pela rifa ESPECÍFICA
        status=RaffleOrder.Status.PAID
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # Só mostra se >= 10 bilhetes NESSA rifa
    if total_tickets >= 10:
        my_referral_codes.append(referral)
```

**Exemplo 1 - Uma campanha:**
- João compra 3 bilhetes na "Rifa A" → Não aparece botão
- João compra mais 5 bilhetes na "Rifa A" → Total = 8 → Não aparece botão
- João compra mais 2 bilhetes na "Rifa A" → Total = 10 → ✅ **APARECE BOTÃO da Rifa A**

**Exemplo 2 - Múltiplas campanhas:**
- João compra 15 bilhetes na "Rifa A" → ✅ Aparece botão da Rifa A
- João compra 5 bilhetes na "Rifa B" → ❌ NÃO aparece botão da Rifa B
- João compra 12 bilhetes na "Rifa C" → ✅ Aparece botão da Rifa C

**Resultado:** João vê 2 cards de compartilhamento (Rifa A e Rifa C), cada um com seu link específico!

---

## Visual da Seção

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  🔗  Campanha Teste                                                          │
│      15 bilhetes comprados • 23 cliques no link • Ganhe 2 números grátis    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ https://site.com/r/teste/?ref=A3K9Z2L7                                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  [📋 Copiar Link]        [📤 Compartilhar]                                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Elementos:
1. **Ícone verde** com link (🔗)
2. **Nome da campanha**
3. **Estatísticas**:
   - Quantos bilhetes você comprou NESSA campanha
   - Quantos cliques seu link recebeu
   - Quantos números grátis você ganha por indicação
4. **Campo de texto** com link completo (readonly)
5. **Dois botões**:
   - **Copiar Link**: Copia para clipboard
   - **Compartilhar**: Usa Web Share API (ou fallback)

---

## Funcionalidades

### 1. Botão "Copiar Link" 📋

**Comportamento:**
1. Clica no botão
2. Link é copiado para clipboard
3. Aparece notificação verde no canto superior direito: "✅ Link copiado!"
4. Notificação some após 2 segundos com animação

**Código:**
```javascript
function copyReferralLink(inputId) {
    const input = document.getElementById(inputId);

    // Tenta API moderna primeiro
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(input.value).then(() => {
            showCopySuccess();
        }).catch(() => {
            fallbackCopy(input); // Fallback para navegadores antigos
        });
    } else {
        fallbackCopy(input);
    }
}
```

**Compatibilidade:**
- ✅ Navegadores modernos: `navigator.clipboard.writeText()`
- ✅ Navegadores antigos: `document.execCommand('copy')`

### 2. Botão "Compartilhar" 📤

**Comportamento:**

#### Em dispositivos móveis/navegadores modernos:
1. Clica no botão
2. Abre o menu nativo de compartilhamento do sistema
3. Usuário escolhe onde compartilhar (WhatsApp, Telegram, etc.)

#### Em navegadores que não suportam Web Share API:
1. Copia link automaticamente
2. Mostra alerta: "Link copiado! Cole e compartilhe onde preferir."

**Código:**
```javascript
function shareReferral(link, raffleName) {
    const shareData = {
        title: 'Participe da Rifa!',
        text: `Participe da rifa "${raffleName}" usando meu link e ganhe números grátis!`,
        url: link
    };

    // Web Share API disponível?
    if (navigator.share) {
        navigator.share(shareData)
            .then(() => console.log('Shared successfully'))
            .catch((error) => {
                if (error.name !== 'AbortError') {
                    fallbackShare(link);
                }
            });
    } else {
        fallbackShare(link);
    }
}
```

**Exemplo de mensagem compartilhada:**
```
Participe da Rifa!

Participe da rifa "Campanha Teste" usando meu link e ganhe números grátis!

https://site.com/r/teste/?ref=A3K9Z2L7
```

---

## Notificação de Sucesso

Quando o link é copiado, aparece uma notificação verde animada:

```
┌─────────────────┐
│ ✅ Link copiado! │  ← Desliza da direita
└─────────────────┘
```

**Características:**
- Aparece no canto superior direito
- Cor verde (`#22c55e`)
- Animação de entrada (desliza da direita)
- Fica visível por 2 segundos
- Animação de saída (desliza para direita)
- Auto-remove do DOM

---

## Posicionamento na Página

A seção aparece **entre** "Minhas Campanhas" e "Minhas Indicações":

```
1. Minhas Campanhas
2. 🆕 Compartilhar Link de Indicação (se >= 10 bilhetes)
3. Minhas Indicações
4. Meus Números
5. Histórico de Compras
```

---

## Múltiplas Campanhas

Se o usuário comprou 10+ bilhetes em **várias campanhas**, cada uma terá seu próprio card com estatísticas específicas:

```
┌────────────────────────────────────────────────────────────┐
│  🔗  Rifa A                                                │
│      15 bilhetes comprados • 20 cliques • Ganhe 2 números  │
│  [Link da Rifa A com código específico]                   │
│  [Copiar] [Compartilhar]                                   │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  🔗  Rifa B                                                │
│      12 bilhetes comprados • 5 cliques • Ganhe 1 número    │
│  [Link da Rifa B com código específico]                   │
│  [Copiar] [Compartilhar]                                   │
└────────────────────────────────────────────────────────────┘
```

**Cada card mostra:**
- Quantos bilhetes você comprou **nessa campanha específica**
- Quantos cliques **o link dessa campanha** recebeu
- Link único **para essa campanha** com seu código de indicação

---

## Implementação Técnica

### Backend - `accounts/views.py`

```python
# Buscar TODOS os códigos de indicação do usuário
all_referral_codes = Referral.objects.filter(
    inviter=request.user
).select_related('raffle')

# Para CADA código, verificar se ele comprou 10+ bilhetes NAQUELA campanha específica
my_referral_codes = []
for referral in all_referral_codes:
    # Soma os bilhetes comprados APENAS nessa rifa específica
    total_tickets = RaffleOrder.objects.filter(
        user=request.user,
        raffle=referral.raffle,  # ← Filtro pela rifa ESPECÍFICA
        status=RaffleOrder.Status.PAID
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # Só inclui se >= 10 bilhetes NESSA rifa
    if total_tickets >= 10:
        # Adiciona o total como atributo para exibir no template
        referral.total_tickets = total_tickets
        my_referral_codes.append(referral)
```

**Diferença crítica:**
- ❌ Antes: Verificava total geral de todas as rifas
- ✅ Agora: Verifica bilhete por bilhete em **cada campanha individualmente**

### Frontend - `customer_area.html`

```html
{% if my_referral_codes %}
<div class="section-title">
    <h2>Compartilhar Link de Indicação</h2>
    <p class="subtitle">Compartilhe o link das campanhas onde você comprou 10+ bilhetes</p>
</div>

<div class="share-referral-section">
    {% for referral in my_referral_codes %}
    <div class="share-card">
        <div class="share-header">
            <div class="share-icon">🔗</div>
            <div class="share-info">
                <h4>{{ referral.raffle.name }}</h4>
                <p class="share-stats">
                    {{ referral.total_tickets }} bilhetes comprados •
                    {{ referral.clicks }} cliques no link •
                    Ganhe {{ referral.raffle.inviter_bonus }} números grátis
                </p>
            </div>
        </div>
        <!-- Botões e link -->
    </div>
    {% endfor %}
</div>
{% endif %}
```

**Importante:**
- Só renderiza se `my_referral_codes` não estiver vazio
- Cada card mostra `referral.total_tickets` (quantidade de bilhetes naquela campanha específica)
- Cada card tem link único para sua campanha

---

## Estilo Visual

### Cores:
- **Ícone**: Gradiente verde (`#22c55e` → `#16a34a`)
- **Botão Copiar**: Cinza claro (`#f1f5f9`)
- **Botão Compartilhar**: Gradiente verde
- **Notificação**: Verde sólido (`#22c55e`)

### Efeitos:
- **Hover no card**: Sombra + borda verde
- **Hover nos botões**: Sobe 1px (`translateY(-1px)`)
- **Campo de texto**: Fundo cinza claro, muda para branco no focus
- **Notificação**: Animação de deslizar

### Responsivo:
- **Desktop**: Botões lado a lado
- **Mobile**: Botões empilhados (1 por linha)

---

## Fluxo Completo de Uso

### Cenário: João quer compartilhar seu link

1. **João faz login** em `/minha-area/`
2. **João já comprou 12 bilhetes** na "Rifa A"
3. **Seção aparece** com o card da "Rifa A"
4. **João clica em "Copiar Link"**
   - Link copiado: `https://site.com/r/rifa-a/?ref=ABC12DEF`
   - Notificação verde aparece
5. **João cola** o link no WhatsApp e envia para amigos
6. **OU João clica em "Compartilhar"**
   - Menu nativo abre (WhatsApp, Telegram, etc.)
   - João escolhe WhatsApp
   - Link já vem preenchido

---

## Verificar se Está Funcionando

### 1. Testar com usuário que tem < 10 bilhetes:
```bash
# Login com usuário que comprou 5 bilhetes
# Acessa /minha-area/
# ❌ Seção NÃO aparece
```

### 2. Testar com usuário que tem >= 10 bilhetes:
```bash
# Login com usuário que comprou 10+ bilhetes
# Acessa /minha-area/
# ✅ Seção APARECE com botões
```

### 3. Testar copiar:
```bash
# Clica em "Copiar Link"
# Notificação verde aparece
# Cola em qualquer lugar (Ctrl+V)
# Link completo aparece
```

### 4. Testar compartilhar (mobile):
```bash
# Abre no celular
# Clica em "Compartilhar"
# Menu nativo abre
# Escolhe WhatsApp
# Mensagem já vem pronta
```

---

## Diferenças entre os Botões

| Botão | Ação | Quando usar |
|-------|------|-------------|
| **Copiar Link** | Copia para clipboard | Desktop, quando vai colar manualmente |
| **Compartilhar** | Abre menu nativo | Mobile, quando vai compartilhar direto em app |

---

## Dados Mostrados no Card

Para cada campanha elegível:

```python
{
    'raffle_name': 'Campanha Teste',
    'clicks': 15,              # Quantas pessoas clicaram
    'inviter_bonus': 2,        # Quantos números você ganha por indicação
    'link': 'https://...'      # Link completo com código
}
```

---

## Casos Especiais

### 1. Usuário comprou 10+ mas não tem código de indicação
**Não deve acontecer**, porque:
- Código é criado automaticamente quando pagamento é aprovado
- Se quantidade >= `referral_min_purchase`

**Mas se acontecer:**
- Card não aparece (não há referral para mostrar)

### 2. Usuário comprou 5 em uma rifa e 5 em outra
```
Rifa A: 5 bilhetes → ❌ NÃO aparece botão da Rifa A
Rifa B: 5 bilhetes → ❌ NÃO aparece botão da Rifa B
Total: 10 bilhetes, mas CADA rifa tem < 10
```
**Resultado:** Seção NÃO aparece (precisa de 10+ em CADA campanha individualmente)

**Explicação:** O link de afiliado é ESPECÍFICO por campanha. João não pode divulgar o link da Rifa A se ele só comprou 5 bilhetes nela, mesmo que tenha comprado 50 bilhetes em outras campanhas.

### 3. Usuário comprou 15 bilhetes em 3 pedidos diferentes
```
Pedido 1: 5 bilhetes na Rifa A
Pedido 2: 6 bilhetes na Rifa A
Pedido 3: 4 bilhetes na Rifa A
Total: 15 bilhetes na Rifa A
```
**Resultado:** ✅ Seção APARECE (soma todos os pedidos da mesma rifa)

---

## Próximas Melhorias (Opcionais)

1. **QR Code** - Gerar QR Code do link ao lado dos botões
2. **WhatsApp direto** - Botão para abrir WhatsApp com mensagem pronta
3. **Estatísticas** - Mostrar conversão (cliques → compras)
4. **Histórico** - Ver quando cada clique aconteceu
5. **Badge de conquista** - "🏆 Top Indicador" para quem tem 5+ indicações

---

## Resumo

✅ **Seção criada** com condição de 10+ bilhetes
✅ **Botão Copiar** com notificação animada
✅ **Botão Compartilhar** com Web Share API + fallback
✅ **Design responsivo** para mobile
✅ **Múltiplas campanhas** suportadas
✅ **Compatibilidade** com navegadores antigos

**O sistema está 100% funcional!** 🚀

---

## Como Testar Rapidamente

### Via Django Shell:
```python
from raffles.models import RaffleOrder, Referral
from accounts.models import User

# Ver bilhetes do usuário
user = User.objects.get(whatsapp='5511999999999')
orders = RaffleOrder.objects.filter(user=user, status='paid')

for order in orders:
    print(f"Rifa: {order.raffle.name} - Bilhetes: {order.quantity}")

# Ver se tem código de indicação
referrals = Referral.objects.filter(inviter=user)
for ref in referrals:
    print(f"Código: {ref.code} - Rifa: {ref.raffle.name}")
```

### Via Browser:
1. Login em `/minha-area/`
2. Procurar seção "Compartilhar Link de Indicação"
3. Se aparecer → Você tem 10+ bilhetes
4. Se não aparecer → Você tem < 10 bilhetes
