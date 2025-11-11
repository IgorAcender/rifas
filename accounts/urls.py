from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.whatsapp_login, name='whatsapp_login'),
    path('check-whatsapp/', views.check_whatsapp, name='check_whatsapp'),
    path('me/', views.me, name='me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
