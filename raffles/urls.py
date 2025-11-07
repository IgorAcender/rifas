from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.RaffleViewSet, basename='raffle')
router.register(r'orders', views.RaffleOrderViewSet, basename='order')
router.register(r'referrals', views.ReferralViewSet, basename='referral')

urlpatterns = router.urls
