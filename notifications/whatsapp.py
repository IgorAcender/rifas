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
    original_phone = phone

    # Normalize phone number - ensure it has country code
    if phone:
        # Remove all non-numeric characters
        phone = ''.join(filter(str.isdigit, phone))

        # Add Brazil country code if not present
        if not phone.startswith('55'):
            phone = '55' + phone

    logger.info(f"📱 Normalizing phone: '{original_phone}' -> '{phone}'")
    logger.info(f"📤 Sending WhatsApp to {phone}")

    # Try Evolution API first
    if settings.EVOLUTION_API_URL and settings.EVOLUTION_API_KEY:
        logger.info(f"🔄 Trying Evolution API: {settings.EVOLUTION_API_URL}")
        try:
            from notifications.evolution import send_whatsapp_message as send_evolution
            result = send_evolution(phone, message)
            if result:
                logger.info(f"✅ Evolution API success")
                return result
            logger.warning("⚠️  Evolution API failed, trying Avolution fallback...")
        except Exception as e:
            logger.error(f"❌ Evolution API error: {e}, trying Avolution fallback...")

    # Fallback to Avolution
    if settings.AVOLUTION_API_URL and settings.AVOLUTION_API_KEY:
        logger.info(f"🔄 Trying Avolution API: {settings.AVOLUTION_API_URL}")
        return send_whatsapp_message_avolution(phone, message)

    logger.error("❌ No WhatsApp API configured!")
    return None


def send_payment_confirmation(order):
    """Send payment confirmation with numbers using custom template"""
    from notifications.models import WhatsAppMessageTemplate

    # Get custom template
    template_text = WhatsAppMessageTemplate.get_default_template()

    # Prepare data for template
    numbers = sorted(order.allocated_numbers.values_list('number', flat=True))
    numbers_str = ', '.join([f"{n:04d}" for n in numbers])

    # Format draw date if available
    draw_date_str = ""
    if order.raffle.draw_date:
        draw_date_str = f"📅 *Data do sorteio:* {order.raffle.draw_date.strftime('%d/%m/%Y às %H:%M')}"

    # Verificar se ganhou algum prêmio
    prizes_message = ""
    if 'won_prizes' in order.payment_data and order.payment_data['won_prizes']:
        prizes_list = []
        for prize in order.payment_data['won_prizes']:
            prizes_list.append(f"🎁 Número *{prize['number']:04d}* - *{prize['prize_amount_formatted']}*")

        prizes_message = f"""
━━━━━━━━━━━━━━━━━━━
🏆 *PARABÉNS! VOCÊ GANHOU!* 🏆

{chr(10).join(prizes_list)}

💰 O prêmio será enviado via PIX em breve!
━━━━━━━━━━━━━━━━━━━
"""

    # Replace placeholders in template
    try:
        message = template_text.format(
            name=order.user.name,
            raffle_name=order.raffle.name,
            prize_name=order.raffle.prize_name,
            draw_date=draw_date_str,
            numbers=numbers_str,
            amount=order.amount,
            order_id=order.id
        )
        # Adicionar mensagem de prêmios se houver
        if prizes_message:
            message = message + "\n\n" + prizes_message
    except Exception as e:
        logger.error(f"Error formatting template: {e}")
        # Fallback to default message
        message = f"""
🎉 *Pagamento Confirmado!*

Olá *{order.user.name}*!

Seu pagamento foi aprovado com sucesso!

━━━━━━━━━━━━━━━━━━━
🎫 *Campanha:* {order.raffle.name}
🏆 *Prêmio:* {order.raffle.prize_name}
{draw_date_str}

🔢 *Seus números da sorte:*
{numbers_str}

💰 *Valor pago:* R$ {order.amount}
📦 *Pedido:* #{order.id}
━━━━━━━━━━━━━━━━━━━

✅ Seus números estão reservados e concorrendo ao prêmio!
{prizes_message}
Boa sorte! 🍀✨
        """.strip()

    return send_whatsapp_message(order.user.whatsapp, message)


