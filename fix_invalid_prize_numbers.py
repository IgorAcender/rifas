#!/usr/bin/env python
"""
Script para remover números premiados que referenciam números já vendidos
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from raffles.models import PrizeNumber, RaffleNumber

def fix_invalid_prize_numbers():
    """Remove prize numbers que referenciam números já vendidos"""
    print("🔍 Buscando números premiados inválidos...")
    
    removed_count = 0
    
    for prize in PrizeNumber.objects.all():
        # Verificar se o RaffleNumber correspondente foi vendido
        raffle_number = prize.raffle.numbers.filter(number=prize.number).first()
        
        if raffle_number and raffle_number.status == RaffleNumber.Status.SOLD:
            # Se foi vendido e o prêmio NÃO foi ganho, é inválido
            if not prize.is_won:
                print(f"❌ Removendo número premiado inválido: {prize.number} da campanha '{prize.raffle.name}'")
                print(f"   Motivo: Número já foi vendido mas prêmio não foi marcado como ganho")
                print(f"   Status atual: is_released={prize.is_released}, is_won={prize.is_won}")
                prize.delete()
                removed_count += 1
    
    if removed_count > 0:
        print(f"\n✅ {removed_count} número(s) premiado(s) inválido(s) removido(s)")
    else:
        print("\n✅ Nenhum número premiado inválido encontrado")

if __name__ == '__main__':
    fix_invalid_prize_numbers()
