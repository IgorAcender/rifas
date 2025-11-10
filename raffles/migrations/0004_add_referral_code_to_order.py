# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raffles', '0003_add_referral_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='raffleorder',
            name='referral_code',
            field=models.CharField(blank=True, max_length=10, verbose_name='Codigo de Indicacao'),
        ),
    ]
