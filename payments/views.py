from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer
from .models import SubscriptionPlan, UserSubscription
from .services import (
    get_all_subscription_plans,
    get_subscription_plan_by_id,
    user_subscription,
    is_user_subscription_active,
    initiate_payment,
    update_user_subscription,
)


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]


class SubscriptionPlanListView(generics.ListAPIView):
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_all_subscription_plans()


class InitiatePaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, plan_id):
        plan = get_subscription_plan_by_id(plan_id)
        if not plan:
            return Response(
                {"detail": "Plan not found."},
                status=status.HTTP_404_NOT_FOUND
                )

        user_subscription, created = user_subscription(request.user)

        if not created and is_user_subscription_active(user_subscription):
            return Response(
                {"detail": "You already have an active subscription."},
                status=status.HTTP_400_BAD_REQUEST
                )

        response_data = initiate_payment(request.user, plan)

        if response_data['status']:
            return Response(
                {"authorization_url": response_data['data']['authorization_url']}
                )
        else:
            return Response(
                {"detail": "Payment initiation failed."},
                status=status.HTTP_400_BAD_REQUEST
                )


@method_decorator(csrf_exempt, name='dispatch')
@api_view(['POST'])
def paystack_webhook(request):
    event = request.data
    if event['event'] == 'charge.success':
        data = event['data']
        email = data['customer']['email']
        plan_id = data['metadata']['plan_id']

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            user = User.objects.get(email=email)
            user_subscription, _ = UserSubscription.objects.get_or_create(user=user)

            update_user_subscription(user_subscription, plan)
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except (SubscriptionPlan.DoesNotExist, User.DoesNotExist):
            return Response(
                {"status": "error", "message": "Plan or User not found"},
                status=status.HTTP_400_BAD_REQUEST
                )
    return Response(
        {"status": "error", "message": "Invalid event"},
        status=status.HTTP_400_BAD_REQUEST
        )


class SubscriptionStatusView(generics.RetrieveAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return user_subscription(self.request.user)[0]


# class UnsubscribeView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user_subscription = user_subscription(request.user)[0]
#         if is_user_subscription_active(user_subscription):
#             deactivate_user_subscription(user_subscription)
#             return Response(
#                 {"detail": "Unsubscribed successfully."},
#                 status=status.HTTP_200_OK
#                 )
#         else:
#             return Response(
#                 {"detail": "No active subscription found."},
#                 status=status.HTTP_400_BAD_REQUEST
#                 )
