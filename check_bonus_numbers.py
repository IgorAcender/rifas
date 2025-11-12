#!/usr/bin/env python3
"""
Script para verificar números específicos e seu source
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from raffles.models import RaffleNumber
from accounts.models import User

# Buscar a Suze
user = User.objects.filter(name__icontains='Suze').first()

if user:
    print(f"👤 User: {user.name} (ID: {user.id})")
    
    # Buscar todos os números
    all_numbers = RaffleNumber.objects.filter(
        order__user=user,
        order__status='paid'
    ).order_by('number')
    
    print(f"\n📊 Total de números: {all_numbers.count()}")
    
    # Agrupar por source
    from collections import defaultdict
    by_source = defaultdict(list)
    
    for num in all_numbers:
        by_source[num.source].append(num.number)
    
    print("\n📋 Números por source:")
    for source, numbers in by_source.items():
        print(f"\n  {source}: {len(numbers)} números")
        if source != 'purchase':
            print(f"  Números: {sorted(numbers)}")
    
    # Verificar os números específicos
    print("\n🔍 Verificando números específicos:")
    for num_value in [14306, 3]:
        num_obj = RaffleNumber.objects.filter(
            order__user=user,
            number=num_value
        ).first()
        if num_obj:
            print(f"  Número {num_value}: source='{num_obj.source}', order_id={num_obj.order_id}")
else:
    print("❌ Usuário Suze não encontrado")
