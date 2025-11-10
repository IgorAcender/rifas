from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Raffle, RaffleOrder, Referral, RaffleNumber, PrizeNumber
from .serializers import RaffleSerializer, RaffleOrderSerializer, ReferralSerializer
import re


class RaffleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Raffles - read only"""
    serializer_class = RaffleSerializer
    queryset = Raffle.objects.filter(status=Raffle.Status.ACTIVE)

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        """Create an order for this raffle"""
        raffle = self.get_object()

        data = {
            'raffle': raffle.id,
            'quantity': request.data.get('quantity', 1),
            'payment_method': request.data.get('payment_method', 'mercadopago')
        }

        # Pass referral code to serializer context
        context = {
            'request': request,
            'referral_code': request.data.get('referral_code')
        }

        serializer = RaffleOrderSerializer(data=data, context=context)
        if serializer.is_valid():
            order = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='my-referral')
    def my_referral(self, request, pk=None):
        """Get user's referral code for this raffle"""
        raffle = self.get_object()

        # Find user's referral for this raffle
        referral = Referral.objects.filter(
            inviter=request.user,
            raffle=raffle
        ).first()

        if not referral:
            # Check if user is eligible (has purchased enough)
            user_orders = RaffleOrder.objects.filter(
                user=request.user,
                raffle=raffle,
                status=RaffleOrder.Status.PAID
            )
            total_quantity = sum(order.quantity for order in user_orders)

            return Response({
                'has_referral': False,
                'eligible': total_quantity >= raffle.referral_min_purchase,
                'total_purchased': total_quantity,
                'min_required': raffle.referral_min_purchase,
                'message': f'Compre pelo menos {raffle.referral_min_purchase} números para ganhar seu link de indicação'
            })

        # Build full URL
        referral_url = request.build_absolute_uri(raffle.get_public_url())
        if '?' in referral_url:
            referral_url += f'&ref={referral.code}'
        else:
            referral_url += f'?ref={referral.code}'

        # Count successful referrals
        successful_referrals = Referral.objects.filter(
            inviter=request.user,
            raffle=raffle,
            status=Referral.Status.REDEEMED
        ).count()

        return Response({
            'has_referral': True,
            'code': referral.code,
            'link': referral_url,
            'clicks': referral.clicks,
            'successful_referrals': successful_referrals,
            'inviter_bonus': raffle.inviter_bonus,
            'invitee_bonus': raffle.invitee_bonus,
            'enable_progressive_bonus': raffle.enable_progressive_bonus,
            'progressive_bonus_every': raffle.progressive_bonus_every,
            'created_at': referral.created_at
        })


class RaffleOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user's orders"""
    serializer_class = RaffleOrderSerializer

    def get_queryset(self):
        return RaffleOrder.objects.filter(user=self.request.user).select_related('raffle')


