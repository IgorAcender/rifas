from django import template

register = template.Library()

@register.filter
def make_prize_key(raffle_id, number):
    """Cria a chave de prêmio no formato: raffle_id_number"""
    return f"{raffle_id}_{number}"
