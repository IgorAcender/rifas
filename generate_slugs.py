"""
Script para gerar slugs para rifas existentes
Execute: python manage.py shell < generate_slugs.py
"""

from raffles.models import Raffle
from django.utils.text import slugify

print("Gerando slugs para rifas existentes...")

raffles = Raffle.objects.filter(slug='')
count = 0

for raffle in raffles:
    base_slug = slugify(raffle.name)
    slug = base_slug
    counter = 1
    
    while Raffle.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    raffle.slug = slug
    raffle.save()
    count += 1
    print(f"✓ Slug gerado para '{raffle.name}': {slug}")

print(f"\n✅ {count} rifas atualizadas com sucesso!")
