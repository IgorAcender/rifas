# Generated migration for notifications app

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_add_delay_seconds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='whatsappmessagetemplate',
            name='template',
            field=models.TextField(help_text='Use placeholders: {name}, {raffle_name}, {prize_name}, {draw_date}, {numbers}, {amount}, {order_id}, {customer_area_url}'),
        ),
    ]
