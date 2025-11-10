#!/usr/bin/env python
"""
Script para testar envio de WhatsApp e debug
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from raffles.models import RaffleOrder
from notifications.whatsapp import send_payment_confirmation
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_last_paid_order():
    """Test WhatsApp sending for last paid order"""
    try:
        # Get last paid order
        order = RaffleOrder.objects.filter(status='paid').order_by('-paid_at').first()

        if not order:
            print("❌ Nenhum pedido pago encontrado")
            return

        print(f"\n📦 Testando pedido #{order.id}")
        print(f"👤 Cliente: {order.user.name}")
        print(f"📱 WhatsApp: {order.user.whatsapp}")
        print(f"🎫 Rifa: {order.raffle.name}")
        print(f"🔢 Quantidade: {order.quantity} números")
        print(f"💰 Valor: R$ {order.amount}")

        numbers = list(order.allocated_numbers.values_list('number', flat=True))
        print(f"🎲 Números alocados: {numbers}")

        print("\n📤 Enviando mensagem de teste...")
        result = send_payment_confirmation(order)

        if result:
            print("✅ Mensagem enviada com sucesso!")
            print(f"📋 Resposta: {result}")
        else:
            print("❌ Falha ao enviar mensagem")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


def test_specific_order(order_id):
    """Test WhatsApp sending for specific order ID"""
    try:
        order = RaffleOrder.objects.get(id=order_id)

        print(f"\n📦 Testando pedido #{order.id}")
        print(f"👤 Cliente: {order.user.name}")
        print(f"📱 WhatsApp: {order.user.whatsapp}")
        print(f"📊 Status: {order.get_status_display()}")

        if order.status != 'paid':
            print(f"⚠️  AVISO: Pedido não está pago (status: {order.status})")

        numbers = list(order.allocated_numbers.values_list('number', flat=True))
        print(f"🎲 Números alocados: {numbers}")

        print("\n📤 Enviando mensagem de teste...")
        result = send_payment_confirmation(order)

        if result:
            print("✅ Mensagem enviada com sucesso!")
            print(f"📋 Resposta: {result}")
        else:
            print("❌ Falha ao enviar mensagem")

    except RaffleOrder.DoesNotExist:
        print(f"❌ Pedido #{order_id} não encontrado")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


def check_evolution_status():
    """Check Evolution API connection status"""
    from notifications.evolution import evolution_api

    print("\n🔍 Verificando status da Evolution API...")
    status = evolution_api.check_instance_status()

    if status:
        print(f"✅ API conectada: {status}")
    else:
        print("❌ API não conectada ou erro na verificação")


if __name__ == '__main__':
    print("=" * 60)
    print("🔧 DEBUG: Sistema de WhatsApp")
    print("=" * 60)

    if len(sys.argv) > 1:
        # Test specific order
        order_id = int(sys.argv[1])
        test_specific_order(order_id)
    else:
        # Check API status
        check_evolution_status()

        # Test last paid order
        test_last_paid_order()

    print("\n" + "=" * 60)
