from django.db import models


class WhatsAppMessageTemplate(models.Model):
    """Template for WhatsApp payment confirmation messages"""
    name = models.CharField(max_length=100, default="payment_confirmation", unique=True)
    template = models.TextField(
        help_text="Use placeholders: {name}, {raffle_name}, {prize_name}, {draw_date}, {numbers}, {amount}, {order_id}, {customer_area_url}"
    )
    delay_seconds = models.IntegerField(
        'Delay (segundos)',
        default=0,
        help_text='Tempo de espera antes de enviar a mensagem (em segundos)'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "WhatsApp Message Template"
        verbose_name_plural = "WhatsApp Message Templates"

    def __str__(self):
        return self.name

    @classmethod
    def get_default_template(cls):
        """Get or create default payment confirmation template"""
        default_template = """🎉 *Pagamento Confirmado!*

Olá *{name}*!

Seu pagamento foi aprovado com sucesso!

━━━━━━━━━━━━━━━━━━━
🎫 *Rifa:* {raffle_name}
🏆 *Prêmio:* {prize_name}
{draw_date}

🔢 *Seus números da sorte:*
{numbers}

💰 *Valor pago:* R$ {amount}
📦 *Pedido:* #{order_id}
━━━━━━━━━━━━━━━━━━━

✅ Seus números estão reservados e concorrendo ao prêmio!

🔗 *Acompanhe aqui:* {customer_area_url}

Boa sorte! 🍀✨"""

        template, created = cls.objects.get_or_create(
            name="payment_confirmation",
            defaults={"template": default_template}
        )
        return template.template

    @classmethod
    def get_referral_bonus_template(cls):
        """Get or create referral bonus notification template"""
        default_template = """🎉 *Parabéns! Indicação Confirmada!* 🎉

Olá *{inviter_name}*!

Ótima notícia! *{invitee_name}* acabou de concluir a compra usando seu link de indicação!

━━━━━━━━━━━━━━━━━━━
🎫 *Campanha:* {raffle_name}
👤 *Quem comprou:* {invitee_name}
💰 *Quantidade:* {invitee_quantity} números

🎁 *Você ganhou {total_bonus} números grátis!*
({bonus_breakdown})

🔢 *Seus números de bônus:*
{bonus_numbers}
━━━━━━━━━━━━━━━━━━━

✨ Continue indicando amigos e ganhe mais números!
Cada indicação bem-sucedida te dá mais chances de ganhar! 🍀"""

        template, created = cls.objects.get_or_create(
            name="referral_bonus_notification",
            defaults={"template": default_template}
        )
        return template.template

    @classmethod
    def get_referral_share_template(cls):
        """Get or create referral share invitation template"""
        default_template = """🎁 *Como Funciona o Programa de Indicações* 🎁

Olá *{name}*!

Você sabia que pode ganhar *{inviter_bonus} números grátis* a cada amigo que comprar usando seu link?

━━━━━━━━━━━━━━━━━━━
🎫 *Campanha:* {raffle_name}
🏆 *Prêmio:* {prize_name}

🎁 *Vantagens:*
• Seu amigo ganha *{invitee_bonus} números extras*
• Você ganha *{inviter_bonus} números grátis*{progressive_message}
• Quanto mais indicar, mais chances de ganhar!

📊 *Suas indicações até agora:*
• {successful_referrals} pessoas já compraram com seu link
• {total_bonus_earned} números de bônus ganhos
━━━━━━━━━━━━━━━━━━━

� *Envie a mensagem abaixo para seus amigos!*
Ela já vem pronta com seu link personalizado.

Aguarde alguns segundos que vou enviar... 🚀"""

        template, created = cls.objects.get_or_create(
            name="referral_share_invitation",
            defaults={"template": default_template, "delay_seconds": 30}
        )
        return template

    @classmethod
    def get_referral_share_delay(cls):
        """Get delay in seconds for referral share invitation"""
        template = cls.objects.filter(name="referral_share_invitation").first()
        return template.delay_seconds if template else 30

    @classmethod
    def get_referral_copy_paste_template(cls):
        """Get or create referral copy-paste message template (ready to forward)"""
        default_template = """🎁 *Participe e Ganhe {invitee_bonus} Números Grátis!*

Olá! Estou participando da campanha *{raffle_name}* e quero te convidar!

🏆 Prêmio: *{prize_name}*

🎁 *Você ganha {invitee_bonus} números extras* só por usar meu link!

🔗 *Clique aqui para participar:*
{referral_link}

Boa sorte! 🍀✨"""

        template, created = cls.objects.get_or_create(
            name="referral_copy_paste",
            defaults={"template": default_template, "delay_seconds": 5}
        )
        return template

    @classmethod
    def get_prize_admin_template(cls):
        """Get or create prize notification template for admins"""
        default_template = """🎯 *NÚMERO PREMIADO SORTEADO!*

Um número premiado acabou de ser sorteado na campanha *{raffle_name}*!

━━━━━━━━━━━━━━━━━━━
🎫 *Campanha:* {raffle_name}
🎁 *Número Premiado:* {prize_number}
💰 *Valor do Prêmio:* R$ {prize_amount}

👤 *Ganhador:*
• Nome: {user_name}
• WhatsApp: {user_whatsapp}
━━━━━━━━━━━━━━━━━━━

💳 Providenciar pagamento via PIX em até 24 horas."""

        template, created = cls.objects.get_or_create(
            name="prize_admin_notification",
            defaults={"template": default_template}
        )
        return template.template

    @classmethod
    def get_prize_group_template(cls):
        """Get or create prize notification template for groups"""
        default_template = """🏆🎊 *TEMOS UM GANHADOR!* 🎊🏆

Número premiado foi sorteado na campanha *{raffle_name}*!

━━━━━━━━━━━━━━━━━━━
🎁 *Número Premiado:* {prize_number}
💰 *Valor do Prêmio:* R$ {prize_amount}

👤 *Ganhador:* {user_name}
━━━━━━━━━━━━━━━━━━━

🎉 Parabéns ao sortudo! Continue participando!"""

        template, created = cls.objects.get_or_create(
            name="prize_group_notification",
            defaults={"template": default_template}
        )
        return template.template

    @classmethod
    def get_prize_winner_template(cls):
        """Get or create prize notification template for the winner"""
        default_template = """🏆🎊 *PARABÉNS, VOCÊ GANHOU UM PRÊMIO!* 🎊🏆

Olá *{user_name}*!

🎉 Você acabou de ganhar um NÚMERO PREMIADO na campanha *{raffle_name}*!

━━━━━━━━━━━━━━━━━━━
🎁 *Número Premiado:* {prize_number}
💰 *Valor do Prêmio:* R$ {prize_amount}
━━━━━━━━━━━━━━━━━━━

🤑 O prêmio será enviado via PIX em até 24 horas!

🍀 Continue participando e concorrendo ao prêmio principal: *{prize_name}*!

✨ Boa sorte! ✨"""

        template, created = cls.objects.get_or_create(
            name="prize_winner_notification",
            defaults={"template": default_template}
        )
        return template.template
