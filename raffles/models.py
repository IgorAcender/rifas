import random
import string
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from accounts.models import User


def generate_referral_code():
    """Generate unique referral code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class SiteConfiguration(models.Model):
    """
    Singleton model to store site-wide configuration.
    Only one instance should exist.
    """

    # Logo settings (Base64 - same pattern as Raffle.prize_image_base64)
    logo_base64 = models.TextField(
        'Logo do Site (Base64)',
        blank=True,
        help_text='Logo em formato Base64. Cole o código data:image/... completo aqui.'
    )

    # Site metadata
    site_name = models.CharField(
        'Nome do Site',
        max_length=100,
        default='Sistema de Rifas',
        help_text='Nome exibido no site'
    )

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Configuração do Site'
        verbose_name_plural = 'Configurações do Site'

    def __str__(self):
        return f"Configurações do Site - {self.site_name}"

    def save(self, *args, **kwargs):
        """Override save to ensure only one instance exists"""
        # Ensure singleton
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValidationError('Já existe uma configuração de site. Edite a existente.')

        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        """Get or create the site configuration singleton"""
        config, created = cls.objects.get_or_create(pk=1)
        return config

    @classmethod
    def get_logo_base64(cls):
        """Get logo as base64 string, or return default SVG logo"""
        config = cls.get_config()

        if config.logo_base64:
            return config.logo_base64

        # Default logo (the existing one from templates)
        return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjEyMCIgdmlld0JveD0iMCAwIDEyMCAxMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iNjAiIGN5PSI2MCIgcj0iNjAiIGZpbGw9IiMzMzUyNjgiLz48cGF0aCBkPSJNMzUgNDVDMzUgNDMgNDAgNDAgNDUgNDBDNTAgNDAgNTUgNDMgNTUgNDVMNjAgODBINTVMNDUgNTBMMzUgNTBMMzUgNDVaIiBmaWxsPSIjRkJCRjI0Ii8+PHBhdGggZD0iTTc1IDQ1Qzc1IDQzIDgwIDQwIDg1IDQwQzkwIDQwIDk1IDQzIDk1IDQ1TDkwIDgwSDg1TDc1IDUwTDc1IDQ1WiIgZmlsbD0iI0ZCQkYyNCIvPjxwYXRoIGQ9Ik00MCA3MEM0MCA2OCA0NSA2NSA1MCA2NUM1NSA2NSA2MCA2OCA2MCA3MEw1NSA5NUg1MEw0MCA3NUw0MCA3MFoiIGZpbGw9IiNGQkJGMjQiLz48cGF0aCBkPSJNNDUgMzVMNzUgMzVMNjAgNjBMNDUgMzVaIiBmaWxsPSIjQ0NENkUwIi8+PHBhdGggZD0iTTUwIDY1TDcwIDY1TDYwIDg1TDUwIDY1WiIgZmlsbD0iI0NDRDZFMCI+PGFuaW1hdGVUcmFuc2Zvcm0gYXR0cmlidXRlTmFtZT0idHJhbnNmb3JtIiB0eXBlPSJzY2FsZSIgZnJvbT0iMSIgdG89IjEuMSIgZHVyPSIwLjVzIiByZXBlYXRDb3VudD0iaW5maW5pdGUiLz48L3BhdGg+PC9zdmc+'


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
    
    # Fee/Tax settings
    fee_percentage = models.DecimalField('Taxa (%)', max_digits=5, decimal_places=2, default=0, help_text='Porcentagem de taxa sobre o valor (ex: 5.00 para 5%)')

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
    invitee_min_purchase = models.PositiveIntegerField('Compra Mínima do Indicado', default=5, help_text='Quantidade mínima que o indicado precisa comprar para ganhar o bônus')
    
    # Progressive bonus
    enable_progressive_bonus = models.BooleanField('Ativar Bônus Progressivo', default=False, help_text='Indicador ganha números extras baseado na quantidade que o indicado compra')
    progressive_bonus_every = models.PositiveIntegerField('Bônus a Cada X Números', default=20, help_text='A cada X números que o indicado compra, o indicador ganha 1 número extra (ex: 20 = ganha 1 número a cada 20 comprados)')

    # Purchase bonus - "A cada X números, ganhe Y números grátis"
    enable_purchase_bonus = models.BooleanField('Ativar Bônus por Quantidade', default=False, help_text='Cliente ganha números extras ao comprar quantidade específica')
    purchase_bonus_every = models.PositiveIntegerField('A Cada X Números', default=10, help_text='A cada X números comprados, ganha Y números grátis')
    purchase_bonus_amount = models.PositiveIntegerField('Ganhe Y Números', default=1, help_text='Quantidade de números grátis ganhos')
    
    # Milestone bonus - "Compre X números, ganhe um prêmio especial"
    enable_milestone_bonus = models.BooleanField('Ativar Prêmio por Meta', default=False, help_text='Cliente ganha prêmio especial ao atingir quantidade mínima')
    milestone_quantity = models.PositiveIntegerField('Quantidade Mínima', default=50, help_text='Quantidade mínima de números para ganhar o prêmio')
    milestone_prize_name = models.CharField('Nome do Prêmio', max_length=200, blank=True, help_text='Ex: PDF Exclusivo, Curso Online, etc')
    milestone_prize_description = models.TextField('Descrição do Prêmio', blank=True, help_text='Detalhes sobre o prêmio especial')

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

    def expand_numbers(self, new_total):
        """Expand raffle by adding more numbers"""
        if new_total <= self.total_numbers:
            raise ValidationError(f'Novo total ({new_total}) deve ser maior que o atual ({self.total_numbers})')

        current_count = self.numbers.count()

        # Create new numbers from current_count + 1 to new_total
        new_numbers = [
            RaffleNumber(raffle=self, number=i)
            for i in range(current_count + 1, new_total + 1)
        ]
        RaffleNumber.objects.bulk_create(new_numbers)

        # Update total_numbers
        self.total_numbers = new_total
        self.save(update_fields=['total_numbers'])

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

    def check_and_release_prize_numbers(self):
        """Verifica e libera números premiados baseado na porcentagem de vendas"""
        if self.total_numbers == 0:
            return

        # Calcular porcentagem atual de vendas
        current_percentage = (self.numbers_sold / self.total_numbers) * 100

        # Verificar cada número premiado não liberado
        for prize_number in self.prize_numbers.filter(is_released=False):
            if prize_number.release_percentage_min <= current_percentage <= prize_number.release_percentage_max:
                prize_number.is_released = True
                prize_number.save(update_fields=['is_released', 'updated_at'])
                print(f"🎁 Número premiado {prize_number.number} liberado! (Vendas em {current_percentage:.1f}%)")


class RaffleNumber(models.Model):
    """Individual raffle number"""

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Disponivel'
        RESERVED = 'reserved', 'Reservado'
        SOLD = 'vendido', 'Vendido'

    class Source(models.TextChoices):
        PURCHASE = 'purchase', 'Compra'
        PURCHASE_BONUS = 'purchase_bonus', 'Bônus de Compra'
        MILESTONE_BONUS = 'milestone_bonus', 'Bônus Milestone'
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

    referral_code = models.CharField('Codigo de Indicacao', max_length=10, blank=True)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    paid_at = models.DateTimeField('Pago em', null=True, blank=True)
    expires_at = models.DateTimeField('Expira em', null=True, blank=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.id} - {self.user.name} - {self.get_status_display()}"

    def calculate_purchase_bonus(self):
        """Calculate bonus numbers based on purchase quantity"""
        bonus_numbers = 0
        
        # Bônus progressivo: "A cada X números, ganhe Y números grátis"
        if self.raffle.enable_purchase_bonus and self.raffle.purchase_bonus_every > 0:
            bonus_numbers = (self.quantity // self.raffle.purchase_bonus_every) * self.raffle.purchase_bonus_amount
        
        return bonus_numbers
    
    def qualifies_for_milestone(self):
        """Check if order qualifies for milestone bonus"""
        if not self.raffle.enable_milestone_bonus:
            return False
        
        return self.quantity >= self.raffle.milestone_quantity

    @transaction.atomic
    def allocate_numbers(self):
        """Allocate random available numbers to this order"""
        if self.allocated_numbers.exists():
            return list(self.allocated_numbers.values_list('number', flat=True))

        # Verificar e liberar números premiados baseado na porcentagem de vendas
        self.raffle.check_and_release_prize_numbers()

        # Calcular bônus de compra
        bonus_count = self.calculate_purchase_bonus()
        total_to_allocate = self.quantity + bonus_count
        
        if bonus_count > 0:
            print(f"🎁 Bônus de compra: {bonus_count} números extras! Total: {total_to_allocate}")

        # Get available numbers (excluindo números premiados que ainda não foram liberados)
        available = list(
            RaffleNumber.objects.filter(
                raffle=self.raffle,
                status=RaffleNumber.Status.AVAILABLE
            ).values_list('id', 'number')
        )

        # Filtrar números disponíveis (excluindo premiados não liberados)
        unreleased_prize_numbers = set(
            self.raffle.prize_numbers.filter(is_released=False).values_list('number', flat=True)
        )

        available_filtered = [(id, num) for id, num in available if num not in unreleased_prize_numbers]

        if len(available_filtered) < total_to_allocate:
            raise ValidationError('Nao ha numeros suficientes disponiveis')

        # Select random numbers (paid + bonus)
        selected = random.sample(available_filtered, total_to_allocate)
        selected_ids = [id for id, num in selected]

        # Separar números pagos e bônus
        paid_ids = selected_ids[:self.quantity]  # Primeiros são pagos
        bonus_ids = selected_ids[self.quantity:]  # Restantes são bônus

        # Reserve paid numbers
        RaffleNumber.objects.filter(id__in=paid_ids).update(
            status=RaffleNumber.Status.RESERVED,
            user=self.user,
            order=self,
            source=RaffleNumber.Source.PURCHASE,
            reserved_at=models.functions.Now()
        )
        
        # Reserve bonus numbers with correct source
        if bonus_ids:
            RaffleNumber.objects.filter(id__in=bonus_ids).update(
                status=RaffleNumber.Status.RESERVED,
                user=self.user,
                order=self,
                source=RaffleNumber.Source.PURCHASE_BONUS,
                reserved_at=models.functions.Now()
            )
        
        # Save bonus info in payment_data
        if bonus_count > 0:
            if not self.payment_data:
                self.payment_data = {}
            self.payment_data['purchase_bonus'] = bonus_count
            self.save(update_fields=['payment_data'])

        return list(
            RaffleNumber.objects.filter(id__in=selected_ids).values_list('number', flat=True)
        )

    @transaction.atomic
    def mark_as_paid(self):
        """Mark order as paid and allocate numbers permanently"""
        from django.utils import timezone

        print(f"🔄 DEBUG: Marking order {self.id} as paid. Referral code: {self.referral_code}")

        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save()

        # Mark all reserved numbers as sold
        self.allocated_numbers.update(
            status=RaffleNumber.Status.SOLD,
            sold_at=timezone.now()
        )
        print(f"✅ DEBUG: Marked {self.allocated_numbers.count()} numbers as sold")

        # Verificar se algum número comprado é um número premiado
        allocated_numbers = list(self.allocated_numbers.values_list('number', flat=True))
        won_prizes = []

        for number in allocated_numbers:
            try:
                prize = PrizeNumber.objects.get(
                    raffle=self.raffle,
                    number=number,
                    is_released=True,
                    is_won=False
                )
                # Marcar como ganho
                prize.is_won = True
                prize.winner = self.user
                prize.won_at = timezone.now()
                prize.save()
                won_prizes.append(prize)
                print(f"🏆 PRÊMIO GANHO! Usuário {self.user.name} ganhou R$ {prize.prize_amount} com o número {number}!")
            except PrizeNumber.DoesNotExist:
                pass

        # Armazenar prêmios ganhos no pedido para exibir depois
        if won_prizes:
            if not self.payment_data:
                self.payment_data = {}
            self.payment_data['won_prizes'] = [
                {
                    'number': p.number,
                    'prize_amount': float(p.prize_amount),
                    'prize_amount_formatted': f'R$ {p.prize_amount:.2f}'
                }
                for p in won_prizes
            ]
            self.save(update_fields=['payment_data'])
        
        # Verificar se qualifica para o prêmio milestone
        if self.qualifies_for_milestone():
            if not self.payment_data:
                self.payment_data = {}
            self.payment_data['milestone_achieved'] = True
            self.payment_data['milestone_prize'] = {
                'name': self.raffle.milestone_prize_name,
                'description': self.raffle.milestone_prize_description,
                'quantity_required': self.raffle.milestone_quantity
            }
            self.save(update_fields=['payment_data'])
            print(f"🎯 MILESTONE! Usuário {self.user.name} ganhou: {self.raffle.milestone_prize_name}")

        # Allocate bonus numbers if referral was used
        if self.referral_code:
            print(f"🎁 DEBUG: Processing referral code: {self.referral_code}")
            try:
                referral = Referral.objects.get(
                    code=self.referral_code,
                    raffle=self.raffle
                )
                print(f"📋 DEBUG: Referral found - status={referral.status}, inviter={referral.inviter.name}, invitee={referral.invitee.name if referral.invitee else 'None'}")
                
                if referral.status == Referral.Status.REDEEMED:
                    print(f"🎯 DEBUG: Calling allocate_bonus_numbers() with quantity={self.quantity}")
                    referral.allocate_bonus_numbers(invitee_purchase_quantity=self.quantity)
                    print(f"✅ DEBUG: Allocated bonus numbers for referral {self.referral_code}")
                else:
                    print(f"⚠️  DEBUG: Referral status is {referral.status}, not REDEEMED")
                    
            except Referral.DoesNotExist:
                print(f"❌ DEBUG: Referral {self.referral_code} not found in database")

        # Create referral code for this user if eligible
        if (self.raffle.enable_referral and
            self.quantity >= self.raffle.referral_min_purchase):
            # Check if user already has a referral code for this raffle
            existing_referral = Referral.objects.filter(
                inviter=self.user,
                raffle=self.raffle
            ).first()

            if not existing_referral:
                new_referral = Referral.objects.create(
                    inviter=self.user,
                    raffle=self.raffle
                )
                print(f"🎁 DEBUG: Created referral code {new_referral.code} for user {self.user.name}")

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
    def allocate_bonus_numbers(self, invitee_purchase_quantity=0):
        """Allocate bonus numbers for both inviter and invitee"""
        print(f"🎁 DEBUG: allocate_bonus_numbers called for referral {self.code}")
        print(f"   Inviter: {self.inviter.name}, Invitee: {self.invitee.name if self.invitee else 'None'}")
        print(f"   Status: {self.status}")
        print(f"   Inviter allocated: {self.inviter_numbers_allocated}, Invitee allocated: {self.invitee_numbers_allocated}")
        print(f"   Invitee purchase quantity: {invitee_purchase_quantity}")
        
        if not self.invitee:
            print("⚠️  DEBUG: No invitee found, cannot allocate bonus numbers")
            return

        # Calculate inviter bonus (base + progressive)
        inviter_total_bonus = self.raffle.inviter_bonus
        
        # Add progressive bonus if enabled
        if self.raffle.enable_progressive_bonus and invitee_purchase_quantity > 0:
            progressive_bonus = invitee_purchase_quantity // self.raffle.progressive_bonus_every
            if progressive_bonus > 0:
                inviter_total_bonus += progressive_bonus
                print(f"📈 DEBUG: Progressive bonus activated!")
                print(f"   Invitee bought: {invitee_purchase_quantity} numbers")
                print(f"   Progressive every: {self.raffle.progressive_bonus_every} numbers")
                print(f"   Progressive bonus: {progressive_bonus} extra numbers")
                print(f"   Total inviter bonus: {self.raffle.inviter_bonus} (base) + {progressive_bonus} (progressive) = {inviter_total_bonus}")

        # Allocate for inviter
        if not self.inviter_numbers_allocated:
            print(f"🎯 DEBUG: Allocating {inviter_total_bonus} numbers for inviter {self.inviter.name}")
            self._allocate_numbers(
                user=self.inviter,
                quantity=inviter_total_bonus,
                source=RaffleNumber.Source.REFERRAL_INVITER
            )
            self.inviter_numbers_allocated = True
            print(f"✅ DEBUG: Inviter numbers allocated")
            
            # Send WhatsApp notification to inviter
            self._send_inviter_notification(inviter_total_bonus, invitee_purchase_quantity)
        else:
            print(f"ℹ️  DEBUG: Inviter already has bonus numbers allocated")

        # Allocate for invitee
        if not self.invitee_numbers_allocated:
            print(f"🎯 DEBUG: Allocating {self.raffle.invitee_bonus} numbers for invitee {self.invitee.name}")
            self._allocate_numbers(
                user=self.invitee,
                quantity=self.raffle.invitee_bonus,
                source=RaffleNumber.Source.REFERRAL_INVITEE
            )
            self.invitee_numbers_allocated = True
            print(f"✅ DEBUG: Invitee numbers allocated")
        else:
            print(f"ℹ️  DEBUG: Invitee already has bonus numbers allocated")

        self.save()
        print(f"✅ DEBUG: Bonus allocation complete for referral {self.code}")

    def _allocate_numbers(self, user, quantity, source):
        """Helper to allocate numbers"""
        from django.utils import timezone

        print(f"🔢 DEBUG: _allocate_numbers - user={user.name}, quantity={quantity}, source={source}")

        # Get available numbers randomly to make it fair
        available = list(
            RaffleNumber.objects.filter(
                raffle=self.raffle,
                status=RaffleNumber.Status.AVAILABLE
            ).order_by('?')  # Randomize order
            .values_list('id', flat=True)[:quantity]
        )

        print(f"📊 DEBUG: Found {len(available)} available numbers (requested {quantity})")

        if len(available) < quantity:
            print(f"⚠️  DEBUG: Not enough available numbers: found {len(available)}, need {quantity}")
            return

        RaffleNumber.objects.filter(id__in=available).update(
            status=RaffleNumber.Status.SOLD,
            user=user,
            source=source,
            sold_at=timezone.now()
        )
        
        print(f"✅ DEBUG: Successfully allocated {len(available)} numbers to {user.name}")

    def _send_inviter_notification(self, total_bonus, invitee_purchase_quantity):
        """Send WhatsApp notification to inviter about successful referral"""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.inviter.whatsapp or not self.invitee:
            return
        
        # Get the allocated bonus numbers
        bonus_numbers = RaffleNumber.objects.filter(
            raffle=self.raffle,
            user=self.inviter,
            source=RaffleNumber.Source.REFERRAL_INVITER
        ).order_by('number').values_list('number', flat=True)
        
        numbers_str = ', '.join([f"{n:04d}" for n in bonus_numbers])
        
        # Build bonus breakdown message
        bonus_breakdown = f"{self.raffle.inviter_bonus} números de bônus base"
        if self.raffle.enable_progressive_bonus and invitee_purchase_quantity > 0:
            progressive_bonus = invitee_purchase_quantity // self.raffle.progressive_bonus_every
            if progressive_bonus > 0:
                bonus_breakdown += f" + {progressive_bonus} números de bônus progressivo ({invitee_purchase_quantity} números comprados ÷ {self.raffle.progressive_bonus_every})"
        
        # Get custom template
        from notifications.models import WhatsAppMessageTemplate
        template_text = WhatsAppMessageTemplate.get_referral_bonus_template()
        
        # Format message with template
        try:
            message = template_text.format(
                inviter_name=self.inviter.name,
                invitee_name=self.invitee.name,
                raffle_name=self.raffle.name,
                invitee_quantity=invitee_purchase_quantity,
                total_bonus=total_bonus,
                bonus_breakdown=bonus_breakdown,
                bonus_numbers=numbers_str
            )
        except Exception as e:
            logger.error(f"Error formatting referral bonus template: {e}")
            # Fallback to hardcoded message
            message = f"""
