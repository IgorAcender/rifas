from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'rifas'})

urlpatterns = [
    path('', health_check, name='health'),
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/raffles/', include('raffles.urls')),
    path('api/payments/', include('payments.urls')),
]
