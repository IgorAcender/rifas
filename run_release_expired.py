#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/Users/user/Desktop/Programação/rifas')

django.setup()

from django.core.management import call_command

call_command('release_expired_reservations', verbosity=2)
