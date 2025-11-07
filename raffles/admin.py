from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Raffle, RaffleNumber, RaffleOrder, Referral


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
            'fields': ('total_numbers', 'price_per_number', 'draw_date')
        }),
        ('Resultado', {
            'fields': ('winner_number', 'winner')
        }),
        ('Indicacoes', {
            'fields': ('inviter_bonus', 'invitee_bonus')
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
