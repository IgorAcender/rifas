import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_whatsapp_message_avolution(phone, message):
    """Send WhatsApp message via Avolution API (Fallback)"""
    url = f"{settings.AVOLUTION_API_URL}/message/sendText/{settings.AVOLUTION_INSTANCE_ID}"

    headers = {
        'apikey': settings.AVOLUTION_API_KEY,
        'Content-Type': 'application/json'
    }

    data = {
        'number': phone,
        'text': message
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"WhatsApp sent via Avolution to {phone}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending WhatsApp via Avolution: {e}")
        return None


def send_whatsapp_message(phone, message):
    """
    Send WhatsApp message with automatic fallback
    Priority: Evolution API -> Avolution API
    """
    # Try Evolution API first
    if settings.EVOLUTION_API_URL and settings.EVOLUTION_API_KEY:
        try:
            from notifications.evolution import send_whatsapp_message as send_evolution
            result = send_evolution(phone, message)
            if result:
                return result
            logger.warning("Evolution API failed, trying Avolution fallback...")
        except Exception as e:
            logger.error(f"Evolution API error: {e}, trying Avolution fallback...")

    # Fallback to Avolution
    if settings.AVOLUTION_API_URL and settings.AVOLUTION_API_KEY:
        return send_whatsapp_message_avolution(phone, message)

    logger.error("No WhatsApp API configured!")
    return None


def send_payment_confirmation(order):
    """Send payment confirmation with numbers"""
    numbers = sorted(order.allocated_numbers.values_list('number', flat=True))
    numbers_str = ', '.join([f"{n:04d}" for n in numbers])

    # Format draw date if available
    draw_date_str = ""
    if order.raffle.draw_date:
        draw_date_str = f"\n📅 *Data do sorteio:* {order.raffle.draw_date.strftime('%d/%m/%Y às %H:%M')}"

    message = f"""
🎉 *Pagamento Confirmado!*

Olá *{order.user.name}*!

Seu pagamento foi aprovado com sucesso!

━━━━━━━━━━━━━━━━━━━
🎫 *Rifa:* {order.raffle.name}
🏆 *Prêmio:* {order.raffle.prize_name}
{draw_date_str}

🔢 *Seus números da sorte:*
{numbers_str}

💰 *Valor pago:* R$ {order.amount}
📦 *Pedido:* #{order.id}
━━━━━━━━━━━━━━━━━━━

✅ Seus números estão reservados e concorrendo ao prêmio!

Boa sorte! 🍀✨
    """.strip()

    return send_whatsapp_message(order.user.whatsapp, message)
