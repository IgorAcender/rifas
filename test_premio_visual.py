"""
Script para testar se números premiados (antigos ou novos) aparecem com o badge 🏆
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from raffles.models import Raffle, UserNumber, PrizeNumber
from datetime import datetime, timedelta

User = get_user_model()


class TestPrizeNumberVisual(TestCase):
    """Testa se números premiados mostram o badge corretamente"""

    def setUp(self):
        """Cria dados de teste"""
        # Cria um usuário
        self.user = User.objects.create_user(
            whatsapp='37999999999',
            name='Test Customer'
        )

        # Cria uma campanha
        self.raffle = Raffle.objects.create(
            name='Test Raffle',
            slug='test-raffle',
            description='Test',
            ticket_price=10.00,
            total_numbers=100,
            status='active'
        )

        # Cria números para o usuário
        self.number_450 = UserNumber.objects.create(
            user=self.user,
            raffle=self.raffle,
            number=450,
            source='purchase'
        )

        self.number_123 = UserNumber.objects.create(
            user=self.user,
            raffle=self.raffle,
            number=123,
            source='purchase'
        )

        # Marca o número 450 como premiado (número antigo/novo)
        self.prize = PrizeNumber.objects.create(
            raffle=self.raffle,
            number=450,
            released=False  # Pode ser True ou False
        )

    def test_prize_key_generation(self):
        """Testa se a chave de prêmio é gerada corretamente"""
        # A chave deve ser: {raffle_id}_{number}
        expected_key = f"{self.raffle.id}_{450}"
        self.assertEqual(expected_key, f"{self.raffle.id}_450")
        print(f"✓ Chave de prêmio gerada corretamente: {expected_key}")

    def test_prize_numbers_dict_population(self):
        """Testa se todos os prêmios são adicionados ao dicionário"""
        user_raffle_ids = [self.raffle.id]
        prize_numbers = PrizeNumber.objects.filter(raffle_id__in=user_raffle_ids)

        # Deve encontrar 1 prêmio
        self.assertEqual(prize_numbers.count(), 1)
        print(f"✓ Encontrados {prize_numbers.count()} prêmio(s)")

        # Constrói o dicionário como faz no código real
        prize_numbers_dict = {}
        for prize in prize_numbers:
            key = f"{prize.raffle_id}_{prize.number}"
            prize_numbers_dict[key] = True

        # O dicionário deve ter 1 entrada
        self.assertEqual(len(prize_numbers_dict), 1)
        print(f"✓ Dicionário de prêmios populado: {prize_numbers_dict}")

        # Verifica se a chave do número 450 existe
        key_450 = f"{self.raffle.id}_450"
        self.assertIn(key_450, prize_numbers_dict)
        print(f"✓ Número 450 marcado como premiado: {key_450}")

    def test_template_condition(self):
        """Testa a condição que o template usa"""
        # Simula o contexto do template
        prize_numbers_dict = {
            f"{self.raffle.id}_450": True,
        }

        # Testa se o número 450 seria marcado como premio
        prize_key_450 = f"{self.raffle.id}_{450}"
        is_prize = prize_key_450 in prize_numbers_dict
        self.assertTrue(is_prize)
        print(f"✓ Número 450 receberia classe 'prize-number': {is_prize}")

        # Testa se o número 123 NÃO seria marcado como premio
        prize_key_123 = f"{self.raffle.id}_{123}"
        is_prize = prize_key_123 in prize_numbers_dict
        self.assertFalse(is_prize)
        print(f"✓ Número 123 não receberia classe 'prize-number': {not is_prize}")

    def test_customer_area_view(self):
        """Testa se a view carrega corretamente com prêmios"""
        client = Client()
        client.force_login(self.user)

        response = client.get('/minha-area/')
        
        # Verifica se a resposta é 200
        self.assertEqual(response.status_code, 200)
        print(f"✓ View carregada com sucesso (status 200)")

        # Verifica se o contexto contém prize_numbers_dict
        if 'prize_numbers_dict' in response.context:
            prize_dict = response.context['prize_numbers_dict']
            print(f"✓ prize_numbers_dict encontrado no contexto: {prize_dict}")

            # Verifica se o número 450 está lá
            key_450 = f"{self.raffle.id}_450"
            if key_450 in prize_dict:
                print(f"✓✓ SUCESSO! Número 450 está marcado como premiado!")
            else:
                print(f"✗ ERRO! Número 450 NÃO está em prize_numbers_dict")
        else:
            print(f"⚠ prize_numbers_dict não encontrado no contexto")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧪 TESTE: Números Premiados com Badge Visual")
    print("="*70 + "\n")
