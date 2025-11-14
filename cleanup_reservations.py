#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/Users/user/Desktop/Programação/rifas')
django.setup()

from raffles.models import RaffleNumber
from django.utils import timezone

now = timezone.now()

# Contar reservas expiradas
expired = RaffleNumber.objects.filter(
    status=RaffleNumber.Status.RESERVED,
    reserved_expires_at__isnull=False,
    reserved_expires_at__lt=now
)

print(f"Encontrados {expired.count()} números reservados expirados")

# Liberar
updated = expired.update(
    status=RaffleNumber.Status.AVAILABLE,
    user=None,
    order=None,
    reserved_at=None,
    reserved_expires_at=None
)

print(f"✅ {updated} número(s) liberado(s)!")
