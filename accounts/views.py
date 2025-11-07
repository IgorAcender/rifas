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


# Frontend Views
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import User


def login_view(request):
    """Pagina de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        whatsapp = request.POST.get('whatsapp')
        password = request.POST.get('password')

        # Normalizar WhatsApp (apenas digitos)
        whatsapp = ''.join(filter(str.isdigit, whatsapp))

        # Se tem senha, e admin
        if password:
            user = authenticate(request, username=whatsapp, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Bem-vindo, {user.name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'WhatsApp ou senha incorretos.')
        else:
            # Usuario normal - apenas WhatsApp
            try:
                user = User.objects.get(whatsapp=whatsapp)
                # Login sem senha (backend customizado)
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Bem-vindo, {user.name}!')
                return redirect('dashboard')
            except User.DoesNotExist:
                # Criar novo usuario
                user = User.objects.create_user(
                    whatsapp=whatsapp,
                    name=f'Usuario {whatsapp[-4:]}'
                )
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Conta criada! Bem-vindo, {user.name}!')
                return redirect('dashboard')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Logout"""
    auth_logout(request)
    messages.success(request, 'Voce saiu do sistema.')
    return redirect('login')
