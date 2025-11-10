import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EvolutionAPI:
    """Evolution API WhatsApp Integration"""

    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance_name = settings.EVOLUTION_INSTANCE_NAME

    def _get_headers(self):
        """Get API headers"""
        return {
            'apikey': self.api_key,
            'Content-Type': 'application/json'
        }

    def send_text_message(self, phone, message):
        """
        Send text message via Evolution API

        Args:
            phone (str): Phone number with country code (e.g., '5511999999999')
            message (str): Message text to send

        Returns:
            dict: API response or None if error
        """
        url = f"{self.base_url}/message/sendText/{self.instance_name}"

        # Ensure phone is in correct format
        if not phone.endswith('@s.whatsapp.net'):
            phone = f"{phone}@s.whatsapp.net"

        payload = {
            'number': phone,
            'text': message
        }

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            logger.info(f"WhatsApp message sent successfully to {phone}")
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout sending WhatsApp to {phone}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp to {phone}: {e}")
            return None

    def send_media_message(self, phone, media_url, caption=''):
        """
        Send media message (image, video, etc.)

        Args:
            phone (str): Phone number with country code
            media_url (str): URL of the media file
            caption (str): Optional caption for the media

        Returns:
            dict: API response or None if error
        """
        url = f"{self.base_url}/message/sendMedia/{self.instance_name}"

        if not phone.endswith('@s.whatsapp.net'):
            phone = f"{phone}@s.whatsapp.net"

        payload = {
            'number': phone,
            'mediatype': 'image',
            'media': media_url,
            'caption': caption
        }

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            logger.info(f"WhatsApp media sent successfully to {phone}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp media to {phone}: {e}")
            return None

    def check_instance_status(self):
        """
        Check if Evolution API instance is connected

        Returns:
            dict: Instance status or None if error
        """
        url = f"{self.base_url}/instance/connectionState/{self.instance_name}"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking Evolution API status: {e}")
            return None


# Singleton instance
evolution_api = EvolutionAPI()


def send_whatsapp_message(phone, message):
    """
    Send WhatsApp message using Evolution API
    Wrapper function to maintain compatibility with existing code

    Args:
        phone (str): Phone number with country code
        message (str): Message text

    Returns:
        dict: API response or None if error
    """
    return evolution_api.send_text_message(phone, message)


def send_payment_confirmation(order):
    """
    Send payment confirmation with allocated numbers

    Args:
        order: RaffleOrder instance

    Returns:
        dict: API response or None if error
    """
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


def send_winner_notification(raffle, winner_number):
    """
    Send winner notification

    Args:
        raffle: Raffle instance
        winner_number: AllocatedNumber instance (winner)

    Returns:
        dict: API response or None if error
    """
    message = f"""
🏆 *PARABÉNS! VOCÊ GANHOU!*

Rifa: *{raffle.name}*
Número sorteado: *{winner_number.number:04d}*

Entraremos em contato para entregar seu prêmio! 🎁
    """.strip()

    return send_whatsapp_message(winner_number.order.user.whatsapp, message)
