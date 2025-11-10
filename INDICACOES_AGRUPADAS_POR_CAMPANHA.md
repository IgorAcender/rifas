# ✅ Indicações Agrupadas por Campanha

## O que mudou

A seção "Minhas Indicações" agora mostra as pessoas que usaram seu link **agrupadas por campanha**, com estatísticas individuais para cada uma.

---

## Visual Novo

### Antes (lista única):
```
Minhas Indicações
─────────────────────
👤 Maria Silva
   Campanha A • 10/11/2025
   ✅ Resgatou seu bilhete

👤 Pedro Santos
   Campanha B • 09/11/2025
   ✅ Resgatou seu bilhete

👤 João Costa
   Campanha A • 08/11/2025
   ✅ Resgatou seu bilhete
```

### Agora (agrupado por campanha):
```
┌─────────────────────────────────────────────────────────────┐
│ Campanha A                                     🎯 Ativa     │
│ 2 indicações • 4 números bônus ganhos                       │
├─────────────────────────────────────────────────────────────┤
│ 👤 Maria Silva                                              │
│    5511999999999 • 10/11/2025  ✅ Resgatou seu bilhete     │
│                                                             │
│ 👤 João Costa                                               │
│    5511888888888 • 08/11/2025  ✅ Resgatou seu bilhete     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Campanha B                                     🎯 Ativa     │
│ 1 indicação • 2 números bônus ganhos                        │
├─────────────────────────────────────────────────────────────┤
│ 👤 Pedro Santos                                             │
│    5511777777777 • 09/11/2025  ✅ Resgatou seu bilhete     │
└─────────────────────────────────────────────────────────────┘
```

---

## Informações Exibidas

### Por campanha:
- **Nome da campanha**
- **Status da campanha** (Ativa, Finalizada, etc.)
- **Total de indicações** nessa campanha específica
- **Números bônus ganhos** nessa campanha específica

### Por pessoa (dentro de cada campanha):
- **Nome** do indicado
- **WhatsApp** do indicado
- **Data** que completou a compra
- **Badge de confirmação**: ✅ Resgatou seu bilhete

---

## Implementação Backend

### `accounts/views.py`

```python
# Buscar todas as indicações bem-sucedidas
all_referrals = Referral.objects.filter(
    inviter=request.user,
    status=Referral.Status.REDEEMED
).select_related('invitee', 'raffle').order_by('raffle', '-redeemed_at')

# Agrupar por campanha usando defaultdict
referrals_by_raffle = defaultdict(list)
for referral in all_referrals:
    referrals_by_raffle[referral.raffle].append(referral)

# Criar estrutura para o template
my_referrals_grouped = []
for raffle, referrals in referrals_by_raffle.items():
    # Contar números bônus DESTA campanha específica
    bonus_count = RaffleNumber.objects.filter(
        user=request.user,
        raffle=raffle,
        source=RaffleNumber.Source.REFERRAL_INVITER
    ).count()

    my_referrals_grouped.append({
        'raffle': raffle,              # Objeto da campanha
        'referrals': referrals,        # Lista de indicações
        'count': len(referrals),       # Total de indicações
        'bonus_numbers': bonus_count   # Números bônus ganhos
    })
```

**Estrutura de dados:**
```python
my_referrals_grouped = [
    {
        'raffle': <Raffle: Campanha A>,
        'referrals': [
            <Referral: Maria>,
            <Referral: João>
        ],
        'count': 2,
        'bonus_numbers': 4
    },
    {
        'raffle': <Raffle: Campanha B>,
        'referrals': [
            <Referral: Pedro>
        ],
        'count': 1,
        'bonus_numbers': 2
    }
]
```

---

## Template HTML

```html
{% for group in my_referrals_grouped %}
<div class="campaign-referral-group">
    <!-- Cabeçalho da campanha (roxo) -->
    <div class="campaign-header">
        <div class="campaign-title">
            <h3>{{ group.raffle.name }}</h3>
            <span class="campaign-stats">
                {{ group.count }} indicações •
                {{ group.bonus_numbers }} números bônus ganhos
            </span>
        </div>
        <div class="campaign-badge">
            🎯 {{ group.raffle.get_status_display }}
        </div>
    </div>

    <!-- Lista de pessoas que usaram o link -->
    <div class="referrals-list">
        {% for referral in group.referrals %}
        <div class="referral-card">
            <div class="referral-avatar">👤</div>
            <div class="referral-info">
                <div class="referral-name">{{ referral.invitee.name }}</div>
                <div class="referral-details">
                    <span>{{ referral.invitee.whatsapp }}</span>
                    <span>•</span>
                    <span>{{ referral.redeemed_at|date:"d/m/Y" }}</span>
                </div>
            </div>
            <div class="referral-badge">
                ✅ Resgatou seu bilhete
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endfor %}
```

---

## Estilos CSS

### Cabeçalho da campanha:
```css
.campaign-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: white;
}
```

### Cards de pessoas:
```css
.referral-card {
    background: #f8fafc;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 16px;
}

.referral-card:hover {
    background: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border-color: #667eea;
}
```

---

## Exemplo Prático

