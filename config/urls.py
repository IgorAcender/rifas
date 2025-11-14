from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import render, redirect
from raffles import views as raffle_views
from raffles.models import SiteConfiguration
from accounts import views as account_views
from notifications import views as notification_views

def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'rifas'})

def home_placeholder(request):
    """Página inicial - redireciona para campanha configurada se houver"""
    try:
        config = SiteConfiguration.objects.first()
        if config and config.home_redirect_raffle:
            return redirect('raffle_public', slug=config.home_redirect_raffle.slug)
    except Exception:
        pass
    
    return render(request, 'home_placeholder.html')

urlpatterns = [
    # Home (raiz)
    path('', home_placeholder, name='home'),
    
    # Auth URLs
    path('admin-login/', account_views.admin_login, name='admin_login'),
    path('login/', account_views.customer_login, name='customer_login'),
    path('minha-area/', account_views.customer_area, name='customer_area'),
    path('logout/', account_views.logout_view, name='logout'),
    path('get-milestone-reward/', account_views.get_milestone_reward, name='get_milestone_reward'),

    # Public Raffle URLs (sem autenticação)
    path('r/<slug:slug>/', raffle_views.raffle_public_view, name='raffle_public'),
    path('r/<slug:slug>/test-payment/', raffle_views.test_payment, name='test_payment'),

    # Frontend URLs (Admin) - todas requerem autenticação
    path('dashboard/', raffle_views.dashboard, name='dashboard'),
    path('campanhas/', raffle_views.raffle_list, name='raffle_list'),
    path('campanha/<int:pk>/', raffle_views.campaign_details, name='campaign_details'),
    path('criar-campanha/', raffle_views.raffle_create, name='raffle_create'),
    path('editar-campanha/<int:pk>/', raffle_views.raffle_edit, name='raffle_edit'),
    path('excluir-campanha/<int:pk>/', raffle_views.raffle_delete, name='raffle_delete'),
    path('apoiadores/', raffle_views.supporters, name='supporters'),
    path('afiliados/', raffle_views.affiliates, name='affiliates'),
    path('configuracoes/', raffle_views.settings_view, name='settings'),
    path('config-site/', raffle_views.site_config_view, name='site_config'),
    path('admin-dashboard/', raffle_views.admin_dashboard, name='admin_dashboard'),
    path('campanha/<int:raffle_id>/configuracoes/', raffle_views.raffle_settings_view, name='raffle_settings'),
    path('sorteador/', raffle_views.raffle_draw, name='raffle_draw'),

    # WhatsApp Manager
    path('whatsapp/', notification_views.whatsapp_manager, name='whatsapp_manager'),
    path('whatsapp/status/', notification_views.get_instance_status, name='whatsapp_status'),
    path('whatsapp/qrcode/', notification_views.get_qrcode, name='whatsapp_qrcode'),
    path('whatsapp/restart/', notification_views.restart_instance, name='whatsapp_restart'),
    path('whatsapp/logout/', notification_views.logout_instance, name='whatsapp_logout'),
    path('whatsapp/test/', notification_views.send_test_message, name='whatsapp_test_message'),
    path('whatsapp/template/save/', notification_views.save_message_template, name='whatsapp_save_template'),

    # API URLs
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/raffles/', include('raffles.urls')),
    path('api/payments/', include('payments.urls')),
]
