from django.urls import path
from . import views

urlpatterns = [
    path('mercadopago/create/', views.create_mercadopago_payment, name='mercadopago_create'),
    path('mercadopago/webhook/', views.mercadopago_webhook, name='mercadopago_webhook'),
    path('status/<int:order_id>/', views.get_order_status, name='get_order_status'),
]
