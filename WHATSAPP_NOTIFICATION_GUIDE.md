# Guia de Notificações WhatsApp - Sistema de Rifas

## 📱 Como Funciona

O sistema está configurado para enviar mensagens automáticas via WhatsApp quando um pagamento é aprovado no MercadoPago.

### Fluxo Completo

```
1. Cliente faz compra → Seleciona números
2. Gera pagamento PIX → MercadoPago
3. Cliente paga → MercadoPago detecta pagamento
4. MercadoPago envia webhook → Seu servidor
5. Sistema marca pedido como pago
6. Sistema envia WhatsApp AUTOMATICAMENTE → Cliente recebe confirmação
```

## 🎯 Mensagem Enviada

Quando o pagamento for aprovado, o cliente receberá automaticamente no WhatsApp cadastrado:

```
🎉 *Pagamento Confirmado!*

Olá *[Nome do Cliente]*!

Seu pagamento foi aprovado com sucesso!

━━━━━━━━━━━━━━━━━━━
🎫 *Rifa:* [Nome da Rifa]
🏆 *Prêmio:* [Nome do Prêmio]
📅 *Data do sorteio:* [Data e Hora]

🔢 *Seus números da sorte:*
0001, 0002, 0003, 0004, 0005

💰 *Valor pago:* R$ XX,XX
📦 *Pedido:* #123
━━━━━━━━━━━━━━━━━━━

✅ Seus números estão reservados e concorrendo ao prêmio!

Boa sorte! 🍀✨
```

## ⚙️ Configuração Necessária

### 1. Configure a Evolution API

Adicione no arquivo `.env`:

```bash
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua-api-key-aqui
EVOLUTION_INSTANCE_NAME=nome-da-sua-instancia
```

### 2. Verifique a Configuração

```bash
# Execute o script de teste
python test_evolution.py

# Opção 1: Testar conexão
# Opção 2: Enviar mensagem de teste
```

### 3. Certifique-se que o Webhook está Configurado

O MercadoPago precisa estar configurado para enviar webhooks para:
```
https://seu-dominio.com/api/payments/mercadopago/webhook/
```

## 🔄 Sistema de Fallback

O sistema possui redundância automática:

1. **Primeira tentativa**: Evolution API
2. **Se Evolution falhar**: Avolution API (fallback automático)

Você pode manter ambas as APIs configuradas para máxima confiabilidade!

## 📝 Onde Está Implementado

### Arquivo: `payments/views.py` (Linhas 140-145)

```python
# Quando pagamento é aprovado
if payment_data["status"] == "approved" and order.status != RaffleOrder.Status.PAID:
    order.mark_as_paid()

    # Envia WhatsApp automaticamente
    from notifications.whatsapp import send_payment_confirmation
    try:
        send_payment_confirmation(order)
    except Exception as e:
        print(f"Error sending WhatsApp notification: {e}")
```

### Arquivo: `notifications/whatsapp.py`

Contém a função `send_payment_confirmation(order)` que:
- Busca os números alocados para o pedido
- Formata a mensagem com todas as informações
- Envia para o WhatsApp do usuário (Evolution API → Avolution API)

### Arquivo: `notifications/evolution.py`

Contém a integração completa com Evolution API:
- `send_text_message()` - Enviar mensagens de texto
- `send_media_message()` - Enviar imagens/vídeos
- `check_instance_status()` - Verificar conexão
- `send_payment_confirmation()` - Confirmação de pagamento
- `send_winner_notification()` - Notificação de ganhador

## 🧪 Como Testar

### Teste Manual Completo

1. **Configure Evolution API** no `.env`

2. **Teste a conexão:**
   ```bash
   python test_evolution.py
   ```

3. **Teste o fluxo completo:**
   - Acesse o sistema como usuário
   - Escolha uma rifa
   - Faça uma compra
   - Gere PIX no MercadoPago
   - Pague o PIX
   - Aguarde aprovação (geralmente instantâneo)
   - Verifique se recebeu WhatsApp no número cadastrado

### Teste via Django Shell

```bash
python manage.py shell
```

```python
# Importar funções
from raffles.models import RaffleOrder
from notifications.whatsapp import send_payment_confirmation

# Pegar um pedido de exemplo
order = RaffleOrder.objects.filter(status='paid').first()

# Enviar mensagem de teste
send_payment_confirmation(order)
```

### Teste Direto da Evolution API

```python
from notifications.evolution import send_whatsapp_message

# Enviar mensagem de teste
send_whatsapp_message('5511999999999', 'Teste de mensagem!')
```

## 📊 Dados Enviados na Mensagem

A mensagem inclui automaticamente:

