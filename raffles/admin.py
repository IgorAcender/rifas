from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Raffle, RaffleNumber, RaffleOrder, Referral, PrizeNumber


@admin.register(Raffle)
class RaffleAdmin(ModelAdmin):
    list_display = ('name', 'status', 'total_numbers', 'numbers_sold', 'numbers_available', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'prize_name')
    readonly_fields = ('numbers_sold', 'numbers_reserved', 'numbers_available', 'created_at', 'updated_at')

    fieldsets = (
        ('Informacoes Basicas', {
            'fields': ('name', 'description', 'status')
        }),
        ('Premio', {
            'fields': ('prize_name', 'prize_description', 'prize_image_base64')
        }),
        ('Configuracoes', {
            'fields': ('total_numbers', 'price_per_number', 'fee_percentage', 'draw_date')
        }),
        ('Resultado', {
            'fields': ('winner_number', 'winner')
        }),
        ('Indicacoes', {
            'fields': (
                'enable_referral', 
                'referral_min_purchase', 
                'inviter_bonus', 
                'invitee_bonus', 
                'invitee_min_purchase',
                'enable_progressive_bonus',
                'progressive_bonus_every'
            ),
            'description': 'Configure o sistema de indicação de amigos. O bônus progressivo permite que o indicador ganhe números extras baseado na quantidade que o indicado compra (ex: 1 número a cada 20 comprados).'
        }),
        ('Bonus de Compra', {
            'fields': (
                'enable_purchase_bonus',
                'purchase_bonus_every',
                'purchase_bonus_amount',
            ),
            'description': 'Configure o bônus progressivo de compra: cliente ganha números extras automaticamente ao comprar quantidade específica (ex: a cada 10 números, ganhe 1 grátis).'
        }),
        ('Premio Milestone', {
            'fields': (
                'enable_milestone_bonus',
                'milestone_quantity',
                'milestone_prize_name',
                'milestone_prize_description',
            ),
            'description': 'Configure um prêmio especial para clientes que comprarem uma quantidade mínima de números (ex: compre 50 números e ganhe um PDF exclusivo).'
        }),
        ('Estatisticas', {
            'fields': ('numbers_sold', 'numbers_reserved', 'numbers_available', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # Se e novo
            obj.initialize_numbers()


@admin.register(RaffleNumber)
class RaffleNumberAdmin(ModelAdmin):
    list_display = ('raffle', 'number', 'status', 'user', 'source', 'sold_at')
    list_filter = ('status', 'source', 'raffle')
    search_fields = ('number', 'user__whatsapp', 'user__name')
    readonly_fields = ('reserved_at', 'sold_at')


@admin.register(RaffleOrder)
class RaffleOrderAdmin(ModelAdmin):
    list_display = ('id', 'raffle', 'user', 'quantity', 'amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('id', 'user__whatsapp', 'user__name', 'raffle__name', 'payment_id')
    readonly_fields = ('created_at', 'paid_at')


@admin.register(Referral)
class ReferralAdmin(ModelAdmin):
    list_display = ('code', 'raffle', 'inviter', 'invitee', 'status', 'clicks', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('code', 'inviter__whatsapp', 'inviter__name', 'invitee__whatsapp', 'invitee__name')
    readonly_fields = ('code', 'clicks', 'created_at', 'redeemed_at')


@admin.register(PrizeNumber)
class PrizeNumberAdmin(ModelAdmin):
    list_display = ('raffle', 'number', 'prize_amount', 'release_percentage_min', 'release_percentage_max', 'is_released', 'is_won', 'winner')
    list_filter = ('is_released', 'is_won', 'raffle')
    search_fields = ('number', 'raffle__name', 'winner__name', 'winner__whatsapp')
    readonly_fields = ('is_released', 'is_won', 'winner', 'won_at', 'created_at', 'updated_at')
