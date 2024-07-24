from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionPlanListView,
    InitiatePaymentView,
    SubscriptionStatusView,
    SubscriptionPlanViewSet,
    paystack_webhook,
    UnsubscribeView
)

router = DefaultRouter()
router.register(r'admin/subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')

urlpatterns = [
    path('', include(router.urls)),
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription_plans'),
    path('initiate-payment/<int:plan_id>/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('subscription-status/', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('webhook/', paystack_webhook, name='paystack_webhook'),
]
