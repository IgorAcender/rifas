from rest_framework import serializers
from .models import Raffle, RaffleOrder, RaffleNumber, Referral


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

        # Check if there are enough numbers
        if raffle.numbers_available < data['quantity']:
            raise serializers.ValidationError('Não há números suficientes disponíveis')

        # Calculate amount
        data['amount'] = raffle.price_per_number * data['quantity']

        return data

    def create(self, validated_data):
        # Set user from request
        validated_data['user'] = self.context['request'].user
        order = super().create(validated_data)

        # Allocate numbers
        order.allocate_numbers()

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
