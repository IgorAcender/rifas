from rest_framework import serializers
from .models import Raffle, RaffleOrder, RaffleNumber, Referral
from django.core.exceptions import ValidationError as DjangoValidationError


class RaffleSerializer(serializers.ModelSerializer):
    """Serializer for Raffle listing"""

    class Meta:
        model = Raffle
        fields = [
            'id', 'name', 'description',
            'prize_name', 'prize_description', 'prize_image_base64',
            'total_numbers', 'price_per_number',
            'numbers_sold', 'numbers_available',
            'status', 'draw_date', 'created_at'
        ]
        read_only_fields = fields


class RaffleNumberSerializer(serializers.ModelSerializer):
    """Serializer for RaffleNumber"""

    class Meta:
        model = RaffleNumber
        fields = ['number', 'status', 'source', 'sold_at']


class RaffleOrderSerializer(serializers.ModelSerializer):
    """Serializer for RaffleOrder"""
    raffle_name = serializers.CharField(source='raffle.name', read_only=True)
    numbers = serializers.SerializerMethodField()

    class Meta:
        model = RaffleOrder
        fields = [
            'id', 'raffle', 'raffle_name', 'quantity', 'amount',
            'status', 'payment_method', 'payment_id',
            'numbers', 'created_at', 'paid_at'
        ]
        read_only_fields = ['id', 'amount', 'status', 'payment_id', 'numbers', 'created_at', 'paid_at']

    def get_numbers(self, obj):
        """Return numbers only if order is paid"""
        if obj.status == RaffleOrder.Status.PAID:
            return sorted(obj.allocated_numbers.values_list('number', flat=True))
        return None

    def validate(self, data):
        raffle = data['raffle']

        # Check if raffle is active
        if raffle.status != Raffle.Status.ACTIVE:
            raise serializers.ValidationError('Esta rifa não está ativa')

        # Initialize numbers if not already done
        if not raffle.numbers.exists():
            raffle.initialize_numbers()
            # Refresh from database to get updated counts
            raffle.refresh_from_db()

        # Release expired reservations before checking availability
        raffle.release_expired_reservations()
        raffle.refresh_from_db()

        # Get current availability
        available = raffle.numbers_available
        requested = data['quantity']
        
        print(f"DEBUG: Raffle '{raffle.name}' - Total: {raffle.total_numbers}, Sold: {raffle.numbers_sold}, Reserved: {raffle.numbers_reserved}, Available: {available}, Requested: {requested}")

        # Check if there are enough numbers
        if available < requested:
            raise serializers.ValidationError(f'Não há números suficientes disponíveis. Disponível: {available}, Solicitado: {requested}')

        # Calculate amount
        data['amount'] = raffle.price_per_number * data['quantity']

        return data

    def create(self, validated_data):
        # Set user from request
        validated_data['user'] = self.context['request'].user
        user = validated_data['user']

        # Check if there's a referral code
        referral_code = self.context.get('referral_code')
        print(f"🛒 DEBUG: Creating order for user {user.name}, referral_code: {referral_code}")

        order = super().create(validated_data)

        # Allocate numbers (may raise Django ValidationError in race conditions)
        try:
            order.allocate_numbers()
        except DjangoValidationError as e:
            # Convert to DRF serializer ValidationError so caller receives 400
            raise serializers.ValidationError(str(e))

        # Handle referral if present
        if referral_code:
            print(f"🎁 DEBUG: Processing referral code: {referral_code}")
            try:
                referral = Referral.objects.get(code=referral_code, raffle=order.raffle)
                print(f"📋 DEBUG: Referral found - status={referral.status}, inviter={referral.inviter.name}")
                
                if referral.status == Referral.Status.PENDING:
                    print(f"🎯 DEBUG: Redeeming referral for user {user.name}")
                    referral.redeem(user)
                    # Store referral in order for later bonus allocation
                    order.referral_code = referral_code
                    order.save(update_fields=['referral_code'])
                    print(f"✅ DEBUG: Referral redeemed and stored in order")
                else:
                    print(f"⚠️  DEBUG: Referral status is {referral.status}, not PENDING")
            except Referral.DoesNotExist:
                print(f"❌ DEBUG: Referral code {referral_code} not found")

        return order


class ReferralSerializer(serializers.ModelSerializer):
    """Serializer for Referral"""
    raffle_name = serializers.CharField(source='raffle.name', read_only=True)
    inviter_name = serializers.CharField(source='inviter.name', read_only=True)
    invitee_name = serializers.CharField(source='invitee.name', read_only=True)

    class Meta:
        model = Referral
        fields = [
            'code', 'raffle', 'raffle_name',
            'inviter_name', 'invitee_name',
            'status', 'clicks', 'created_at'
        ]
        read_only_fields = ['code', 'inviter_name', 'invitee_name', 'status', 'clicks', 'created_at']

    def create(self, validated_data):
        validated_data['inviter'] = self.context['request'].user
        return super().create(validated_data)
