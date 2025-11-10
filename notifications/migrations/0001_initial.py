# Generated migration for WhatsAppMessageTemplate model

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppMessageTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='payment_confirmation', max_length=100, unique=True)),
                ('template', models.TextField(help_text='Use placeholders: {name}, {raffle_name}, {prize_name}, {draw_date}, {numbers}, {amount}, {order_id}')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'WhatsApp Message Template',
                'verbose_name_plural': 'WhatsApp Message Templates',
            },
        ),
    ]