def send_referral_share_invitation(order):
    """Send referral share invitation with user's referral link"""
    from notifications.models import WhatsAppMessageTemplate
    from raffles.models import Referral, RaffleNumber
    from django.urls import reverse
    from django.conf import settings
    import threading
    import time

    # Check if user is eligible for referral
    if not order.raffle.enable_referral:
        return None
    
    if order.quantity < order.raffle.referral_min_purchase:
        return None

    # Get delay from template settings
    template_obj = WhatsAppMessageTemplate.get_referral_share_template()
    delay_seconds = template_obj.delay_seconds if hasattr(template_obj, 'delay_seconds') else 30

    def send_delayed():
        """Internal function to send message after delay"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Wait for the configured delay
            if delay_seconds > 0:
                logger.info(f"⏳ Waiting {delay_seconds} seconds before sending referral invitation to {order.user.whatsapp}")
                time.sleep(delay_seconds)
            
            # Get or create user's referral code
            referral, created = Referral.objects.get_or_create(
                inviter=order.user,
                raffle=order.raffle
            )

            # Build referral URL
            base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            public_path = reverse('raffle_public', kwargs={'slug': order.raffle.slug})
            referral_url = f"{base_url}{public_path}?ref={referral.code}"

            # Count successful referrals
            successful_referrals = Referral.objects.filter(
                inviter=order.user,
                raffle=order.raffle,
                status=Referral.Status.REDEEMED
            ).count()

            # Count total bonus numbers earned
            total_bonus_earned = RaffleNumber.objects.filter(
                raffle=order.raffle,
                user=order.user,
                source=RaffleNumber.Source.REFERRAL_INVITER
            ).count()

            # Build progressive bonus message
            progressive_message = ""
            if order.raffle.enable_progressive_bonus:
                progressive_message = f"\n• *Bônus Progressivo:* +1 número a cada {order.raffle.progressive_bonus_every} que seu amigo comprar!"

            # Get custom template text
            template_text = template_obj.template if hasattr(template_obj, 'template') else template_obj

            # Format message with template
            try:
                message = template_text.format(
                    name=order.user.name,
                    raffle_name=order.raffle.name,
                    prize_name=order.raffle.prize_name,
                    inviter_bonus=order.raffle.inviter_bonus,
                    invitee_bonus=order.raffle.invitee_bonus,
                    progressive_message=progressive_message,
                    referral_link=referral_url,
                    successful_referrals=successful_referrals,
                    total_bonus_earned=total_bonus_earned
                )
            except Exception as e:
                logger.error(f"Error formatting referral share template: {e}")
                # Fallback to simple message
                message = f"""
🎁 *Ganhe Números Grátis Indicando Amigos!*

Olá *{order.user.name}*!

Compartilhe seu link e ganhe *{order.raffle.inviter_bonus} números grátis* a cada amigo que comprar!

🔗 *Seu link:*
{referral_url}

Seu amigo também ganha *{order.raffle.invitee_bonus} números extras*!

Quanto mais você indica, mais chances de ganhar! 🍀
                """.strip()

            # Send the message
            result = send_whatsapp_message(order.user.whatsapp, message)
            if result:
                logger.info(f"✅ Referral invitation sent successfully to {order.user.whatsapp} (after {delay_seconds}s delay)")
                
                # Now trigger the copy-paste message (will be sent 5s later)
                logger.info(f"🚀 Scheduling copy-paste message for {order.user.whatsapp}")
                send_referral_copy_paste(order)
            else:
                logger.error(f"❌ Failed to send referral invitation to {order.user.whatsapp}")
                
        except Exception as e:
            logger.error(f"❌ Error in delayed referral invitation: {e}", exc_info=True)

    # Start background thread to send after delay
    thread = threading.Thread(target=send_delayed, daemon=True)
    thread.start()
    
    return True  # Return immediately, message will be sent in background


def send_prize_won_notification(user, raffle, prize_number, prize_amount):
    """
    Send immediate notification when user wins a prize number
    """
    message = f"""
🏆🎊 *PARABÉNS, VOCÊ GANHOU UM PRÊMIO!* 🎊🏆

Olá *{user.name}*!

🎉 Você acabou de ganhar um NÚMERO PREMIADO na campanha *{raffle.name}*!

━━━━━━━━━━━━━━━━━━━
🎁 *Número Premiado:* {prize_number:04d}
💰 *Valor do Prêmio:* R$ {prize_amount:.2f}
━━━━━━━━━━━━━━━━━━━

🤑 O prêmio será enviado via PIX em até 24 horas!

🍀 Continue participando e concorrendo ao prêmio principal: *{raffle.prize_name}*!

