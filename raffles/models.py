import random
import string
from django.db import models, transaction
from django.core.exceptions import ValidationError
from accounts.models import User


def generate_referral_code():
    """Generate unique referral code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class Raffle(models.Model):
    """Raffle model"""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Rascunho'
        ACTIVE = 'active', 'Ativa'
        FINISHED = 'finished', 'Finalizada'
        CANCELLED = 'cancelled', 'Cancelada'

    name = models.CharField('Nome', max_length=200)
    description = models.TextField('Descrição', blank=True)
    prize_name = models.CharField('Nome do Prêmio', max_length=200)
    prize_description = models.TextField('Descrição do Prêmio', blank=True)
    prize_image_base64 = models.TextField('Imagem do Prêmio (Base64)', blank=True)

    total_numbers = models.PositiveIntegerField('Total de Números')
    price_per_number = models.DecimalField('Preço por Número', max_digits=10, decimal_places=2)

    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.DRAFT)

    draw_date = models.DateTimeField('Data do Sorteio', null=True, blank=True)
    winner_number = models.PositiveIntegerField('Número Vencedor', null=True, blank=True)
    winner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='raffles_won',
        verbose_name='Vencedor'
    )

    # Referral settings
    inviter_bonus = models.PositiveIntegerField('Bônus do Indicante', default=2, help_text='Números grátis para quem indica')
    invitee_bonus = models.PositiveIntegerField('Bônus do Indicado', default=1, help_text='Números grátis para quem foi indicado')

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Rifa'
        verbose_name_plural = 'Rifas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

    @property
    def numbers_sold(self):
        """Count sold numbers"""
        return self.numbers.filter(status=RaffleNumber.Status.SOLD).count()

    @property
    def numbers_reserved(self):
        """Count reserved numbers"""
        return self.numbers.filter(status=RaffleNumber.Status.RESERVED).count()

    @property
    def numbers_available(self):
        """Count available numbers"""
        return self.total_numbers - self.numbers_sold - self.numbers_reserved

    def initialize_numbers(self):
        """Create all numbers for this raffle"""
        if self.numbers.exists():
            return

        numbers = [
            RaffleNumber(raffle=self, number=i)
            for i in range(1, self.total_numbers + 1)
        ]
        RaffleNumber.objects.bulk_create(numbers)


class RaffleNumber(models.Model):
    """Individual raffle number"""

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Disponível'
        RESERVED = 'reserved', 'Reservado'
        SOLD = 'vendido', 'Vendido'

    class Source(models.TextChoices):
        PURCHASE = 'purchase', 'Compra'
        REFERRAL_INVITER = 'referral_inviter', 'Bônus Indicante'
        REFERRAL_INVITEE = 'referral_invitee', 'Bônus Indicado'

    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='numbers')
    number = models.PositiveIntegerField('Número')
    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='raffle_numbers'
    )
    order = models.ForeignKey(
        'RaffleOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allocated_numbers'
    )
    source = models.CharField(
        'Origem',
        max_length=30,
        choices=Source.choices,
        default=Source.PURCHASE
    )

    reserved_at = models.DateTimeField('Reservado em', null=True, blank=True)
    sold_at = models.DateTimeField('Vendido em', null=True, blank=True)

    class Meta:
        verbose_name = 'Número da Rifa'
        verbose_name_plural = 'Números da Rifa'
        unique_together = ['raffle', 'number']
        ordering = ['raffle', 'number']

    def __str__(self):
        return f"Rifa {self.raffle.name} - Número {self.number:04d}"


class RaffleOrder(models.Model):
    """Raffle order/purchase"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        PAID = 'paid', 'Pago'
        CANCELLED = 'cancelled', 'Cancelado'
        EXPIRED = 'expired', 'Expirado'

    class PaymentMethod(models.TextChoices):
        MERCADOPAGO = 'mercadopago', 'MercadoPago'
        PIX = 'pix', 'PIX'
        CREDIT_CARD = 'credit_card', 'Cartão de Crédito'

    raffle = models.ForeignKey(Raffle, on_delete=models.PROTECT, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='raffle_orders')

    quantity = models.PositiveIntegerField('Quantidade de Números')
    amount = models.DecimalField('Valor Total', max_digits=10, decimal_places=2)

    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_method = models.CharField(
        'Método de Pagamento',
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MERCADOPAGO
    )

    payment_id = models.CharField('ID do Pagamento', max_length=200, blank=True)
    payment_data = models.JSONField('Dados do Pagamento', default=dict, blank=True)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    paid_at = models.DateTimeField('Pago em', null=True, blank=True)
    expires_at = models.DateTimeField('Expira em', null=True, blank=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.id} - {self.user.name} - {self.get_status_display()}"

    @transaction.atomic
    def allocate_numbers(self):
        """Allocate random available numbers to this order"""
        if self.allocated_numbers.exists():
            return list(self.allocated_numbers.values_list('number', flat=True))

        # Get available numbers
        available = list(
            RaffleNumber.objects.filter(
                raffle=self.raffle,
                status=RaffleNumber.Status.AVAILABLE
            ).values_list('id', flat=True)
        )

        if len(available) < self.quantity:
            raise ValidationError('Não há números suficientes disponíveis')

        # Select random numbers
        selected_ids = random.sample(available, self.quantity)

        # Reserve numbers
        RaffleNumber.objects.filter(id__in=selected_ids).update(
            status=RaffleNumber.Status.RESERVED,
            user=self.user,
            order=self,
            reserved_at=models.functions.Now()
        )

        return list(
            RaffleNumber.objects.filter(id__in=selected_ids).values_list('number', flat=True)
        )

    @transaction.atomic
    def mark_as_paid(self):
        """Mark order as paid and allocate numbers permanently"""
        from django.utils import timezone

        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save()

        # Mark all reserved numbers as sold
        self.allocated_numbers.update(
            status=RaffleNumber.Status.SOLD,
            sold_at=timezone.now()
        )

        return list(self.allocated_numbers.values_list('number', flat=True))


