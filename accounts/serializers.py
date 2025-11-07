from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'whatsapp', 'name', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class WhatsAppLoginSerializer(serializers.Serializer):
    """
    Serializer for WhatsApp login.
    Creates user if doesn't exist, returns JWT tokens.
    """
    whatsapp = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=150, required=False)

    def validate_whatsapp(self, value):
        """Normalize WhatsApp number"""
        return ''.join(filter(str.isdigit, value))

    def create(self, validated_data):
        """Get or create user and return with tokens"""
        whatsapp = validated_data['whatsapp']
        name = validated_data.get('name')

        user, created = User.objects.get_or_create(
            whatsapp=whatsapp,
            defaults={'name': name or whatsapp}
        )

        # Update name if provided and changed
        if name and user.name != name:
            user.name = name
            user.save(update_fields=['name'])

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'created': created
        }
