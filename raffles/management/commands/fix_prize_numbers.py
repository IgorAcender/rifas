from django.core.management.base import BaseCommand
from raffles.models import Raffle, PrizeNumber, RaffleNumber


class Command(BaseCommand):
    help = 'Corrige números premiados que foram liberados incorretamente (sem ter sido comprados)'

    def handle(self, *args, **options):
        self.stdout.write('Verificando números premiados liberados...\n')

        # Buscar todos os números premiados liberados
        released_prizes = PrizeNumber.objects.filter(is_released=True).select_related('raffle')

        fixed_count = 0
        correct_count = 0

        for prize in released_prizes:
            # Verificar se o número foi realmente comprado
            was_purchased = RaffleNumber.objects.filter(
                raffle=prize.raffle,
                number=prize.number,
                status=RaffleNumber.Status.SOLD
            ).exists()

            if not was_purchased:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Número premiado {prize.number} da campanha "{prize.raffle.name}" '
                        f'foi liberado mas não foi comprado'
                    )
                )
                prize.is_released = False
                prize.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Corrigido: Número {prize.number} marcado como não liberado'
                    )
                )
            else:
                correct_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Número premiado {prize.number} da campanha "{prize.raffle.name}" '
                        f'está correto (comprado e liberado)'
                    )
                )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ Correção concluída!'))
        self.stdout.write(f'   - Números corrigidos: {fixed_count}')
        self.stdout.write(f'   - Números corretos: {correct_count}')
        self.stdout.write(f'   - Total verificados: {fixed_count + correct_count}')
        self.stdout.write('='*60)
