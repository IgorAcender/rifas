# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raffles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='raffle',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, unique=True, verbose_name='Slug'),
        ),
    ]
