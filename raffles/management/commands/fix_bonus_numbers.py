"""
Management command para corrigir números bônus antigos
"""
from django.core.management.base import BaseCommand
from raffles.models import RaffleNumber, RaffleOrder
from django.db.models import Count, Q

class Command(BaseCommand):
    help = 'Corrige números bônus antigos que foram marcados como purchase'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Iniciando correção de números bônus...'))
        
        fixed_count = 0
        
        # Buscar todos os pedidos pagos
        orders = RaffleOrder.objects.filter(status='paid').select_related('user', 'raffle')
        
        for order in orders:
            # Buscar números deste pedido
            numbers = order.allocated_numbers.filter(source='purchase').order_by('number')
            total = numbers.count()
            
            # Se tem mais números que a quantidade comprada, os extras são bônus
            if total > order.quantity:
                bonus_count = total - order.quantity
                
                self.stdout.write(f'\n📦 Pedido #{order.id} - {order.user.name}')
                self.stdout.write(f'   Quantidade comprada: {order.quantity}')
                self.stdout.write(f'   Total alocado: {total}')
                self.stdout.write(f'   Bônus detectado: {bonus_count}')
                
                # Os últimos números são bônus
                bonus_numbers = numbers[order.quantity:]
                
                for num in bonus_numbers:
                    self.stdout.write(f'   ✅ Marcando número {num.number} como REFERRAL_INVITEE')
                    num.source = RaffleNumber.Source.REFERRAL_INVITEE
                    num.save(update_fields=['source'])
                    fixed_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {fixed_count} números corrigidos!'))
