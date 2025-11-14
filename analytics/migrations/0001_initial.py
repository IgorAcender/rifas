from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('raffles', '0021_add_reserved_expires_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_type', models.CharField(
                    choices=[
                        ('home', 'Página Inicial'),
                        ('raffle_public', 'Raffle Pública'),
                        ('raffle_details', 'Detalhes da Raffle'),
                        ('customer_area', 'Área do Cliente'),
                        ('other', 'Outra'),
                    ],
                    default='other',
                    max_length=20,
                )),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('ip_address', models.CharField(max_length=50)),
                ('referer', models.CharField(blank=True, max_length=500)),
                ('viewed_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('raffle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='raffles.raffle')),
            ],
            options={
                'verbose_name': 'Visualização de Página',
                'verbose_name_plural': 'Visualizações de Página',
                'ordering': ['-viewed_at'],
                'indexes': [
                    models.Index(fields=['page_type', 'viewed_at'], name='page_type_viewed_at_idx'),
                    models.Index(fields=['raffle', 'viewed_at'], name='raffle_viewed_at_idx'),
                ],
            },
        ),
    ]