| Campo | Fonte | Exemplo |
|-------|-------|---------|
| Nome do cliente | `order.user.name` | "João Silva" |
| Nome da rifa | `order.raffle.name` | "iPhone 15 Pro Max" |
| Nome do prêmio | `order.raffle.prize_name` | "iPhone 15 Pro Max 256GB" |
| Data do sorteio | `order.raffle.draw_date` | "25/12/2024 às 20:00" |
| Números da sorte | `order.allocated_numbers` | "0001, 0002, 0003" |
| Valor pago | `order.amount` | "R$ 10,00" |
| Número do pedido | `order.id` | "#123" |
| WhatsApp destino | `order.user.whatsapp` | "5511999999999" |

## 🛠️ Personalizar a Mensagem

Para personalizar a mensagem, edite o arquivo `notifications/whatsapp.py`, função `send_payment_confirmation()`:

```python
def send_payment_confirmation(order):
    # ... código existente ...

    message = f"""
    Sua mensagem personalizada aqui!

    Use {order.user.name} para nome
    Use {order.raffle.name} para rifa
    Use {numbers_str} para números

    Formatação WhatsApp:
    *negrito*
    _itálico_
    ~riscado~
    ```código```
    """.strip()

    return send_whatsapp_message(order.user.whatsapp, message)
```

## 🔍 Logs e Monitoramento

O sistema registra logs automáticos:

```python
# Logs de sucesso
"WhatsApp message sent successfully to 5511999999999"
"WhatsApp sent via Avolution to 5511999999999"

# Logs de erro
"Error sending WhatsApp to 5511999999999: [erro]"
"Evolution API failed, trying Avolution fallback..."
"No WhatsApp API configured!"
```

Para ver logs em tempo real durante desenvolvimento:

```bash
# No terminal onde o Django está rodando
python manage.py runserver

# Você verá os logs aparecerem quando mensagens forem enviadas
```

## ⚠️ Troubleshooting

### Mensagem não chega

**Checklist:**

1. ✅ Evolution API está configurada corretamente no `.env`?
2. ✅ Instância Evolution está conectada ao WhatsApp?
3. ✅ Número do usuário está cadastrado com código do país? (ex: 5511999999999)
4. ✅ Webhook do MercadoPago está configurado?
5. ✅ Pagamento foi realmente aprovado?
6. ✅ Verifique os logs do servidor

### Testar webhook do MercadoPago

O webhook do MercadoPago só funciona em produção (HTTPS). Para testar localmente:

```bash
# Use ngrok para criar túnel HTTPS
ngrok http 8000

# Configure o webhook do MercadoPago para:
https://seu-ngrok-url.ngrok.io/api/payments/mercadopago/webhook/
```

### Mensagem com erro de formatação

O WhatsApp usa formatação markdown:
- `*texto*` = negrito
- `_texto_` = itálico
- `~texto~` = riscado

Se a mensagem não aparecer formatada, verifique se usou os caracteres corretos.

## 🚀 Próximas Melhorias (Opcional)

### 1. Adicionar Imagem do Prêmio

```python
from notifications.evolution import evolution_api

# Enviar texto + imagem
evolution_api.send_media_message(
    phone=order.user.whatsapp,
    media_url='https://url-da-imagem.com/premio.jpg',
    caption='Seu prêmio: iPhone 15 Pro Max!'
)
```

### 2. Mensagem quando Rifa Finaliza

```python
# Em raffles/models.py, adicionar no método que finaliza a rifa
from notifications.whatsapp import send_whatsapp_message

# Enviar para todos os participantes
for order in self.orders.filter(status='paid'):
    send_whatsapp_message(
        order.user.whatsapp,
        f"A rifa {self.name} foi finalizada! Sorteio em breve!"
    )
```

### 3. Lembrete de Sorteio (1 dia antes)

Implementar usando Celery (já está no projeto):

```python
# notifications/tasks.py
from celery import shared_task

@shared_task
def send_draw_reminders():
    tomorrow = timezone.now() + timedelta(days=1)
    raffles = Raffle.objects.filter(
        draw_date__date=tomorrow.date(),
        status='active'
    )

    for raffle in raffles:
        for order in raffle.orders.filter(status='paid'):
            send_whatsapp_message(
                order.user.whatsapp,
                f"Amanhã é o sorteio da rifa {raffle.name}! Boa sorte!"
            )
```

## 📞 Números de Teste

Para testar sem enviar para clientes reais:

1. Use o número do admin configurado em `ADMIN_WHATSAPP`
2. Crie pedidos de teste com seu próprio número
3. Use o script `test_evolution.py`

## ✅ Checklist de Deploy

Antes de colocar em produção:

- [ ] Evolution API configurada e testada
- [ ] Mensagem de teste enviada e recebida
- [ ] Webhook MercadoPago configurado (HTTPS)
- [ ] Variáveis de ambiente configuradas no servidor
- [ ] Fallback para Avolution API configurado (opcional)
- [ ] Logs configurados para monitoramento
- [ ] Teste completo: compra → pagamento → WhatsApp

## 🎉 Pronto!

Seu sistema está configurado para enviar mensagens WhatsApp automaticamente quando o pagamento for aprovado!

**Não precisa fazer nada manualmente** - o sistema cuida de tudo automaticamente. 🚀
