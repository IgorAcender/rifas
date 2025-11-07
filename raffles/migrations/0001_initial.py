# Generated migration for raffles app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import raffles.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Raffle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descricao')),
                ('prize_name', models.CharField(max_length=200, verbose_name='Nome do Premio')),
                ('prize_description', models.TextField(blank=True, verbose_name='Descricao do Premio')),
                ('prize_image_base64', models.TextField(blank=True, verbose_name='Imagem do Premio (Base64)')),
                ('total_numbers', models.PositiveIntegerField(verbose_name='Total de Numeros')),
                ('price_per_number', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Preco por Numero')),
                ('status', models.CharField(choices=[('draft', 'Rascunho'), ('active', 'Ativa'), ('finished', 'Finalizada'), ('cancelled', 'Cancelada')], default='draft', max_length=20, verbose_name='Status')),
                ('draw_date', models.DateTimeField(blank=True, null=True, verbose_name='Data do Sorteio')),
                ('winner_number', models.PositiveIntegerField(blank=True, null=True, verbose_name='Numero Vencedor')),
                ('inviter_bonus', models.PositiveIntegerField(default=2, help_text='Numeros gratis para quem indica', verbose_name='Bonus do Indicante')),
                ('invitee_bonus', models.PositiveIntegerField(default=1, help_text='Numeros gratis para quem foi indicado', verbose_name='Bonus do Indicado')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='raffles_won', to=settings.AUTH_USER_MODEL, verbose_name='Vencedor')),
            ],
            options={
                'verbose_name': 'Rifa',
                'verbose_name_plural': 'Rifas',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RaffleOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantidade de Numeros')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor Total')),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('paid', 'Pago'), ('cancelled', 'Cancelado'), ('expired', 'Expirado')], default='pending', max_length=20, verbose_name='Status')),
                ('payment_method', models.CharField(choices=[('mercadopago', 'MercadoPago'), ('pix', 'PIX'), ('credit_card', 'Cartao de Credito')], default='mercadopago', max_length=20, verbose_name='Metodo de Pagamento')),
                ('payment_id', models.CharField(blank=True, max_length=200, verbose_name='ID do Pagamento')),
                ('payment_data', models.JSONField(blank=True, default=dict, verbose_name='Dados do Pagamento')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('paid_at', models.DateTimeField(blank=True, null=True, verbose_name='Pago em')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Expira em')),
                ('raffle', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='raffles.raffle')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='raffle_orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RaffleNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(verbose_name='Numero')),
                ('status', models.CharField(choices=[('available', 'Disponivel'), ('reserved', 'Reservado'), ('vendido', 'Vendido')], default='available', max_length=20, verbose_name='Status')),
                ('source', models.CharField(choices=[('purchase', 'Compra'), ('referral_inviter', 'Bonus Indicante'), ('referral_invitee', 'Bonus Indicado')], default='purchase', max_length=30, verbose_name='Origem')),
                ('reserved_at', models.DateTimeField(blank=True, null=True, verbose_name='Reservado em')),
                ('sold_at', models.DateTimeField(blank=True, null=True, verbose_name='Vendido em')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='allocated_numbers', to='raffles.raffleorder')),
                ('raffle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='numbers', to='raffles.raffle')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='raffle_numbers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Numero da Rifa',
                'verbose_name_plural': 'Numeros da Rifa',
                'ordering': ['raffle', 'number'],
                'unique_together': {('raffle', 'number')},
            },
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=raffles.models.generate_referral_code, max_length=10, unique=True, verbose_name='Codigo')),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('redeemed', 'Resgatado'), ('expired', 'Expirado')], default='pending', max_length=20, verbose_name='Status')),
                ('inviter_numbers_allocated', models.BooleanField(default=False, verbose_name='Numeros do indicante alocados')),
                ('invitee_numbers_allocated', models.BooleanField(default=False, verbose_name='Numeros do indicado alocados')),
                ('clicks', models.PositiveIntegerField(default=0, verbose_name='Cliques')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('redeemed_at', models.DateTimeField(blank=True, null=True, verbose_name='Resgatado em')),
                ('invitee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals_received', to=settings.AUTH_USER_MODEL, verbose_name='Indicado')),
                ('inviter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals_sent', to=settings.AUTH_USER_MODEL, verbose_name='Indicante')),
                ('raffle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals', to='raffles.raffle')),
            ],
            options={
                'verbose_name': 'Indicacao',
                'verbose_name_plural': 'Indicacoes',
                'ordering': ['-created_at'],
            },
        ),
    ]
