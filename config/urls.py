from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from raffles import views as raffle_views
from accounts import views as account_views

def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'rifas'})

urlpatterns = [
    # Auth URLs
    path('admin-login/', account_views.admin_login, name='admin_login'),
    path('login/', account_views.customer_login, name='customer_login'),
    path('minha-area/', account_views.customer_area, name='customer_area'),
    path('logout/', account_views.logout_view, name='logout'),

    # Public Raffle URLs (sem autenticação)
    path('r/<slug:slug>/', raffle_views.raffle_public_view, name='raffle_public'),

    # Frontend URLs (Admin)
    path('', raffle_views.dashboard, name='dashboard'),
    path('campanhas/', raffle_views.raffle_list, name='raffle_list'),
    path('criar-campanha/', raffle_views.raffle_create, name='raffle_create'),
    path('editar-campanha/<int:pk>/', raffle_views.raffle_edit, name='raffle_edit'),
    path('apoiadores/', raffle_views.supporters, name='supporters'),
    path('afiliados/', raffle_views.affiliates, name='affiliates'),
    path('configuracoes/', raffle_views.settings_view, name='settings'),

    # API URLs
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/raffles/', include('raffles.urls')),
    path('api/payments/', include('payments.urls')),
]
