#!/usr/bin/env python
"""
Script para corrigir o login do admin
Adiciona email ao usuário admin existente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User


def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║     🔧 CORREÇÃO DE LOGIN DO ADMIN                      ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("Este script vai atualizar o email do seu usuário admin")
    print("para que você possa fazer login com EMAIL + SENHA")
    print()

    # Buscar admin existente
    admin = User.objects.filter(is_staff=True).first()
    
    if not admin:
        print("❌ Nenhum usuário admin encontrado!")
        print("   Execute: python manage.py create_admin")
        sys.exit(1)

    print(f"👤 Admin encontrado: {admin.name}")
    print(f"   WhatsApp: {admin.whatsapp}")
    if admin.email:
        print(f"   Email atual: {admin.email}")
    else:
        print("   Email atual: (não configurado)")
    print()

    # Solicitar email
    email = input("📧 Digite o email do admin: ").strip()
    
    if not email:
        print("❌ Email é obrigatório!")
        sys.exit(1)

    # Solicitar se quer atualizar senha
    update_password = input("🔑 Deseja atualizar a senha? (s/n): ").strip().lower()
    
    new_password = None
    if update_password in ['s', 'sim', 'y', 'yes']:
        import getpass
        new_password = getpass.getpass("Digite a nova senha: ")
        
        if not new_password:
            print("❌ Senha não pode ser vazia!")
            sys.exit(1)

    # Atualizar admin
    admin.email = email
    
    if new_password:
        admin.set_password(new_password)
    
    admin.save()

    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║     ✅ ADMIN ATUALIZADO COM SUCESSO!                   ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("Agora você pode fazer login em /admin-login/ com:")
    print(f"  📧 Email: {email}")
    
    if new_password:
        print(f"  🔑 Senha: {new_password}")
    else:
        print("  🔑 Senha: [senha anterior mantida]")
    
    print()
    print("🌐 Acesse: http://localhost:8000/admin-login/")
    print()


if __name__ == "__main__":
    main()
