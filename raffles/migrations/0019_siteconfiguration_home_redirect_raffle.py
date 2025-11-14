# Generated migration to add home_redirect_raffle field to SiteConfiguration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('raffles', '0018_raffle_milestone_prize_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='home_redirect_raffle',
            field=models.ForeignKey(blank=True, help_text='Campanha para a qual a página inicial redirecionará. Se vazio, mostra lista de campanhas.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='raffles.raffle', verbose_name='Campanha Padrão da Home'),
        ),
    ]