class ReferralViewSet(viewsets.ModelViewSet):
    """ViewSet for Referrals"""
    serializer_class = ReferralSerializer
    lookup_field = 'code'
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        if self.action in ['retrieve', 'register_click', 'redeem']:
            return Referral.objects.all()
        return Referral.objects.filter(inviter=self.request.user).select_related('raffle')

    def get_permissions(self):
        if self.action in ['register_click', 'redeem']:
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def register_click(self, request, code=None):
        """Register a click on referral link"""
        referral = self.get_object()
        referral.register_click()
        return Response({
            'message': 'Click registrado',
            'raffle': RaffleSerializer(referral.raffle).data
        })

    @action(detail=True, methods=['post'])
    def redeem(self, request, code=None):
        """Redeem referral code"""
        referral = self.get_object()

        try:
            referral.redeem(request.user)
            return Response({
                'message': 'Código de indicação resgatado com sucesso!',
                'raffle': RaffleSerializer(referral.raffle).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# Frontend Views
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import base64


@login_required
def dashboard(request):
    """Dashboard principal - Admin vê estatísticas completas de todas as campanhas"""
    if request.user.is_staff:
        # Admin Dashboard - Estatísticas de todas as campanhas
        from django.db.models import Sum, Count, Q

        raffles = Raffle.objects.all().order_by('-created_at')

        # Calcular estatísticas para cada campanha
        campaigns_stats = []
        for raffle in raffles:
            # Contar números vendidos e reservados
            numbers_sold = raffle.numbers.filter(status=RaffleNumber.Status.SOLD).count()
            numbers_reserved = raffle.numbers.filter(status=RaffleNumber.Status.RESERVED).count()
            numbers_available = raffle.total_numbers - numbers_sold - numbers_reserved

            # Calcular valor arrecadado (apenas pagos)
            paid_orders = RaffleOrder.objects.filter(
                raffle=raffle,
                status=RaffleOrder.Status.PAID
            )
            total_revenue = paid_orders.aggregate(total=Sum('amount'))['total'] or 0

            # Contar compradores únicos (apenas pagos)
            unique_buyers = paid_orders.values('user').distinct().count()

            # Calcular taxa total arrecadada
            fee_amount = total_revenue * (raffle.fee_percentage / 100)
            net_revenue = total_revenue - fee_amount

            campaigns_stats.append({
                'raffle': raffle,
                'numbers_sold': numbers_sold,
                'numbers_reserved': numbers_reserved,
                'numbers_available': numbers_available,
                'total_revenue': total_revenue,
                'fee_amount': fee_amount,
                'net_revenue': net_revenue,
                'unique_buyers': unique_buyers,
                'percentage_sold': round((numbers_sold / raffle.total_numbers) * 100, 1) if raffle.total_numbers > 0 else 0,
            })

        # Estatísticas gerais
        total_campaigns = raffles.count()
        active_campaigns = raffles.filter(status=Raffle.Status.ACTIVE).count()
        total_buyers = RaffleOrder.objects.filter(status=RaffleOrder.Status.PAID).values('user').distinct().count()
        total_revenue_all = RaffleOrder.objects.filter(status=RaffleOrder.Status.PAID).aggregate(total=Sum('amount'))['total'] or 0

        context = {
            'campaigns_stats': campaigns_stats,
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'total_buyers': total_buyers,
            'total_revenue_all': total_revenue_all,
        }
        return render(request, 'raffles/admin_dashboard.html', context)
    else:
        # User Dashboard - Estatísticas do usuário
        user_raffles = Raffle.objects.filter(winner=request.user).count()
        user_orders = RaffleOrder.objects.filter(user=request.user, status=RaffleOrder.Status.PAID).count()

        context = {
            'user_raffles': user_raffles,
            'user_orders': user_orders,
        }
        return render(request, 'raffles/dashboard.html', context)


@login_required
def campaign_details(request, pk):
    """Detalhes completos de uma campanha - Admin only"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    raffle = get_object_or_404(Raffle, pk=pk)

    from django.db.models import Sum, Count
    from collections import defaultdict

    # Obter filtro da query string
    filter_by = request.GET.get('filter', 'total_amount')  # Padrão: maiores compradores

    # Estatísticas da campanha
    numbers_sold = raffle.numbers.filter(status=RaffleNumber.Status.SOLD).count()
    numbers_reserved = raffle.numbers.filter(status=RaffleNumber.Status.RESERVED).count()
    numbers_available = raffle.total_numbers - numbers_sold - numbers_reserved

    # Pedidos pagos
    paid_orders = RaffleOrder.objects.filter(
        raffle=raffle,
        status=RaffleOrder.Status.PAID
    ).select_related('user').order_by('-paid_at')

    total_revenue = paid_orders.aggregate(total=Sum('amount'))['total'] or 0
    fee_amount = total_revenue * (raffle.fee_percentage / 100)
    net_revenue = total_revenue - fee_amount

    # Agrupar por comprador
    buyers_data = defaultdict(lambda: {
        'user': None,
        'total_amount': 0,
        'total_quantity': 0,
        'orders_count': 0,
        'purchased_numbers': [],
        'bonus_numbers': [],
        'referral_bonus_count': 0,
        'successful_referrals': 0,
    })

    for order in paid_orders:
        buyer_key = order.user.id
        buyers_data[buyer_key]['user'] = order.user
        buyers_data[buyer_key]['total_amount'] += order.amount
        buyers_data[buyer_key]['total_quantity'] += order.quantity
        buyers_data[buyer_key]['orders_count'] += 1

    # Adicionar números de cada comprador e estatísticas de indicações
    for buyer_id, data in buyers_data.items():
        # Números comprados
        purchased = RaffleNumber.objects.filter(
            raffle=raffle,
            user=data['user'],
            source=RaffleNumber.Source.PURCHASE,
            status=RaffleNumber.Status.SOLD
        ).values_list('number', flat=True)
        data['purchased_numbers'] = sorted(list(purchased))

        # Números ganhos por indicação
        bonus = RaffleNumber.objects.filter(
            raffle=raffle,
            user=data['user'],
            source__in=[RaffleNumber.Source.REFERRAL_INVITER, RaffleNumber.Source.REFERRAL_INVITEE],
            status=RaffleNumber.Status.SOLD
        ).values_list('number', flat=True)
        data['bonus_numbers'] = sorted(list(bonus))
        data['referral_bonus_count'] = len(data['bonus_numbers'])

        # Contar quantas pessoas esse usuário indicou com sucesso (nesta campanha)
        successful_referrals = Referral.objects.filter(
            raffle=raffle,
            inviter=data['user'],
            status=Referral.Status.REDEEMED
        ).count()
        data['successful_referrals'] = successful_referrals

    # Converter para lista
    buyers_list = list(buyers_data.values())

    # Aplicar ordenação baseada no filtro
    if filter_by == 'total_amount':
        buyers_list = sorted(buyers_list, key=lambda x: x['total_amount'], reverse=True)
    elif filter_by == 'total_quantity':
        buyers_list = sorted(buyers_list, key=lambda x: x['total_quantity'], reverse=True)
    elif filter_by == 'referral_bonus':
        buyers_list = sorted(buyers_list, key=lambda x: x['referral_bonus_count'], reverse=True)
    elif filter_by == 'successful_referrals':
        buyers_list = sorted(buyers_list, key=lambda x: x['successful_referrals'], reverse=True)
    elif filter_by == 'name':
        buyers_list = sorted(buyers_list, key=lambda x: x['user'].name.lower())

    # Estatísticas de indicações
    referrals = Referral.objects.filter(raffle=raffle, status=Referral.Status.REDEEMED)
    total_referrals = referrals.count()

    # Top 5 indicadores
    top_inviters = []
    inviter_stats = {}
    for referral in referrals:
        inviter_id = referral.inviter.id
        if inviter_id not in inviter_stats:
            inviter_stats[inviter_id] = {
                'user': referral.inviter,
                'referral_count': 0,
                'bonus_numbers': 0
            }
        inviter_stats[inviter_id]['referral_count'] += 1

    # Adicionar contagem de números bônus
    for inviter_id, stats in inviter_stats.items():
        bonus_count = RaffleNumber.objects.filter(
            raffle=raffle,
            user=stats['user'],
            source=RaffleNumber.Source.REFERRAL_INVITER,
            status=RaffleNumber.Status.SOLD
        ).count()
        stats['bonus_numbers'] = bonus_count

    top_inviters = sorted(inviter_stats.values(), key=lambda x: x['referral_count'], reverse=True)[:5]

    context = {
        'raffle': raffle,
        'numbers_sold': numbers_sold,
        'numbers_reserved': numbers_reserved,
        'numbers_available': numbers_available,
        'total_revenue': total_revenue,
        'fee_amount': fee_amount,
        'net_revenue': net_revenue,
        'percentage_sold': round((numbers_sold / raffle.total_numbers) * 100, 1) if raffle.total_numbers > 0 else 0,
        'buyers_list': buyers_list,
        'total_buyers': len(buyers_list),
        'total_referrals': total_referrals,
        'top_inviters': top_inviters,
        'current_filter': filter_by,
    }
    return render(request, 'raffles/campaign_details.html', context)


@login_required
def raffle_list(request):
    """Lista de campanhas"""
    if request.user.is_staff:
        raffles = Raffle.objects.all()
    else:
        raffles = Raffle.objects.filter(status=Raffle.Status.ACTIVE)

    context = {
        'raffles': raffles,
    }
    return render(request, 'raffles/list.html', context)


@login_required
def raffle_create(request):
    """Criar nova campanha"""
    if request.method == 'POST':
        try:
            prize_image_base64 = ''
            if 'prize_image' in request.FILES:
                image_file = request.FILES['prize_image']
                image_data = image_file.read()
                prize_image_base64 = base64.b64encode(image_data).decode('utf-8')

            raffle = Raffle.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                prize_name=request.POST.get('prize_name'),
                prize_description=request.POST.get('prize_description', ''),
                prize_image_base64=prize_image_base64,
                total_numbers=int(request.POST.get('total_numbers')),
                price_per_number=float(request.POST.get('price_per_number')),
                fee_percentage=float(request.POST.get('fee_percentage', 0)),
                status=request.POST.get('status', 'draft'),
                draw_date=request.POST.get('draw_date') if request.POST.get('draw_date') else None,
                inviter_bonus=int(request.POST.get('inviter_bonus', 2)),
                invitee_bonus=int(request.POST.get('invitee_bonus', 1)),
                enable_progressive_bonus=request.POST.get('enable_progressive_bonus') == '1',
                progressive_bonus_every=int(request.POST.get('progressive_bonus_every', 20)),
            )

            raffle.initialize_numbers()

            # Processar números premiados
            prize_numbers_data = {}
            for key in request.POST.keys():
                match = re.match(r'prize_numbers\[(\d+)\]\[(\w+)\]', key)
                if match:
                    index, field = match.groups()
                    if index not in prize_numbers_data:
                        prize_numbers_data[index] = {}
                    prize_numbers_data[index][field] = request.POST.get(key)

            # Criar números premiados
            for prize_data in prize_numbers_data.values():
                if all(k in prize_data for k in ['number', 'prize_amount', 'release_min', 'release_max']):
                    PrizeNumber.objects.create(
                        raffle=raffle,
                        number=int(prize_data['number']),
                        prize_amount=float(prize_data['prize_amount']),
                        release_percentage_min=float(prize_data['release_min']),
                        release_percentage_max=float(prize_data['release_max'])
                    )

            messages.success(request, 'Campanha criada com sucesso!')
            return redirect('raffle_list')

        except Exception as e:
            messages.error(request, f'Erro ao criar campanha: {str(e)}')

    return render(request, 'raffles/create.html')


@login_required
def raffle_edit(request, pk):
    """Editar campanha existente"""
    raffle = get_object_or_404(Raffle, pk=pk)

    if request.method == 'POST':
        try:
            # Check if total_numbers is being increased
            new_total_numbers = int(request.POST.get('total_numbers', raffle.total_numbers))
            if new_total_numbers > raffle.total_numbers:
                raffle.expand_numbers(new_total_numbers)
                messages.success(request, f'Campanha expandida de {raffle.total_numbers} para {new_total_numbers} titulos!')
            elif new_total_numbers < raffle.total_numbers:
                messages.warning(request, 'Nao e possivel reduzir a quantidade de titulos. Apenas aumentar.')

            # Update basic fields
            raffle.name = request.POST.get('name')
            raffle.description = request.POST.get('description', '')
            raffle.prize_name = request.POST.get('prize_name')
            raffle.prize_description = request.POST.get('prize_description', '')
            raffle.price_per_number = float(request.POST.get('price_per_number'))
            raffle.fee_percentage = float(request.POST.get('fee_percentage', 0))
            raffle.status = request.POST.get('status', 'draft')
            raffle.inviter_bonus = int(request.POST.get('inviter_bonus', 2))
            raffle.invitee_bonus = int(request.POST.get('invitee_bonus', 1))
            raffle.enable_progressive_bonus = request.POST.get('enable_progressive_bonus') == '1'
            raffle.progressive_bonus_every = int(request.POST.get('progressive_bonus_every', 20))

            # Update draw_date if provided
            if request.POST.get('draw_date'):
                raffle.draw_date = request.POST.get('draw_date')

            # Update image if new one is uploaded
            if 'prize_image' in request.FILES:
                image_file = request.FILES['prize_image']
                image_data = image_file.read()
                raffle.prize_image_base64 = base64.b64encode(image_data).decode('utf-8')

            raffle.save()

            # Processar números premiados (remover antigos e adicionar novos)
            raffle.prize_numbers.all().delete()

            prize_numbers_data = {}
            for key in request.POST.keys():
                match = re.match(r'prize_numbers\[(\d+)\]\[(\w+)\]', key)
                if match:
                    index, field = match.groups()
                    if index not in prize_numbers_data:
                        prize_numbers_data[index] = {}
                    prize_numbers_data[index][field] = request.POST.get(key)

            # Criar números premiados
            for prize_data in prize_numbers_data.values():
                if all(k in prize_data for k in ['number', 'prize_amount', 'release_min', 'release_max']):
                    PrizeNumber.objects.create(
                        raffle=raffle,
                        number=int(prize_data['number']),
                        prize_amount=float(prize_data['prize_amount']),
                        release_percentage_min=float(prize_data['release_min']),
                        release_percentage_max=float(prize_data['release_max'])
                    )

            messages.success(request, 'Campanha atualizada com sucesso!')
            return redirect('raffle_list')

        except Exception as e:
            messages.error(request, f'Erro ao atualizar campanha: {str(e)}')

    context = {
        'raffle': raffle,
    }
    return render(request, 'raffles/edit.html', context)


@login_required
def supporters(request):
    """Meus apoiadores"""
    if request.user.is_staff:
        orders = RaffleOrder.objects.filter(status=RaffleOrder.Status.PAID).select_related('user', 'raffle')
    else:
        orders = []

    context = {
        'orders': orders,
    }
    return render(request, 'raffles/supporters.html', context)


@login_required
def affiliates(request):
    """Gerenciar afiliados"""
    referrals = Referral.objects.all() if request.user.is_staff else []

    context = {
        'referrals': referrals,
    }
    return render(request, 'raffles/affiliates.html', context)


@login_required
def settings_view(request):
    """Configuracoes"""
    return render(request, 'raffles/settings.html')


# Public Views (no login required)
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


def raffle_public_view(request, slug):
    """Pagina publica da rifa para vendas"""
    raffle = get_object_or_404(Raffle, slug=slug, status=Raffle.Status.ACTIVE)
    
    # Get all numbers with their status
    numbers = RaffleNumber.objects.filter(raffle=raffle).order_by('number')
    
    context = {
        'raffle': raffle,
        'numbers': numbers,
        'numbers_list': list(numbers.values('number', 'status')),
    }
    return render(request, 'raffles/public_view.html', context)
