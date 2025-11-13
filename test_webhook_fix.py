#!/usr/bin/env python3
"""
Script para testar o webhook do MercadoPago
Simula uma requisição do MercadoPago com form-urlencoded
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Adicionar 'testserver' aos ALLOWED_HOSTS para testes
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

django.setup()

from django.test.client import Client
from raffles.models import RaffleOrder
import json

def test_webhook_form_encoded():
    """Testa webhook com form-urlencoded (formato real do MercadoPago)"""
    print("\n🧪 Testando Webhook com form-urlencoded...\n")
    
    client = Client()
    webhook_url = '/api/payments/mercadopago/webhook/'
    
    # Simular dados que MercadoPago envia
    webhook_data = {
        'action': 'payment.updated',
        'data[id]': '999999999',  # ID de teste
    }
    
    # Teste 1: Form-urlencoded
    print("📨 Test 1: Enviando como form-urlencoded...")
    response = client.post(
        webhook_url,
        data=webhook_data,
        content_type='application/x-www-form-urlencoded'
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Webhook aceitou form-urlencoded!")
    else:
        print(f"   Response: {response.content.decode()[:100]}\n")
    
    # Teste 2: JSON
    print("📨 Test 2: Enviando como JSON...")
    json_data = {
        'action': 'payment.updated',
        'data': {'id': '999999999'}
    }
    response = client.post(
        webhook_url,
        data=json.dumps(json_data),
        content_type='application/json'
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Webhook aceitou JSON!")
    else:
        print(f"   Response: {response.content.decode()[:100]}\n")
    
    print("✅ Testes completos!")


def test_with_real_payment_id():
    """Testa com um payment_id real no banco de dados"""
    print("\n🔍 Testando com pedido real no banco...\n")
    
    # Buscar pedido recente
    try:
        order = RaffleOrder.objects.latest('id')
        print(f"📦 Pedido encontrado: #{order.id}")
        print(f"👤 Usuário: {order.user.name}")
        print(f"💳 Status: {order.status}")
        print(f"📱 WhatsApp: {order.user.whatsapp}\n")
        
    except RaffleOrder.DoesNotExist:
        print("ℹ️  Nenhum pedido encontrado no banco de dados (esperado em novo setup)")
        return
    
    # Se tiver payment_id, usar para teste
    if order.payment_id:
        print(f"💳 Payment ID: {order.payment_id}")
        
        client = Client()
        webhook_url = '/api/payments/mercadopago/webhook/'
        
        webhook_data = {
            'action': 'payment.updated',
            'data[id]': str(order.payment_id),
        }
        
        print("\n📨 Enviando webhook de teste...")
        response = client.post(
            webhook_url,
            data=webhook_data,
            content_type='application/x-www-form-urlencoded'
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")


def test_rest_framework_parsers():
    """Verifica se os parsers estão configurados"""
    print("\n⚙️  Verificando Configuração do REST Framework...\n")
    
    from django.conf import settings
    
    parsers = settings.REST_FRAMEWORK.get('DEFAULT_PARSER_CLASSES', [])
    
    print("✅ Parsers configurados:")
    for parser in parsers:
        print(f"  - {parser}")
    
    expected = [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ]
    
    all_present = all(p in str(parsers) for p in expected)
    
    if all_present:
        print("\n✅ Todos os parsers necessários estão configurados!")
        return True
    else:
        print("\n❌ Faltam parsers! Verifique settings.py")
        print(f"   Esperado: {expected}")
        print(f"   Encontrado: {parsers}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DE WEBHOOK DO MERCADOPAGO")
    print("=" * 60)
    
    # Executar testes
    parsers_ok = test_rest_framework_parsers()
    
    if parsers_ok:
        test_webhook_form_encoded()
        test_with_real_payment_id()
    
    print("\n" + "=" * 60)
    print("✅ Testes Concluídos!")
    print("=" * 60)
