"""
Management command para verificar e liberar números premiados
"""
from django.core.management.base import BaseCommand
from raffles.models import Raffle, PrizeNumber

class Command(BaseCommand):
    help = 'Verifica e libera números premiados baseado na porcentagem de vendas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Verificando números premiados...'))
        
        raffles = Raffle.objects.all()
        
        for raffle in raffles:
            self.stdout.write(f'\n📊 Campanha: {raffle.name}')
            self.stdout.write(f'   Total: {raffle.total_numbers} números')
            self.stdout.write(f'   Vendidos: {raffle.numbers_sold} números')
            
            if raffle.total_numbers > 0:
                percentage = (raffle.numbers_sold / raffle.total_numbers) * 100
                self.stdout.write(f'   Porcentagem: {percentage:.1f}%')
            else:
                percentage = 0
                
            # Buscar números premiados
            prize_numbers = raffle.prize_numbers.all()
            
            if not prize_numbers.exists():
                self.stdout.write(self.style.WARNING('   ⚠️  Nenhum número premiado configurado'))
                continue
                
            for prize in prize_numbers:
                status = '🔓 LIBERADO' if prize.is_released else '🔒 BLOQUEADO'
                self.stdout.write(f'   {status} Número {prize.number}: R$ {prize.prize_amount} (libera em {prize.release_percentage_min}%)')
                
                # Forçar verificação
                if not prize.is_released and percentage >= prize.release_percentage_min:
                    prize.is_released = True
                    prize.save()
                    self.stdout.write(self.style.SUCCESS(f'      ✅ LIBERADO AGORA!'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Verificação concluída!'))
