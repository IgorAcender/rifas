from django.core.management.base import BaseCommand
from django.utils import timezone
from raffles.models import RaffleNumber
from datetime import timedelta


class Command(BaseCommand):
    help = 'Libera números reservados que expiraram (executa a cada hora)'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Liberar números com reserva expirada
        expired = RaffleNumber.objects.filter(
            status=RaffleNumber.Status.RESERVED,
            reserved_expires_at__isnull=False,
            reserved_expires_at__lt=now
        )
        
        count = expired.count()
        
        if count > 0:
            expired.update(
                status=RaffleNumber.Status.AVAILABLE,
                user=None,
                order=None,
                reserved_at=None,
                reserved_expires_at=None
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ {count} número(s) reservado(s) liberado(s) com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('✓ Nenhum número reservado expirado encontrado.')
            )
