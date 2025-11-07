import requests
from django.conf import settings


def send_whatsapp_message(phone, message):
    """Send WhatsApp message via Avolution API"""
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
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending WhatsApp: {e}")
        return None


def send_payment_confirmation(order):
    """Send payment confirmation with numbers"""
    numbers = sorted(order.allocated_numbers.values_list('number', flat=True))
    numbers_str = ', '.join([f"{n:04d}" for n in numbers])

    message = f"""
🎉 *Pagamento Confirmado!*

Rifa: *{order.raffle.name}*
Seus números: {numbers_str}

Boa sorte! 🍀
    """.strip()

    return send_whatsapp_message(order.user.whatsapp, message)
