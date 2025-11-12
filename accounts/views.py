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


@api_view(['POST'])
@permission_classes([AllowAny])
def check_whatsapp(request):
    """
    Check if WhatsApp number is already registered.
    Returns user data if exists, null otherwise.

    POST /api/auth/check-whatsapp/
    {
        "whatsapp": "37900000000"
    }
    """
    whatsapp = request.data.get('whatsapp', '').strip()

    if not whatsapp:
        return Response(
            {'error': 'WhatsApp number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Normalize WhatsApp (remove formatting)
    whatsapp_clean = ''.join(filter(str.isdigit, whatsapp))

    try:
        user = User.objects.get(whatsapp=whatsapp_clean, is_staff=False)
        return Response({
            'exists': True,
            'user': {
                'name': user.name,
                'cpf': user.cpf or '',
                'whatsapp': whatsapp_clean
            }
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'exists': False,
            'user': None
        }, status=status.HTTP_200_OK)


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
    from raffles.models import RaffleNumber, RaffleOrder, Referral

    my_numbers = RaffleNumber.objects.filter(
        user=request.user,
        status__in=['reserved', 'vendido']
    ).select_related('raffle').order_by('-sold_at', '-reserved_at')

    my_orders = RaffleOrder.objects.filter(
        user=request.user
    ).select_related('raffle').order_by('-created_at')

    # Group orders by campaign with totals
    from collections import defaultdict
    from django.db.models import Sum

    orders_by_raffle = defaultdict(list)
    for order in my_orders:
        if order.status == RaffleOrder.Status.PAID:
            orders_by_raffle[order.raffle].append(order)

    # Create grouped campaigns structure
    my_campaigns_grouped = []
    for raffle, orders in orders_by_raffle.items():
        # Contar números comprados (source='purchase')
        purchased_count = RaffleNumber.objects.filter(
            raffle=raffle,
            order__user=request.user,
            order__status=RaffleOrder.Status.PAID,
            source='purchase'
        ).count()
        
        # Contar números bônus (todos os outros sources)
        bonus_count = RaffleNumber.objects.filter(
            raffle=raffle,
            order__user=request.user,
            order__status=RaffleOrder.Status.PAID
        ).exclude(source='purchase').count()
        
        # Total de números (comprados + bônus)
        total_numbers_count = purchased_count + bonus_count
        
        total_amount = sum(order.amount for order in orders)

        my_campaigns_grouped.append({
            'raffle': raffle,
            'orders': orders,
            'purchased_count': purchased_count,  # Números comprados
            'bonus_count': bonus_count,  # Números bônus
            'total_quantity': total_numbers_count,  # Total
            'total_amount': total_amount  # Investido
        })

    # Get successful referrals grouped by campaign
    all_referrals = Referral.objects.filter(
        inviter=request.user,
        status=Referral.Status.REDEEMED
    ).select_related('invitee', 'raffle').order_by('raffle', '-redeemed_at')

    # Group referrals by raffle
    referrals_by_raffle = defaultdict(list)
    for referral in all_referrals:
        referrals_by_raffle[referral.raffle].append(referral)

    # Convert to list of dicts for template
    my_referrals_grouped = []
    for raffle, referrals in referrals_by_raffle.items():
        # Count bonus numbers for this specific raffle
        bonus_count = RaffleNumber.objects.filter(
            user=request.user,
            raffle=raffle,
            source=RaffleNumber.Source.REFERRAL_INVITER
        ).count()

        my_referrals_grouped.append({
            'raffle': raffle,
            'referrals': referrals,
            'count': len(referrals),
            'bonus_numbers': bonus_count
        })

    # Count total bonus numbers earned from all referrals
    bonus_numbers_count = RaffleNumber.objects.filter(
        user=request.user,
        source=RaffleNumber.Source.REFERRAL_INVITER
    ).count()

    # Get user's referral codes with ticket counts per campaign
    # Get all referral codes for this user
    all_referral_codes = Referral.objects.filter(
        inviter=request.user
    ).select_related('raffle')

    # For each referral, calculate total tickets bought in that specific raffle
    my_referral_codes = []
    for referral in all_referral_codes:
        total_tickets = RaffleOrder.objects.filter(
            user=request.user,
            raffle=referral.raffle,
            status=RaffleOrder.Status.PAID
        ).aggregate(total=Sum('quantity'))['total'] or 0

        # Only include if user bought 10+ tickets in THIS specific raffle
        if total_tickets >= 10:
            # Add total_tickets as an attribute for display
            referral.total_tickets = total_tickets
            my_referral_codes.append(referral)

    context = {
        'my_numbers': my_numbers,
        'my_orders': my_orders,
        'my_campaigns_grouped': my_campaigns_grouped,
        'my_referrals_grouped': my_referrals_grouped,
        'bonus_numbers_count': bonus_numbers_count,
        'my_referral_codes': my_referral_codes,
    }
    return render(request, 'accounts/customer_area.html', context)


def logout_view(request):
    """Logout"""
    auth_logout(request)
    messages.success(request, 'Voce saiu do sistema.')
    return redirect('admin_login')
