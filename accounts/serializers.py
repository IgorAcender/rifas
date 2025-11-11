from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'whatsapp', 'name', 'email', 'cpf', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class WhatsAppLoginSerializer(serializers.Serializer):
    """
    Serializer for WhatsApp login.
    Creates user if doesn't exist, returns JWT tokens.
    """
    whatsapp = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=150, required=False)
    cpf = serializers.CharField(max_length=14, required=False, allow_blank=True)

    def validate_whatsapp(self, value):
        """Normalize WhatsApp number"""
        return ''.join(filter(str.isdigit, value))

    def validate_cpf(self, value):
        """Normalize CPF (remove formatting)"""
        if value:
            return ''.join(filter(str.isdigit, value))
        return value

    def create(self, validated_data):
        """Get or create user and return with tokens"""
        whatsapp = validated_data['whatsapp']
        name = validated_data.get('name')
        cpf = validated_data.get('cpf')

        user, created = User.objects.get_or_create(
            whatsapp=whatsapp,
            defaults={'name': name or whatsapp, 'cpf': cpf or None}
        )

        # Update name and cpf if provided and changed
        update_fields = []
        if name and user.name != name:
            user.name = name
            update_fields.append('name')

        if cpf and user.cpf != cpf:
            user.cpf = cpf
            update_fields.append('cpf')

        if update_fields:
            user.save(update_fields=update_fields)

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
