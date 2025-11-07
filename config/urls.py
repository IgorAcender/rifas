from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from raffles import views as raffle_views

def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'rifas'})

urlpatterns = [
    # Frontend URLs
    path('', raffle_views.dashboard, name='dashboard'),
    path('campanhas/', raffle_views.raffle_list, name='raffle_list'),
    path('criar-campanha/', raffle_views.raffle_create, name='raffle_create'),
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