🎉 *Parabéns! Indicação Confirmada!* 🎉

Olá *{self.inviter.name}*!

Ótima notícia! *{self.invitee.name}* acabou de concluir a compra usando seu link de indicação!

━━━━━━━━━━━━━━━━━━━
🎫 *Campanha:* {self.raffle.name}
👤 *Quem comprou:* {self.invitee.name}
💰 *Quantidade:* {invitee_purchase_quantity} números

🎁 *Você ganhou {total_bonus} números grátis!*
({bonus_breakdown})

🔢 *Seus números de bônus:*
{numbers_str}
━━━━━━━━━━━━━━━━━━━

✨ Continue indicando amigos e ganhe mais números!
Cada indicação bem-sucedida te dá mais chances de ganhar! 🍀
        """.strip()
        
        # Send via WhatsApp
        from notifications.whatsapp import send_whatsapp_message
        
        logger.info(f"📤 Sending referral bonus notification to inviter {self.inviter.whatsapp}")
        try:
            result = send_whatsapp_message(self.inviter.whatsapp, message)
            if result:
                logger.info(f"✅ Referral notification sent successfully to {self.inviter.name}")
            else:
                logger.error(f"❌ Failed to send referral notification to {self.inviter.name}")
        except Exception as e:
            logger.error(f"❌ Error sending referral notification: {e}", exc_info=True)


class PrizeNumber(models.Model):
    """Número premiado dentro de uma campanha"""

    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='prize_numbers')
    number = models.PositiveIntegerField('Número Premiado')
    prize_amount = models.DecimalField('Valor do Prêmio (R$)', max_digits=10, decimal_places=2)

    # Faixa de porcentagem para liberar esse número
    release_percentage_min = models.DecimalField(
        'Porcentagem Mínima (%)',
        max_digits=5,
        decimal_places=2,
        help_text='Ex: 18.00 para 18%'
    )
    release_percentage_max = models.DecimalField(
        'Porcentagem Máxima (%)',
        max_digits=5,
        decimal_places=2,
        help_text='Ex: 22.00 para 22%'
    )

    # Controle de status
    is_released = models.BooleanField('Foi Liberado', default=False)
    is_won = models.BooleanField('Foi Ganho', default=False)
    winner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prize_numbers_won',
        verbose_name='Ganhador'
    )
    won_at = models.DateTimeField('Ganho em', null=True, blank=True)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Número Premiado'
        verbose_name_plural = 'Números Premiados'
        unique_together = ['raffle', 'number']
        ordering = ['release_percentage_min', 'number']

    def __str__(self):
        return f"Número {self.number} - R$ {self.prize_amount} ({self.release_percentage_min}%-{self.release_percentage_max}%)"

    def check_and_release(self):
        """Verifica se o número deve ser liberado baseado na porcentagem de vendas"""
        if self.is_released:
            return False

        # Calcular porcentagem de vendas atual
        current_percentage = (self.raffle.numbers_sold / self.raffle.total_numbers) * 100

        # Verificar se está na faixa de liberação
        if self.release_percentage_min <= current_percentage <= self.release_percentage_max:
            self.is_released = True
            self.save(update_fields=['is_released', 'updated_at'])
            return True

        return False
