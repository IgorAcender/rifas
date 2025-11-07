from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Raffle, RaffleOrder, Referral
from .serializers import RaffleSerializer, RaffleOrderSerializer, ReferralSerializer


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

        serializer = RaffleOrderSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    """Dashboard principal"""
    user_raffles = Raffle.objects.filter(winner=request.user).count()
    user_orders = RaffleOrder.objects.filter(user=request.user, status=RaffleOrder.Status.PAID).count()

    context = {
        'user_raffles': user_raffles,
        'user_orders': user_orders,
    }
    return render(request, 'raffles/dashboard.html', context)


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
                status=request.POST.get('status', 'draft'),
                draw_date=request.POST.get('draw_date') if request.POST.get('draw_date') else None,
                inviter_bonus=int(request.POST.get('inviter_bonus', 2)),
                invitee_bonus=int(request.POST.get('invitee_bonus', 1)),
            )

            raffle.initialize_numbers()
            messages.success(request, 'Campanha criada com sucesso!')
            return redirect('raffle_list')

        except Exception as e:
            messages.error(request, f'Erro ao criar campanha: {str(e)}')

    return render(request, 'raffles/create.html')


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
