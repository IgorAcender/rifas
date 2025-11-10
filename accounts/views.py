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
from django.contrib.auth.decorators import login_required
from .models import User


def admin_login(request):
    """Login do administrador - apenas email e senha"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Buscar usuário por email
        try:
            user = User.objects.get(email=email, is_staff=True)
            # Verificar senha
            if user.check_password(password):
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Bem-vindo, {user.name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Email ou senha incorretos.')
        except User.DoesNotExist:
            messages.error(request, 'Email ou senha incorretos.')

    return render(request, 'accounts/admin_login.html')


def customer_login(request):
    """Login do cliente - apenas WhatsApp"""
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('customer_area')

    if request.method == 'POST':
        whatsapp = request.POST.get('whatsapp')

        # Normalizar WhatsApp
        whatsapp = ''.join(filter(str.isdigit, whatsapp))

        # Buscar usuario
        try:
            user = User.objects.get(whatsapp=whatsapp, is_staff=False)
            # Login sem senha
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Bem-vindo, {user.name}!')
            return redirect('customer_area')
        except User.DoesNotExist:
            messages.error(request, 'WhatsApp nao encontrado. Voce ja fez alguma compra?')

    return render(request, 'accounts/customer_login.html')


@login_required
def customer_area(request):
    """Area do cliente - ver seus numeros e historico"""
    from raffles.models import RaffleNumber, RaffleOrder

    my_numbers = RaffleNumber.objects.filter(
        user=request.user,
        status__in=['reserved', 'vendido']
    ).select_related('raffle').order_by('-sold_at', '-reserved_at')

    my_orders = RaffleOrder.objects.filter(
        user=request.user
    ).select_related('raffle').order_by('-created_at')

    context = {
        'my_numbers': my_numbers,
        'my_orders': my_orders,
    }
    return render(request, 'accounts/customer_area.html', context)


def logout_view(request):
    """Logout"""
    auth_logout(request)
    messages.success(request, 'Voce saiu do sistema.')
    return redirect('admin_login')
