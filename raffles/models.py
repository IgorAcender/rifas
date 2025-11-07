import random
import string
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils.text import slugify
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
    slug = models.SlugField('Slug', max_length=250, unique=True, blank=True)
    description = models.TextField('Descricao', blank=True)
    prize_name = models.CharField('Nome do Premio', max_length=200)
    prize_description = models.TextField('Descricao do Premio', blank=True)
    prize_image_base64 = models.TextField('Imagem do Premio (Base64)', blank=True)

    total_numbers = models.PositiveIntegerField('Total de Numeros')
    price_per_number = models.DecimalField('Preco por Numero', max_digits=10, decimal_places=2)

    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.DRAFT)

    draw_date = models.DateTimeField('Data do Sorteio', null=True, blank=True)
    winner_number = models.PositiveIntegerField('Numero Vencedor', null=True, blank=True)
    winner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='raffles_won',
        verbose_name='Vencedor'
    )

    # Referral settings
    enable_referral = models.BooleanField('Ativar Indicações', default=True, help_text='Permitir que clientes indiquem amigos')
    referral_min_purchase = models.PositiveIntegerField('Mínimo para Indicar', default=1, help_text='Quantidade mínima de números para poder indicar (0 = sem mínimo)')
    inviter_bonus = models.PositiveIntegerField('Bonus do Indicante', default=2, help_text='Numeros gratis para quem indica')
    invitee_bonus = models.PositiveIntegerField('Bonus do Indicado', default=1, help_text='Numeros gratis para quem foi indicado')

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Rifa'
        verbose_name_plural = 'Rifas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        """Auto-generate slug from name"""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Raffle.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_public_url(self):
        """Get public URL for this raffle"""
        from django.urls import reverse
        return reverse('raffle_public', kwargs={'slug': self.slug})

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

    def release_expired_reservations(self):
        """Release numbers from expired pending orders"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Orders pending for more than 15 minutes are considered expired
        expiration_time = timezone.now() - timedelta(minutes=15)
        
        # Find expired pending orders
        expired_orders = self.orders.filter(
            status=RaffleOrder.Status.PENDING,
            created_at__lt=expiration_time
        )
        
        # Release their numbers
        for order in expired_orders:
            order.allocated_numbers.update(
                status=RaffleNumber.Status.AVAILABLE,
                user=None,
                order=None,
                reserved_at=None
            )
            order.status = RaffleOrder.Status.EXPIRED
            order.save(update_fields=['status'])


class RaffleNumber(models.Model):
    """Individual raffle number"""

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Disponivel'
        RESERVED = 'reserved', 'Reservado'
        SOLD = 'vendido', 'Vendido'

    class Source(models.TextChoices):
        PURCHASE = 'purchase', 'Compra'
        REFERRAL_INVITER = 'referral_inviter', 'Bonus Indicante'
        REFERRAL_INVITEE = 'referral_invitee', 'Bonus Indicado'

    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='numbers')
    number = models.PositiveIntegerField('Numero')
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
        verbose_name = 'Numero da Rifa'
        verbose_name_plural = 'Numeros da Rifa'
        unique_together = ['raffle', 'number']
        ordering = ['raffle', 'number']

    def __str__(self):
        return f"Rifa {self.raffle.name} - Numero {self.number:04d}"


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
        CREDIT_CARD = 'credit_card', 'Cartao de Credito'

    raffle = models.ForeignKey(Raffle, on_delete=models.PROTECT, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='raffle_orders')

    quantity = models.PositiveIntegerField('Quantidade de Numeros')
    amount = models.DecimalField('Valor Total', max_digits=10, decimal_places=2)

    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_method = models.CharField(
        'Metodo de Pagamento',
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
            raise ValidationError('Nao ha numeros suficientes disponiveis')

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

    code = models.CharField('Codigo', max_length=10, unique=True, default=generate_referral_code)
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

    inviter_numbers_allocated = models.BooleanField('Numeros do indicante alocados', default=False)
    invitee_numbers_allocated = models.BooleanField('Numeros do indicado alocados', default=False)

    clicks = models.PositiveIntegerField('Cliques', default=0)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    redeemed_at = models.DateTimeField('Resgatado em', null=True, blank=True)

    class Meta:
        verbose_name = 'Indicacao'
        verbose_name_plural = 'Indicacoes'
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
            raise ValidationError('Este codigo de indicacao ja foi utilizado')

        if invitee == self.inviter:
            raise ValidationError('Voce nao pode usar seu proprio codigo de indicacao')

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
