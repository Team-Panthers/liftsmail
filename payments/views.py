from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
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
    deactivate_user_subscription,
    handle_subscription_deactivation
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



class UnsubscribeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {"detail": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if email != request.user.email:
            return Response(
                {"detail": "You can only unsubscribe yourself."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Retrieve or create the user subscription instance
            user_subscription_instance = user_subscription(request.user)[0]
            
            # Retrieve the Free Plan object from the database
            free_plan = SubscriptionPlan.objects.get(name='Free Plan')
            
            # Check if the user is already on the Free Plan
            if user_subscription_instance.plan == free_plan:
                return Response(
                    {"detail": "You are already on the Free Plan."},
                    status=status.HTTP_200_OK
                )
            
            # Check if the subscription is already deactivated
            if not user_subscription_instance.will_renew:
                return Response(
                    {
                        "detail": f"Subscription has already been deactivated. It will revert to the free plan after {user_subscription_instance.subscription_end_date}."
                    },
                    status=status.HTTP_200_OK
                )
            
            # Deactivate the subscription
            deactivate_user_subscription(user_subscription_instance)
            
            # Check if subscription is still active and today's date is not past the end date
            today = timezone.now().date()
            if is_user_subscription_active(user_subscription_instance) and today <= user_subscription_instance.subscription_end_date:
                return Response(
                    {
                        "detail": f"Unsubscribed successfully. Your subscription will be deactivated after {user_subscription_instance.subscription_end_date}."
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Handle transition to free plan
                handle_subscription_deactivation(user_subscription_instance)
                
                return Response(
                    {
                        "detail": "Subscription ended. Switched to the free plan."
                    },
                    status=status.HTTP_200_OK
                )
        
        except ObjectDoesNotExist:
            # Handle case where the user subscription does not exist
            return Response(
                {"detail": "Subscription record not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            # Handle any other exceptions
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

