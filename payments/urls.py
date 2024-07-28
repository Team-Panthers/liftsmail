from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionPlanListView,
    UpdatePlanAndInitiatePaymentView,
    SubscriptionStatusView,
    SubscriptionPlanViewSet,
    paystack_webhook,
    UnsubscribeView
)
from.import views

router = DefaultRouter()
router.register(r'admin/subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')

urlpatterns = [
    path('', include(router.urls)),
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription_plans'),
    path('initiate-payment/', UpdatePlanAndInitiatePaymentView.as_view(), name='initiate_payment'),
    path('subscription-status/', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('call-back/', views.payment_callback, name='payment_callback'),
    path('webhook/', paystack_webhook, name='paystack_webhook'),
]