### João tem indicações em 3 campanhas:

**Campanha "Rifa do Carro":**
- Maria comprou em 10/11/2025
- Pedro comprou em 09/11/2025
- Carlos comprou em 08/11/2025
- **Total:** 3 indicações, 6 números bônus

**Campanha "Rifa da Moto":**
- Ana comprou em 07/11/2025
- **Total:** 1 indicação, 2 números bônus

**Campanha "Rifa do Celular":**
- Lucas comprou em 06/11/2025
- Julia comprou em 05/11/2025
- **Total:** 2 indicações, 4 números bônus

### O que João vê:

```
┌─────────────────────────────────────────────────────────────┐
│ Rifa do Carro                                  🎯 Ativa     │
│ 3 indicações • 6 números bônus ganhos                       │
├─────────────────────────────────────────────────────────────┤
│ 👤 Maria Silva        5511999999999 • 10/11/2025           │
│ 👤 Pedro Santos       5511888888888 • 09/11/2025           │
│ 👤 Carlos Oliveira    5511777777777 • 08/11/2025           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Rifa da Moto                                   🎯 Ativa     │
│ 1 indicação • 2 números bônus ganhos                        │
├─────────────────────────────────────────────────────────────┤
│ 👤 Ana Costa          5511666666666 • 07/11/2025           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Rifa do Celular                                🎯 Ativa     │
│ 2 indicações • 4 números bônus ganhos                       │
├─────────────────────────────────────────────────────────────┤
│ 👤 Lucas Ferreira     5511555555555 • 06/11/2025           │
│ 👤 Julia Almeida      5511444444444 • 05/11/2025           │
└─────────────────────────────────────────────────────────────┘
```

---

## Vantagens do Agrupamento

### 1. **Organização clara**
- Fácil ver quantas indicações em cada campanha
- Estatísticas separadas por campanha

### 2. **Acompanhamento de desempenho**
- Ver qual campanha está gerando mais indicações
- Comparar números bônus entre campanhas

### 3. **Informação completa**
- Nome + WhatsApp de cada indicado
- Data exata da compra
- Status da campanha

### 4. **Melhor UX**
- Não precisa procurar pela campanha
- Visão geral imediata de cada campanha
- Cards organizados e fáceis de ler

---

## Ordenação

### Campanhas:
- Ordenadas pela **ordem em que aparecem** no banco de dados
- Pode ser customizado para ordenar por:
  - Mais indicações primeiro
  - Mais recente primeiro
  - Alfabética

### Pessoas (dentro de cada campanha):
- Ordenadas por **data de resgate** (mais recente primeiro)
- Última pessoa que comprou aparece no topo

---

## Responsividade

### Desktop:
- Cabeçalho horizontal (título à esquerda, badge à direita)
- Cards de pessoas compactos

### Mobile:
- Cabeçalho vertical (badge abaixo do título)
- Cards de pessoas empilhados
- Badge ocupa largura total

---

## Estado Vazio

Se não houver indicações em nenhuma campanha:

```
┌─────────────────────────────────────────────────────────────┐
│                        🔗                                   │
│                                                             │
│              Nenhuma indicação ainda                        │
│                                                             │
│  Compartilhe seu link de indicação após fazer uma          │
│  compra e ganhe números grátis!                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Dados Retornados

Para cada grupo de campanha:

```python
{
    'raffle': Raffle object,           # Objeto completo da campanha
    'referrals': [Referral objects],   # Lista de indicações
    'count': 3,                        # Total de indicações
    'bonus_numbers': 6                 # Números bônus DESTA campanha
}
```

Para cada indicação:

```python
{
    'invitee': User object,            # Pessoa que comprou
    'redeemed_at': datetime,           # Quando completou compra
    'raffle': Raffle object,           # Campanha (já vem do grupo)
}
```

---

## Queries no Banco

### Total de queries:
```
1. Buscar todas as indicações do usuário
2. Para cada campanha única:
   - Contar números bônus dessa campanha
```

**Otimização:**
- Usa `select_related('invitee', 'raffle')` para evitar N+1 queries
- Usa `defaultdict` para agrupar em memória (rápido)

---

## Customizações Futuras

### Possíveis melhorias:

1. **Ordenação customizada**
   ```python
   # Ordenar por quantidade de indicações (maior primeiro)
   my_referrals_grouped.sort(key=lambda x: x['count'], reverse=True)
   ```

2. **Filtros**
   - Mostrar apenas campanhas ativas
   - Esconder campanhas sem indicações

3. **Estatísticas extras**
   - Média de indicações por campanha
   - Taxa de conversão (cliques → compras)

4. **Ações por campanha**
   - Botão para compartilhar link daquela campanha
   - Ver detalhes da campanha

---

## Resumo

✅ **Indicações agrupadas** por campanha
✅ **Estatísticas individuais** para cada campanha
✅ **Lista completa** de pessoas que usaram o link
✅ **Informações detalhadas**: Nome, WhatsApp, Data
✅ **Design limpo** com cabeçalho roxo degradê
✅ **Responsivo** para mobile
✅ **Performance otimizada** com select_related

**O sistema está pronto para usar!** 🚀
