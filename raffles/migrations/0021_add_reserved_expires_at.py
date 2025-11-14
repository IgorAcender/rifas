from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raffles', '0020_auto_migration'),  # Ajuste para a última migração
    ]

    operations = [
        migrations.AddField(
            model_name='rafflenumber',
            name='reserved_expires_at',
            field=models.DateTimeField('Reserva Expira em', null=True, blank=True, help_text='Data/hora quando a reserva vai expirar'),
        ),
    ]
