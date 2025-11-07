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
