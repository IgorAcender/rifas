from django.db import models


class WhatsAppMessageTemplate(models.Model):
    """Template for WhatsApp payment confirmation messages"""
    name = models.CharField(max_length=100, default="payment_confirmation", unique=True)
    template = models.TextField(
        help_text="Use placeholders: {name}, {raffle_name}, {prize_name}, {draw_date}, {numbers}, {amount}, {order_id}"
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