class Referral(models.Model):
    """Referral system"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        REDEEMED = 'redeemed', 'Resgatado'
        EXPIRED = 'expired', 'Expirado'

    code = models.CharField('Código', max_length=10, unique=True, default=generate_referral_code)
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='referrals')

    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='referrals_sent',
        verbose_name='Indicante'
    )
    invitee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals_received',
        verbose_name='Indicado'
    )

    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.PENDING)

    inviter_numbers_allocated = models.BooleanField('Números do indicante alocados', default=False)
    invitee_numbers_allocated = models.BooleanField('Números do indicado alocados', default=False)

    clicks = models.PositiveIntegerField('Cliques', default=0)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    redeemed_at = models.DateTimeField('Resgatado em', null=True, blank=True)

    class Meta:
        verbose_name = 'Indicação'
        verbose_name_plural = 'Indicações'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.inviter.name}"

    def register_click(self):
        """Register a click on this referral link"""
        self.clicks += 1
        self.save(update_fields=['clicks'])

    @transaction.atomic
    def redeem(self, invitee):
        """Redeem referral and allocate bonus numbers"""
        from django.utils import timezone

        if self.status != self.Status.PENDING:
            raise ValidationError('Este código de indicação já foi utilizado')

        if invitee == self.inviter:
            raise ValidationError('Você não pode usar seu próprio código de indicação')

        self.invitee = invitee
        self.status = self.Status.REDEEMED
        self.redeemed_at = timezone.now()
        self.save()

        return self

    @transaction.atomic
    def allocate_bonus_numbers(self):
        """Allocate bonus numbers for both inviter and invitee"""
        if not self.invitee:
            return

        # Allocate for inviter
        if not self.inviter_numbers_allocated:
            self._allocate_numbers(
                user=self.inviter,
                quantity=self.raffle.inviter_bonus,
                source=RaffleNumber.Source.REFERRAL_INVITER
            )
            self.inviter_numbers_allocated = True

        # Allocate for invitee
        if not self.invitee_numbers_allocated:
            self._allocate_numbers(
                user=self.invitee,
                quantity=self.raffle.invitee_bonus,
                source=RaffleNumber.Source.REFERRAL_INVITEE
            )
            self.invitee_numbers_allocated = True

        self.save()

    def _allocate_numbers(self, user, quantity, source):
        """Helper to allocate numbers"""
        from django.utils import timezone

        available = list(
            RaffleNumber.objects.filter(
                raffle=self.raffle,
                status=RaffleNumber.Status.AVAILABLE
            ).values_list('id', flat=True)[:quantity]
        )

        if len(available) < quantity:
            return

        RaffleNumber.objects.filter(id__in=available).update(
            status=RaffleNumber.Status.SOLD,
            user=user,
            source=source,
            sold_at=timezone.now()
        )
