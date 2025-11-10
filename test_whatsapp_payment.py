#!/usr/bin/env python
"""
Script para testar envio de WhatsApp após pagamento
Execute: python test_whatsapp_payment.py <order_id>
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from raffles.models import RaffleOrder
from notifications.whatsapp import send_payment_confirmation


def test_payment_notification(order_id):
    """Test sending payment notification for a specific order"""
    try:
        order = RaffleOrder.objects.get(id=order_id)
    except RaffleOrder.DoesNotExist:
        print(f"❌ Pedido {order_id} não encontrado")
        return

    print(f"\n📦 Testando envio de WhatsApp para pedido #{order.id}")
    print(f"👤 Cliente: {order.user.name}")
    print(f"📱 WhatsApp: {order.user.whatsapp}")
    print(f"🎫 Rifa: {order.raffle.name}")
    print(f"💰 Valor: R$ {order.amount}")
    print(f"📊 Status: {order.status}")

    if not order.user.whatsapp:
        print("\n❌ Erro: Cliente não tem WhatsApp cadastrado!")
        return

    # Get numbers
    numbers = sorted(order.allocated_numbers.values_list('number', flat=True))
    print(f"🔢 Números: {', '.join([f'{n:04d}' for n in numbers])}")

    print("\n📤 Enviando mensagem...")
    try:
        result = send_payment_confirmation(order)
        if result:
            print("✅ Mensagem enviada com sucesso!")
            print(f"📋 Resultado: {result}")
        else:
            print("❌ Falha ao enviar mensagem (resultado None)")
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_whatsapp_payment.py <order_id>")
        print("\nPedidos recentes:")
        orders = RaffleOrder.objects.order_by('-created_at')[:5]
        for order in orders:
            print(f"  - Pedido #{order.id} - {order.user.name} - {order.status}")
        sys.exit(1)

    order_id = sys.argv[1]
    test_payment_notification(order_id)
