#!/usr/bin/env python3
"""
Script para verificar se as migrations de bônus foram aplicadas
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from raffles.models import Raffle
from django.db import connection

print("🔍 Verificando sistema de bônus...\n")

# 1. Verificar campos no banco
print("1️⃣ Verificando campos no banco de dados:")
with connection.cursor() as cursor:
    cursor.execute("PRAGMA table_info(raffles_raffle)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_fields = [
        'enable_purchase_bonus',
        'purchase_bonus_every',
        'purchase_bonus_amount',
        'enable_milestone_bonus',
        'milestone_quantity',
        'milestone_prize_name',
        'milestone_prize_description'
    ]
    
    missing = []
    for field in required_fields:
        if field in columns:
            print(f"   ✅ {field}")
        else:
            print(f"   ❌ {field} - FALTANDO!")
            missing.append(field)

# 2. Verificar migrations
print("\n2️⃣ Verificando migrations aplicadas:")
from django.db.migrations.recorder import MigrationRecorder
recorder = MigrationRecorder(connection)
migrations = recorder.applied_migrations()
raffles_migrations = [m for m in migrations if m[0] == 'raffles']
print(f"   Total de migrations em 'raffles': {len(raffles_migrations)}")

has_bonus_migration = any('milestone' in str(m) or '0009' in str(m) for m in raffles_migrations)
if has_bonus_migration:
    print(f"   ✅ Migration de bônus encontrada")
else:
    print(f"   ❌ Migration 0009 não encontrada!")

# 3. Testar criação de objeto
print("\n3️⃣ Testando acesso aos campos:")
try:
    raffle = Raffle.objects.first()
    if raffle:
        print(f"   ✅ enable_purchase_bonus: {raffle.enable_purchase_bonus}")
        print(f"   ✅ enable_milestone_bonus: {raffle.enable_milestone_bonus}")
    else:
        print("   ⚠️  Nenhuma campanha encontrada para testar")
except AttributeError as e:
    print(f"   ❌ ERRO: {e}")
    print("   Os campos de bônus NÃO estão disponíveis no modelo!")

print("\n" + "="*50)
if missing:
    print("❌ PROBLEMA: Campos faltando no banco!")
    print("\n💡 SOLUÇÃO:")
    print("   Execute: python3 manage.py migrate raffles")
else:
    print("✅ Sistema de bônus instalado corretamente!")
    print("\n📝 Próximo passo:")
    print("   Acesse /admin e edite uma campanha")
    print("   Você verá as seções 'Bonus de Compra' e 'Premio Milestone'")
