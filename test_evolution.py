#!/usr/bin/env python
"""
Script para testar a integração com Evolution API
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from notifications.evolution import evolution_api, send_whatsapp_message


def test_connection():
    """Test Evolution API connection"""
    print("=" * 60)
    print("TESTE DE CONEXÃO - EVOLUTION API")
    print("=" * 60)
    print(f"\nURL: {settings.EVOLUTION_API_URL}")
    print(f"Instance: {settings.EVOLUTION_INSTANCE_NAME}")
    print(f"API Key: {'*' * 20}{settings.EVOLUTION_API_KEY[-4:] if settings.EVOLUTION_API_KEY else 'NOT SET'}")

    if not settings.EVOLUTION_API_URL:
        print("\n❌ EVOLUTION_API_URL não configurada!")
        print("Configure no arquivo .env")
        return False

    if not settings.EVOLUTION_API_KEY:
        print("\n❌ EVOLUTION_API_KEY não configurada!")
        print("Configure no arquivo .env")
        return False

    if not settings.EVOLUTION_INSTANCE_NAME:
        print("\n❌ EVOLUTION_INSTANCE_NAME não configurada!")
        print("Configure no arquivo .env")
        return False

    print("\n✅ Configurações OK!")

    # Test instance status
    print("\nTestando status da instância...")
    status = evolution_api.check_instance_status()

    if status:
        print(f"✅ Status: {status}")
        return True
    else:
        print("❌ Erro ao verificar status da instância")
        return False


def test_send_message():
    """Test sending a message"""
    print("\n" + "=" * 60)
    print("TESTE DE ENVIO DE MENSAGEM")
    print("=" * 60)

    # Get phone from admin settings
    test_phone = settings.ADMIN_WHATSAPP

    print(f"\nEnviando mensagem de teste para: {test_phone}")

    message = """
🤖 *Teste Evolution API*

Esta é uma mensagem de teste do sistema de rifas.

Se você recebeu esta mensagem, a integração está funcionando! ✅
    """.strip()

    result = send_whatsapp_message(test_phone, message)

    if result:
        print(f"✅ Mensagem enviada com sucesso!")
        print(f"Resposta: {result}")
        return True
    else:
        print("❌ Erro ao enviar mensagem")
        return False


def show_menu():
    """Show test menu"""
    print("\n" + "=" * 60)
    print("EVOLUTION API - MENU DE TESTES")
    print("=" * 60)
    print("\n1. Testar conexão")
    print("2. Enviar mensagem de teste")
    print("3. Testar conexão + enviar mensagem")
    print("4. Sair")

    choice = input("\nEscolha uma opção: ")
    return choice


def main():
    """Main function"""
    while True:
        choice = show_menu()

        if choice == '1':
            test_connection()
        elif choice == '2':
            test_send_message()
        elif choice == '3':
            if test_connection():
                print("\nProsseguindo para teste de envio...")
                test_send_message()
        elif choice == '4':
            print("\nSaindo...")
            break
        else:
            print("\n❌ Opção inválida!")

        input("\nPressione ENTER para continuar...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTeste cancelado pelo usuário.")
        sys.exit(0)
