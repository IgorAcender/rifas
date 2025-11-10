#!/usr/bin/env python
"""
Script para criar códigos de referência para usuários que compraram 10+ bilhetes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from raffles.models import Referral, RaffleOrder, Raffle
from django.db.models import Sum

def create_referral_codes():
    print("🔍 Procurando usuários que precisam de códigos de referência...")
    
    # Pegar todos os usuários
    users = User.objects.filter(is_staff=False)
    
    for user in users:
        print(f"\n👤 Usuário: {user.name} ({user.whatsapp})")
        
        # Pegar todas as rifas ativas
        raffles = Raffle.objects.filter(status=Raffle.Status.ACTIVE)
        
        for raffle in raffles:
            # Contar quantos tickets o usuário comprou nesta rifa
            total_tickets = RaffleOrder.objects.filter(
                user=user,
                raffle=raffle,
                status=RaffleOrder.Status.PAID
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            if total_tickets >= 10:
                # Verificar se já existe um código de referência
                existing_referral = Referral.objects.filter(
                    inviter=user,
                    raffle=raffle
                ).first()
                
                if existing_referral:
                    print(f"   ✅ Já existe código para {raffle.name}: {existing_referral.code}")
                else:
                    # Criar novo código de referência
                    referral = Referral.objects.create(
                        inviter=user,
                        raffle=raffle,
                        status=Referral.Status.ACTIVE
                    )
                    print(f"   🎉 Código criado para {raffle.name}: {referral.code} ({total_tickets} tickets)")
            else:
                print(f"   ⏭️  Não qualifica para {raffle.name} (apenas {total_tickets} tickets, precisa 10+)")

if __name__ == '__main__':
    create_referral_codes()
    print("\n✅ Processo concluído!")
