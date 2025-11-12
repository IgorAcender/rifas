#!/usr/bin/env python3
"""
Script para corrigir números bônus antigos que foram marcados como 'purchase'.
Este script identifica números bônus baseado nos dados de payment_data dos pedidos.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from raffles.models import RaffleOrder, RaffleNumber
from django.db.models import Q

def fix_bonus_numbers():
    """
    Corrige números bônus antigos identificando-os através de:
    1. Pedidos com payment_data contendo 'purchase_bonus'
    2. Números de indicação (referral)
    """
    
    print("🔍 Buscando pedidos com bônus...")
    
    # Buscar pedidos pagos que têm bônus registrado
    orders_with_bonus = RaffleOrder.objects.filter(
        status='paid',
        payment_data__isnull=False
    )
    
    fixed_count = 0
    
    for order in orders_with_bonus:
        # Verificar se tem bônus de compra no payment_data
        bonus_count = 0
        if isinstance(order.payment_data, dict):
            bonus_count = order.payment_data.get('purchase_bonus', 0)
        
        if bonus_count > 0:
            print(f"\n📦 Pedido #{order.id} - User: {order.user.name}")
            print(f"   Quantidade comprada: {order.quantity}")
            print(f"   Bônus registrado: {bonus_count}")
            
            # Buscar todos os números deste pedido
            all_numbers = order.allocated_numbers.filter(source='purchase').order_by('number')
            total_allocated = all_numbers.count()
            
            print(f"   Total de números alocados: {total_allocated}")
            
            if total_allocated == order.quantity + bonus_count:
                # Os últimos N números são bônus
                paid_numbers = all_numbers[:order.quantity]
                bonus_numbers = all_numbers[order.quantity:]
                
                print(f"   ✅ Marcando {bonus_numbers.count()} números como PURCHASE_BONUS:")
                
                for num in bonus_numbers:
                    print(f"      - Número {num.number}: purchase → purchase_bonus")
                    num.source = RaffleNumber.Source.PURCHASE_BONUS
                    num.save(update_fields=['source'])
                    fixed_count += 1
            else:
                print(f"   ⚠️  Inconsistência detectada, pulando...")
    
    # Verificar números de indicação que podem estar marcados errado
    print("\n🔍 Buscando números de indicação...")
    
    # Números que têm referral_code mas estão marcados como purchase
    referral_orders = RaffleOrder.objects.filter(
        status='paid',
        referral_code__isnull=False
    ).exclude(referral_code='')
    
    for order in referral_orders:
        # Esses números podem ser bônus de indicação
        # Vamos verificar se o usuário tem números extras além do que comprou
        all_user_numbers = RaffleNumber.objects.filter(
            raffle=order.raffle,
            order__user=order.user,
            order__status='paid'
        )
        
        total_purchased = RaffleOrder.objects.filter(
            raffle=order.raffle,
            user=order.user,
            status='paid'
        ).values_list('quantity', flat=True)
        
        total_should_have = sum(total_purchased)
        total_has = all_user_numbers.count()
        
        if total_has > total_should_have:
            print(f"\n👤 User: {order.user.name}")
            print(f"   Total comprado: {total_should_have}")
            print(f"   Total possui: {total_has}")
            print(f"   Diferença (bônus): {total_has - total_should_have}")
            print(f"   ℹ️  Esses números podem ser bônus de indicação")
    
    print(f"\n✅ Total de números corrigidos: {fixed_count}")
    print(f"✅ Concluído!")

if __name__ == '__main__':
    fix_bonus_numbers()