✨ Boa sorte! ✨
    """.strip()

    try:
        result = send_whatsapp_message(user.whatsapp, message)
        if result:
            logger.info(f"🏆 Prize notification sent to {user.name} - Prize: R$ {prize_amount}")

        # Send notifications to admins and groups
        send_prize_admin_notifications(user, raffle, prize_number, prize_amount)

        return result
    except Exception as e:
        logger.error(f"❌ Error sending prize notification to {user.name}: {e}")
        return None


def send_prize_admin_notifications(user, raffle, prize_number, prize_amount):
    """
    Send prize won notifications to all configured admins and groups
    """
    from raffles.models import SiteConfiguration
    from .models import WhatsAppMessageTemplate

    # Get templates
    admin_template = WhatsAppMessageTemplate.get_prize_admin_template()
    group_template = WhatsAppMessageTemplate.get_prize_group_template()

    # Format admin message
    admin_message = admin_template.format(
        raffle_name=raffle.name,
        prize_number=f"{prize_number:04d}",
        prize_amount=f"{prize_amount:.2f}",
        user_name=user.name,
        user_whatsapp=user.whatsapp
    ).strip()

    # Format group message
    group_message = group_template.format(
        raffle_name=raffle.name,
        prize_number=f"{prize_number:04d}",
        prize_amount=f"{prize_amount:.2f}",
        user_name=user.name
    ).strip()

    # Get admin phones and group IDs
    admin_phones = SiteConfiguration.get_admin_phones()
    group_phones = SiteConfiguration.get_group_phones()

    # Send to all admin phones
    for phone in admin_phones:
        try:
            result = send_whatsapp_message(phone, admin_message)
            if result:
                logger.info(f"✅ Prize admin notification sent to {phone}")
            else:
                logger.error(f"❌ Failed to send prize admin notification to {phone}")
        except Exception as e:
            logger.error(f"❌ Error sending prize admin notification to {phone}: {e}")

    # Send to all groups
    for group_id in group_phones:
        try:
            result = send_whatsapp_message(group_id, group_message)
            if result:
                logger.info(f"✅ Prize group notification sent to {group_id}")
            else:
                logger.error(f"❌ Failed to send prize group notification to {group_id}")
        except Exception as e:
            logger.error(f"❌ Error sending prize group notification to {group_id}: {e}")


def send_referral_copy_paste(order):
    """Send copy-paste ready referral message (3rd message)"""
    from notifications.models import WhatsAppMessageTemplate
    from raffles.models import Referral
    from django.urls import reverse
    from django.conf import settings
    import threading
    import time

    # Check if user is eligible for referral
    if not order.raffle.enable_referral:
        return None
    
    if order.quantity < order.raffle.referral_min_purchase:
        return None

    # Get delay from template settings (defaults to 5 seconds)
    template_obj = WhatsAppMessageTemplate.get_referral_copy_paste_template()
    delay_seconds = template_obj.delay_seconds if hasattr(template_obj, 'delay_seconds') else 5

    def send_delayed():
        """Internal function to send message after delay"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Wait for the configured delay (5 seconds after message 2)
            if delay_seconds > 0:
                logger.info(f"⏳ Waiting {delay_seconds} seconds before sending copy-paste message to {order.user.whatsapp}")
                time.sleep(delay_seconds)
            
            # Get user's referral code (should already exist from previous message)
            try:
                referral = Referral.objects.get(
                    inviter=order.user,
                    raffle=order.raffle
                )
            except Referral.DoesNotExist:
                logger.error(f"❌ Referral not found for user {order.user.id} in raffle {order.raffle.id}")
                return

            # Build referral URL
            base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            public_path = reverse('raffle_public', kwargs={'slug': order.raffle.slug})
            referral_url = f"{base_url}{public_path}?ref={referral.code}"

            # Get custom template text
            template_text = template_obj.template if hasattr(template_obj, 'template') else template_obj

            # Format message with template
            try:
                message = template_text.format(
                    raffle_name=order.raffle.name,
                    prize_name=order.raffle.prize_name,
                    invitee_bonus=order.raffle.invitee_bonus,
                    referral_link=referral_url
                )
            except Exception as e:
                logger.error(f"Error formatting copy-paste template: {e}")
                # Fallback to simple message
                message = f"""
🎁 Participe e Ganhe {order.raffle.invitee_bonus} Números Grátis!

Olá! Estou participando da campanha *{order.raffle.name}* e quero te convidar!

🏆 Prêmio: *{order.raffle.prize_name}*

🎁 *Você ganha {order.raffle.invitee_bonus} números extras* só por usar meu link!

🔗 *Clique aqui para participar:*
{referral_url}

Boa sorte! 🍀✨
                """.strip()

            # Send the message
            result = send_whatsapp_message(order.user.whatsapp, message)
            if result:
                logger.info(f"✅ Copy-paste message sent successfully to {order.user.whatsapp} (after {delay_seconds}s delay)")
            else:
                logger.error(f"❌ Failed to send copy-paste message to {order.user.whatsapp}")
                
        except Exception as e:
            logger.error(f"❌ Error in delayed copy-paste message: {e}", exc_info=True)

    # Start background thread to send after delay
    thread = threading.Thread(target=send_delayed, daemon=True)
    thread.start()
    
    return True  # Return immediately, message will be sent in background

