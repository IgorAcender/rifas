from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Raffle, RaffleOrder, Referral, RaffleNumber, PrizeNumber
from .serializers import RaffleSerializer, RaffleOrderSerializer, ReferralSerializer
from django.utils import timezone
from datetime import timedelta
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

    @action(detail=True, methods=['get'], url_path='check-reservation')
    def check_reservation(self, request, pk=None):
        """Verificar se ainda há uma reserva ativa e quanto tempo resta"""
        from django.db.models import Q
        
        raffle = self.get_object()
        
        # Release expired reservations first
        raffle.release_expired_reservations()
        
        # Pegar reservas ativas do usuário
        user_reservations = RaffleNumber.objects.filter(
            raffle=raffle,
            user=request.user,
            status=RaffleNumber.Status.RESERVED,
            reserved_expires_at__isnull=False
        )
        
        if not user_reservations.exists():
            return Response({
                'has_reservation': False,
                'message': 'Nenhuma reserva ativa'
            })
        
        # Pegar a reserva com maior tempo restante
        reservation = user_reservations.order_by('reserved_expires_at').last()
        now = timezone.now()
        
        if reservation.reserved_expires_at <= now:
            # Liberou enquanto checava
            reservation.status = RaffleNumber.Status.AVAILABLE
            reservation.user = None
            reservation.order = None
            reservation.reserved_at = None
            reservation.reserved_expires_at = None
            reservation.save()
            
            return Response({
                'has_reservation': False,
                'message': 'Sua reserva expirou',
                'numbers': []
            })
        
        # Calcular tempo restante em segundos
        time_remaining = (reservation.reserved_expires_at - now).total_seconds()
        
        # Pegar todos os números reservados
        reserved_numbers = list(user_reservations.values_list('number', flat=True))
        
        return Response({
            'has_reservation': True,
            'numbers': reserved_numbers,
            'expires_at': reservation.reserved_expires_at.isoformat(),
            'time_remaining_seconds': int(time_remaining),
            'message': f'Seu pedido expira em {int(time_remaining // 60)} minutos'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='reservation-status')
    def reservation_status(self, request, pk=None):
        """API simples para verificar tempo de reserva (usado pelo frontend)"""
        raffle = self.get_object()
        
        # Verificar reservas expiradas
        now = timezone.now()
        expired = RaffleNumber.objects.filter(
            raffle=raffle,
            status=RaffleNumber.Status.RESERVED,
            reserved_expires_at__lt=now
        )
        
        # Liberar expiradas
        for num in expired:
            num.status = RaffleNumber.Status.AVAILABLE
            num.user = None
            num.order = None
            num.reserved_at = None
            num.reserved_expires_at = None
            num.save()
        
        # Pegar reserva do usuário
        user_reservation = RaffleNumber.objects.filter(
            raffle=raffle,
            user=request.user,
            status=RaffleNumber.Status.RESERVED,
            reserved_expires_at__isnull=False
        ).order_by('reserved_expires_at').last()
        
        if not user_reservation:
            return Response({'has_active_reservation': False})
        
        if user_reservation.reserved_expires_at <= now:
            return Response({'has_active_reservation': False})
        
        time_remaining = (user_reservation.reserved_expires_at - now).total_seconds()
        
        return Response({
            'has_active_reservation': True,
            'time_remaining_seconds': int(time_remaining),
            'expires_at': user_reservation.reserved_expires_at.isoformat()
        })

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

            # Estatísticas de números premiados
            from .models import PrizeNumber
            total_prize_numbers = PrizeNumber.objects.filter(raffle=raffle).count()
            won_prize_numbers = PrizeNumber.objects.filter(raffle=raffle, is_won=True).count()

            # Calcular taxa total arrecadada
            fee_amount = total_revenue * (raffle.fee_percentage / 100)
            net_revenue = total_revenue - fee_amount

            campaigns_stats.append({
                'raffle': raffle,
                'numbers_sold': numbers_sold,
                'numbers_reserved': numbers_reserved,
                'numbers_available': numbers_available,
                'available_value': numbers_available * raffle.price_per_number,
                'total_revenue': total_revenue,
                'fee_amount': fee_amount,
                'net_revenue': net_revenue,
                'unique_buyers': unique_buyers,
                'percentage_sold': round((numbers_sold / raffle.total_numbers) * 100, 1) if raffle.total_numbers > 0 else 0,
                'total_prize_numbers': total_prize_numbers,
                'won_prize_numbers': won_prize_numbers,
                'prize_percentage': round((won_prize_numbers / total_prize_numbers) * 100, 1) if total_prize_numbers > 0 else 0,
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
    available_value = numbers_available * raffle.price_per_number

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

    # Números Premiados (Prize Numbers)
    prize_numbers = PrizeNumber.objects.filter(raffle=raffle).order_by('number')
    prize_winners = []
    for prize in prize_numbers:
        prize_winners.append({
            'number': prize.number,
            'prize_amount': prize.prize_amount,
            'is_released': prize.is_released,
            'is_won': prize.is_won,
            'winner': prize.winner,
            'won_at': prize.won_at,
            'release_percentage_min': prize.release_percentage_min,
            'release_percentage_max': prize.release_percentage_max,
        })

    context = {
        'raffle': raffle,
        'numbers_sold': numbers_sold,
        'numbers_reserved': numbers_reserved,
        'numbers_available': numbers_available,
        'available_value': available_value,
        'total_revenue': total_revenue,
        'fee_amount': fee_amount,
        'net_revenue': net_revenue,
        'percentage_sold': round((numbers_sold / raffle.total_numbers) * 100, 1) if raffle.total_numbers > 0 else 0,
        'buyers_list': buyers_list,
        'total_buyers': len(buyers_list),
        'total_referrals': total_referrals,
        'top_inviters': top_inviters,
        'current_filter': filter_by,
        'prize_winners': prize_winners,
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
            import logging
            logger = logging.getLogger(__name__)

            prize_image_base64 = ''
            logger.info(f"FILES received: {list(request.FILES.keys())}")

            if 'prize_image' in request.FILES:
                image_file = request.FILES['prize_image']
                logger.info(f"Image file: name={image_file.name}, size={image_file.size}")
                image_data = image_file.read()
                encoded_data = base64.b64encode(image_data).decode('utf-8')
                # Detect content type from file extension
                content_type = 'image/jpeg'
                if image_file.name.lower().endswith('.png'):
                    content_type = 'image/png'
                elif image_file.name.lower().endswith('.gif'):
                    content_type = 'image/gif'
                elif image_file.name.lower().endswith('.webp'):
                    content_type = 'image/webp'
                prize_image_base64 = f'data:{content_type};base64,{encoded_data}'
                logger.info(f"Image encoded: type={content_type}, base64_length={len(encoded_data)}")
            else:
                logger.warning("No 'prize_image' in request.FILES")

            # Preparar valores numéricos com tratamento de strings vazias
            total_numbers_str = request.POST.get('total_numbers', '').strip()
            price_per_number_str = request.POST.get('price_per_number', '').strip()
            fee_percentage_str = request.POST.get('fee_percentage', '').strip()
            inviter_bonus_str = request.POST.get('inviter_bonus', '').strip()
            invitee_bonus_str = request.POST.get('invitee_bonus', '').strip()
            progressive_bonus_every_str = request.POST.get('progressive_bonus_every', '').strip()
            purchase_bonus_every_str = request.POST.get('purchase_bonus_every', '').strip()
            purchase_bonus_amount_str = request.POST.get('purchase_bonus_amount', '').strip()
            milestone_quantity_str = request.POST.get('milestone_quantity', '').strip()

            raffle = Raffle.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                prize_name=request.POST.get('prize_name'),
                prize_description=request.POST.get('prize_description', ''),
                prize_image_base64=prize_image_base64,
                total_numbers=int(total_numbers_str) if total_numbers_str else 100,
                price_per_number=float(price_per_number_str) if price_per_number_str else 0.01,
                fee_percentage=float(fee_percentage_str) if fee_percentage_str else 0,
                status=request.POST.get('status', 'draft'),
                draw_date=request.POST.get('draw_date') if request.POST.get('draw_date') else None,
                inviter_bonus=int(inviter_bonus_str) if inviter_bonus_str else 2,
                invitee_bonus=int(invitee_bonus_str) if invitee_bonus_str else 1,
                enable_progressive_bonus=request.POST.get('enable_progressive_bonus') == '1',
                progressive_bonus_every=int(progressive_bonus_every_str) if progressive_bonus_every_str else 20,
                # Purchase bonus
                enable_purchase_bonus=request.POST.get('enable_purchase_bonus') == '1',
                purchase_bonus_every=int(purchase_bonus_every_str) if purchase_bonus_every_str else 10,
                purchase_bonus_amount=int(purchase_bonus_amount_str) if purchase_bonus_amount_str else 1,
                # Milestone bonus
                enable_milestone_bonus=request.POST.get('enable_milestone_bonus') == '1',
                milestone_quantity=int(milestone_quantity_str) if milestone_quantity_str else 50,
                milestone_prize_name=request.POST.get('milestone_prize_name', ''),
                milestone_prize_description=request.POST.get('milestone_prize_description', ''),
                milestone_prize_url=request.POST.get('milestone_prize_url', ''),
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
                    # Validar se os valores não estão vazios
                    number_str = prize_data['number'].strip()
                    prize_amount_str = prize_data['prize_amount'].strip()
                    release_min_str = prize_data['release_min'].strip()
                    release_max_str = prize_data['release_max'].strip()
                    
                    # Criar apenas se todos os valores forem válidos
                    if number_str and prize_amount_str and release_min_str and release_max_str:
                        PrizeNumber.objects.create(
                            raffle=raffle,
                            number=int(number_str),
                            prize_amount=float(prize_amount_str),
                            release_percentage_min=float(release_min_str),
                            release_percentage_max=float(release_max_str)
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
            
            # Converter valores numéricos com tratamento de strings vazias
            price_per_number = request.POST.get('price_per_number', '').strip()
            raffle.price_per_number = float(price_per_number) if price_per_number else 0.01
            
            fee_percentage = request.POST.get('fee_percentage', '').strip()
            raffle.fee_percentage = float(fee_percentage) if fee_percentage else 0
            
            raffle.status = request.POST.get('status', 'draft')
            
            inviter_bonus = request.POST.get('inviter_bonus', '').strip()
            raffle.inviter_bonus = int(inviter_bonus) if inviter_bonus else 2
            
            invitee_bonus = request.POST.get('invitee_bonus', '').strip()
            raffle.invitee_bonus = int(invitee_bonus) if invitee_bonus else 1
            
            raffle.enable_progressive_bonus = request.POST.get('enable_progressive_bonus') == '1'
            
            progressive_bonus_every = request.POST.get('progressive_bonus_every', '').strip()
            raffle.progressive_bonus_every = int(progressive_bonus_every) if progressive_bonus_every else 20
            
            # Purchase bonus
            raffle.enable_purchase_bonus = request.POST.get('enable_purchase_bonus') == '1'
            
            purchase_bonus_every = request.POST.get('purchase_bonus_every', '').strip()
            raffle.purchase_bonus_every = int(purchase_bonus_every) if purchase_bonus_every else 10
            
            purchase_bonus_amount = request.POST.get('purchase_bonus_amount', '').strip()
            raffle.purchase_bonus_amount = int(purchase_bonus_amount) if purchase_bonus_amount else 1
            
            # Milestone bonus
            raffle.enable_milestone_bonus = request.POST.get('enable_milestone_bonus') == '1'
            
            milestone_quantity = request.POST.get('milestone_quantity', '').strip()
            raffle.milestone_quantity = int(milestone_quantity) if milestone_quantity else 50
            
            raffle.milestone_prize_name = request.POST.get('milestone_prize_name', '')
            raffle.milestone_prize_description = request.POST.get('milestone_prize_description', '')
            raffle.milestone_prize_url = request.POST.get('milestone_prize_url', '')

            # Update draw_date if provided
            if request.POST.get('draw_date'):
                raffle.draw_date = request.POST.get('draw_date')

            # Update image if new one is uploaded
            if 'prize_image' in request.FILES:
                image_file = request.FILES['prize_image']
                image_data = image_file.read()
                encoded_data = base64.b64encode(image_data).decode('utf-8')
                # Detect content type from file extension
                content_type = 'image/jpeg'
                if image_file.name.lower().endswith('.png'):
                    content_type = 'image/png'
                elif image_file.name.lower().endswith('.gif'):
                    content_type = 'image/gif'
                elif image_file.name.lower().endswith('.webp'):
                    content_type = 'image/webp'
                raffle.prize_image_base64 = f'data:{content_type};base64,{encoded_data}'

            raffle.save()

            # Processar números premiados
            # NÃO deletar números que já foram liberados ou ganhos para preservar histórico
            # Apenas deletar números que ainda não foram liberados
            raffle.prize_numbers.filter(is_released=False, is_won=False).delete()

            prize_numbers_data = {}
            for key in request.POST.keys():
                match = re.match(r'prize_numbers\[(\d+)\]\[(\w+)\]', key)
                if match:
                    index, field = match.groups()
                    if index not in prize_numbers_data:
                        prize_numbers_data[index] = {}
                    prize_numbers_data[index][field] = request.POST.get(key)

            # Criar/atualizar números premiados
            for prize_data in prize_numbers_data.values():
                if all(k in prize_data for k in ['number', 'prize_amount', 'release_min', 'release_max']):
                    # Validar se os valores não estão vazios
                    number_str = prize_data['number'].strip()
                    prize_amount_str = prize_data['prize_amount'].strip()
                    release_min_str = prize_data['release_min'].strip()
                    release_max_str = prize_data['release_max'].strip()
                    
                    # Criar apenas se todos os valores forem válidos
                    if number_str and prize_amount_str and release_min_str and release_max_str:
                        prize_number_value = int(number_str)
                        
                        # Verificar se já existe um número premiado para este número
                        existing = raffle.prize_numbers.filter(number=prize_number_value).first()
                        
                        if existing:
                            # Se já foi liberado ou ganho, não alterar
                            if not existing.is_released and not existing.is_won:
                                # Atualizar os dados
                                existing.prize_amount = float(prize_amount_str)
                                existing.release_percentage_min = float(release_min_str)
                                existing.release_percentage_max = float(release_max_str)
                                existing.save()
                        else:
                            # Verificar se o RaffleNumber correspondente já foi vendido
                            raffle_number = raffle.numbers.filter(number=prize_number_value).first()
                            if raffle_number and raffle_number.status == RaffleNumber.Status.SOLD:
                                print(f"⚠️  Não é possível criar número premiado {prize_number_value} - número já foi vendido")
                                continue
                            
                            # Criar novo
                            PrizeNumber.objects.create(
                                raffle=raffle,
                                number=prize_number_value,
                                prize_amount=float(prize_amount_str),
                                release_percentage_min=float(release_min_str),
                                release_percentage_max=float(release_max_str)
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
def raffle_delete(request, pk):
    """Delete a raffle campaign"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"raffle_delete called - pk={pk}, method={request.method}, user={request.user}")

    raffle = get_object_or_404(Raffle, pk=pk)

    # Only allow staff users to delete campaigns
    if not request.user.is_staff:
        logger.warning(f"Non-staff user {request.user} tried to delete raffle {pk}")
        messages.error(request, 'Você não tem permissão para excluir campanhas.')
        return redirect('raffle_list')

    if request.method == 'POST':
        try:
            raffle_name = raffle.name
            logger.info(f"Deleting raffle: {raffle_name} (id={pk})")
            # Django will cascade delete related objects (numbers, orders, etc.)
            raffle.delete()
            logger.info(f"Raffle deleted successfully: {raffle_name}")
            messages.success(request, f'Campanha "{raffle_name}" excluída com sucesso!')
            return redirect('raffle_list')
        except Exception as e:
            logger.error(f"Error deleting raffle {pk}: {str(e)}")
            messages.error(request, f'Erro ao excluir campanha: {str(e)}')
            return redirect('raffle_edit', pk=pk)

    # If GET request, redirect back to edit page
    logger.info(f"GET request to raffle_delete - redirecting to edit")
    return redirect('raffle_edit', pk=pk)


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
    from django.conf import settings
    
    raffle = get_object_or_404(Raffle, slug=slug, status=Raffle.Status.ACTIVE)
    
    # Get all numbers with their status
    numbers = RaffleNumber.objects.filter(raffle=raffle).order_by('number')
    
    # Get prize numbers (todos - para mostrar como disponíveis e gerar interesse)
    prize_numbers = raffle.prize_numbers.all().order_by('release_percentage_min', 'number')
    
    # Get user's numbers if authenticated
    user_numbers = []
    if request.user.is_authenticated:
        user_numbers = list(
            RaffleNumber.objects.filter(
                raffle=raffle, 
                user=request.user,
                status__in=[RaffleNumber.Status.SOLD, RaffleNumber.Status.RESERVED]
            ).values_list('number', flat=True)
        )
    
    context = {
        'raffle': raffle,
        'numbers': numbers,
        'numbers_list': list(numbers.values('number', 'status')),
        'admin_whatsapp': settings.ADMIN_WHATSAPP,
        'user_numbers': user_numbers,
        'prize_numbers': prize_numbers,
    }
    return render(request, 'raffles/public_view.html', context)


@login_required
def site_config_view(request):
    """View para configurar logo e identidade visual do site"""
    from .models import SiteConfiguration
    from django.contrib import messages
    import logging

    logger = logging.getLogger(__name__)
    config = SiteConfiguration.get_config()

    if request.method == 'POST':
        # Update site name
        site_name = request.POST.get('site_name', '').strip()
        if site_name:
            config.site_name = site_name

        # Update logo if provided
        logo_base64 = request.POST.get('logo_base64', '').strip()
        if logo_base64:
            config.logo_base64 = logo_base64

        # Update notification contacts
        admin_phones = request.POST.get('admin_phones', '').strip()
        config.admin_phones = admin_phones
        
        group_phones = request.POST.get('group_phones', '').strip()
        config.group_phones = group_phones

        # Update home redirect raffle
        home_redirect_raffle_id = request.POST.get('home_redirect_raffle', '').strip()
        logger.info(f"DEBUG: home_redirect_raffle_id recebido: '{home_redirect_raffle_id}'")
        
        if home_redirect_raffle_id:
            try:
                raffle = Raffle.objects.get(id=int(home_redirect_raffle_id))
                config.home_redirect_raffle = raffle
                config.save()  # Salvar imediatamente para garantir
                logger.info(f"DEBUG: home_redirect_raffle definido para {raffle.name} (ID: {raffle.id})")
            except (Raffle.DoesNotExist, ValueError) as e:
                config.home_redirect_raffle = None
                logger.error(f"DEBUG: Erro ao definir raffle: {e}")
        else:
            config.home_redirect_raffle = None
            logger.info(f"DEBUG: home_redirect_raffle_id vazio, limpando campo")

        # Salvar outras configurações
        site_name = request.POST.get('site_name', '').strip()
        if site_name:
            config.site_name = site_name

        # Update logo if provided
        logo_base64 = request.POST.get('logo_base64', '').strip()
        if logo_base64:
            config.logo_base64 = logo_base64

        # Update notification contacts
        admin_phones = request.POST.get('admin_phones', '').strip()
        config.admin_phones = admin_phones
        
        group_phones = request.POST.get('group_phones', '').strip()
        config.group_phones = group_phones

        config.save()
        logger.info(f"DEBUG: SiteConfiguration salva completa. home_redirect_raffle = {config.home_redirect_raffle} (ID: {config.home_redirect_raffle_id})")
        
        messages.success(request, 'Configurações salvas com sucesso!')
        return redirect('site_config')

    # Get all active raffles for the dropdown
    active_raffles = Raffle.objects.filter(status=Raffle.Status.ACTIVE).order_by('-created_at')
    logger.info(f"DEBUG: Campanhas ativas: {active_raffles.count()}")
    
    return render(request, 'raffles/site_config.html', {
        'config': config,
        'active_raffles': active_raffles
    })


@login_required
def raffle_settings_view(request, raffle_id):
    """View para configurar WhatsApp e outras configurações de uma rifa"""
    from django.contrib import messages
    
    try:
        raffle = Raffle.objects.get(id=raffle_id)
    except Raffle.DoesNotExist:
        messages.error(request, 'Rifa não encontrada!')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        # Update WhatsApp
        admin_whatsapp = request.POST.get('admin_whatsapp', '').strip()
        raffle.admin_whatsapp = admin_whatsapp
        
        # Update Milestone Bonus settings
        raffle.enable_milestone_bonus = request.POST.get('enable_milestone_bonus') == 'on'
        
        if raffle.enable_milestone_bonus:
            raffle.milestone_quantity = int(request.POST.get('milestone_quantity', 50))
            raffle.milestone_prize_name = request.POST.get('milestone_prize_name', '').strip()
            raffle.milestone_prize_description = request.POST.get('milestone_prize_description', '').strip()
            raffle.milestone_prize_url = request.POST.get('milestone_prize_url', '').strip()
        
        raffle.save()
        
        messages.success(request, f'Configurações de "{raffle.name}" salvas com sucesso!')
        return redirect('raffle_settings', raffle_id=raffle.id)
    
    return render(request, 'raffles/raffle_settings.html', {'raffle': raffle})


@login_required
def admin_dashboard(request):
    """View para dashboard administrativo"""
    raffles = Raffle.objects.all().order_by('-created_at')
    return render(request, 'raffles/admin_dashboard.html', {'raffles': raffles})
def raffle_draw(request):
    """View para sortear ganhador de uma campanha"""
    from django.contrib import messages
    import json

    # Buscar apenas campanhas ativas ou finalizadas
    raffles = Raffle.objects.filter(
        status__in=[Raffle.Status.ACTIVE, Raffle.Status.FINISHED]
    ).order_by('-created_at')

    winner_data = None
    raffle_id = request.GET.get('raffle_id')

    if request.method == 'POST' and raffle_id:
        try:
            raffle = Raffle.objects.get(id=raffle_id)

            # Buscar todos os números vendidos (pagos)
            sold_numbers = RaffleNumber.objects.filter(
                raffle=raffle,
                order__status='paid'
            ).select_related('order', 'order__user')

            if not sold_numbers.exists():
                messages.error(request, 'Nenhum número vendido para esta campanha.')
            else:
                # Sortear um número aleatório
                import random
                sold_numbers_list = list(sold_numbers)
                winner_number = random.choice(sold_numbers_list)

                # Preparar dados do ganhador
                user = winner_number.order.user
                phone = user.whatsapp or ''

                # Mascarar telefone: (37) 9****-1626
                masked_phone = ''
                if len(phone) >= 4:
                    # Formato: (XX) 9****-XXXX
                    if len(phone) == 11:  # Celular com 9
                        masked_phone = f"({phone[:2]}) {phone[2]}****-{phone[-4:]}"
                    elif len(phone) == 10:  # Fixo
                        masked_phone = f"({phone[:2]}) ****-{phone[-4:]}"
                    else:
                        masked_phone = f"****-{phone[-4:]}"
                else:
                    masked_phone = "****"

                # Buscar todos os números comprados por esse usuário nesta campanha
                user_numbers = RaffleNumber.objects.filter(
                    raffle=raffle,
                    order__user=user,
                    order__status='paid'
                ).order_by('number').values_list('number', flat=True)

                # Converter para lista
                user_numbers_list = list(user_numbers)
                total_numbers = len(user_numbers_list)

                # Buscar números bônus ganhos pelo usuário nesta campanha
                # Buscar números que foram dados como bônus (purchase_bonus, milestone_bonus ou referral)
                bonus_numbers = RaffleNumber.objects.filter(
                    raffle=raffle,
                    order__user=user,
                    order__status='paid',
                    source__in=['purchase_bonus', 'milestone_bonus', 'referral_inviter', 'referral_invitee']
                ).order_by('number').values_list('number', flat=True)

                bonus_numbers_list = list(bonus_numbers)
                total_bonus = len(bonus_numbers_list)

                winner_data = {
                    'number': winner_number.number,
                    'name': user.name,
                    'masked_phone': masked_phone,
                    'real_phone': phone,
                    'total_numbers': total_numbers,
                    'user_numbers': user_numbers_list,  # Lista de todos os números
                    'bonus_numbers': bonus_numbers_list,  # Lista dos números bônus
                    'total_bonus': total_bonus,  # Quantidade de bônus
                    'raffle_name': raffle.name,
                    'user_id': user.id,
                    'order_id': winner_number.order.id,
                }

                print(f"DEBUG: Winner data = {winner_data}")
                # messages.success(request, f'Ganhador sorteado: {user.name}!')  # Removido - polui outras páginas

        except Raffle.DoesNotExist:
            messages.error(request, 'Campanha não encontrada.')
        except Exception as e:
            messages.error(request, f'Erro ao sortear: {str(e)}')

    context = {
        'raffles': raffles,
        'selected_raffle_id': raffle_id,
        'winner_data': json.dumps(winner_data) if winner_data else None,
    }

    return render(request, 'raffles/draw.html', context)
