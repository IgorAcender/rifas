from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import WhatsAppLoginSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def whatsapp_login(request):
    """
    WhatsApp login endpoint.
    Creates user if doesn't exist, returns JWT tokens.

    POST /api/auth/login/
    {
        "whatsapp": "5511999999999",
        "name": "John Doe"  # optional
    }
    """
    serializer = WhatsAppLoginSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def me(request):
    """
    Get current user info.

    GET /api/auth/me/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
