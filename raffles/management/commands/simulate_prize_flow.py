from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Simula fluxo: mark_as_paid + webhook merge para verificar preservation de won_prizes"

    def add_arguments(self, parser):
        parser.add_argument('order_id', type=int, help='ID do RaffleOrder a simular')

    def handle(self, *args, **options):
        order_id = options['order_id']
        from raffles.models import RaffleOrder
        from django.utils import timezone
        try:
            order = RaffleOrder.objects.get(id=order_id)
        except RaffleOrder.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Pedido {order_id} não encontrado'))
            return

        self.stdout.write(self.style.NOTICE(f'Pedido {order.id} - status atual: {order.status}'))
        self.stdout.write('payment_data atual:')
        self.stdout.write(str(order.payment_data))

        # Run mark_as_paid() if not already paid
        if order.status != RaffleOrder.Status.PAID:
            self.stdout.write('Chamando order.mark_as_paid()...')
            order.mark_as_paid()
            self.stdout.write(self.style.SUCCESS('mark_as_paid() executado'))
        else:
            self.stdout.write('Pedido já está como PAID, pulando mark_as_paid()')

        # Show payment_data after mark_as_paid
        order.refresh_from_db()
        self.stdout.write('payment_data após mark_as_paid:')
        self.stdout.write(str(order.payment_data))

        # Simular payload do MercadoPago (mimic webhook) e aplicar merge usando mesma lógica
        self.stdout.write('Simulando payload do MercadoPago e merge...')
        payment_data = {
            'id': 'SIMULATED-123',
            'status': 'approved',
            'external_reference': str(order.id),
        }

        # Mesclar campos importantes (won_prizes etc.) - mesmo comportamento do webhook
        existing = order.payment_data or {}
        for key in ('won_prizes', 'milestone_achieved', 'milestone_prize'):
            if key in existing and key not in payment_data:
                payment_data[key] = existing[key]

        order.payment_data = payment_data
        order.save(update_fields=['payment_data'])

        self.stdout.write(self.style.SUCCESS('Merge simulado aplicado. payment_data final:'))
        order.refresh_from_db()
        self.stdout.write(str(order.payment_data))

        # Final checks
        if order.payment_data and 'won_prizes' in order.payment_data:
            self.stdout.write(self.style.SUCCESS('✅ won_prizes preservado na payment_data'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ won_prizes NÃO encontrado em payment_data'))
