#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from raffles.models import RaffleNumber, RaffleOrder
from accounts.models import User

# Get user - try to find any user
users = User.objects.filter(is_staff=False)[:5]
if not users:
    print('No users found!')
    exit()

print(f'Found {users.count()} users, showing first one:')
user = users.first()
print(f'User: {user.name}')
print(f'Phone: {user.whatsapp}')
print()

# Check numbers by status
numbers = RaffleNumber.objects.filter(user=user)
print(f'Total numbers: {numbers.count()}')
print()

for status_choice in RaffleNumber.Status:
    count = numbers.filter(status=status_choice.value).count()
    print(f'  {status_choice.label}: {count}')

print()
print('Last 5 numbers:')
for num in numbers.order_by('-id')[:5]:
    print(f'  Num: {num.number:04d} | Status: {num.status} | Raffle: {num.raffle.name} | Order: {num.order_id}')

print()
print('Last 3 orders:')
orders = RaffleOrder.objects.filter(user=user).order_by('-created_at')[:3]
for order in orders:
    allocated_count = order.allocated_numbers.count()
    print(f'  Order #{order.id} | Status: {order.status} | Qty: {order.quantity} | Allocated: {allocated_count} | Created: {order.created_at}')
