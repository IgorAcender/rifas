#!/bin/bash

# Script para corrigir o login do admin
# Adiciona email ao usuário admin existente

echo "╔════════════════════════════════════════════════════════╗"
echo "║     🔧 CORREÇÃO DE LOGIN DO ADMIN                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Este script vai atualizar o email do seu usuário admin"
echo "para que você possa fazer login com EMAIL + SENHA"
echo ""

# Solicitar email
read -p "Digite o email do admin: " ADMIN_EMAIL

# Solicitar se quer atualizar senha também
read -p "Deseja atualizar a senha? (s/n): " UPDATE_PASSWORD

if [ "$UPDATE_PASSWORD" = "s" ] || [ "$UPDATE_PASSWORD" = "S" ]; then
    read -sp "Digite a nova senha: " NEW_PASSWORD
    echo ""
    python manage.py update_admin_email --email="$ADMIN_EMAIL" --password="$NEW_PASSWORD"
else
    python manage.py update_admin_email --email="$ADMIN_EMAIL"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║     ✅ ADMIN ATUALIZADO COM SUCESSO!                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Agora você pode fazer login em /admin-login/ com:"
echo "  📧 Email: $ADMIN_EMAIL"
if [ "$UPDATE_PASSWORD" = "s" ] || [ "$UPDATE_PASSWORD" = "S" ]; then
    echo "  🔑 Senha: [senha atualizada]"
else
    echo "  🔑 Senha: [senha anterior mantida]"
fi
echo ""
