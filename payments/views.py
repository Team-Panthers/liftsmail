from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer
from .models import SubscriptionPlan, UserSubscription
from .services import (
    get_all_subscription_plans,
    get_subscription_plan_by_id,
    user_subscription,
    is_user_subscription_active,
    initiate_payment,
    verify_payment,
    update_user_subscription,
    deactivate_user_subscription,
    handle_subscription_deactivation    
)
from .response_utils import success, created, bad_request, not_found, forbidden, server_error
from django.contrib.auth import get_user_model

User = get_user_model()


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]


class SubscriptionPlanListView(generics.ListAPIView):
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_all_subscription_plans()


class SubscriptionStatusView(generics.RetrieveAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return user_subscription(self.request.user)


class UpdatePlanAndInitiatePaymentView(generics.GenericAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        plan_id = request.data.get('plan')
        current_subscription = UserSubscription.objects.get(user=user)
        
        plan = get_subscription_plan_by_id(plan_id) 
        if not plan:
            return not_found("Plan not found.")

        if plan == current_subscription.plan and is_user_subscription_active(current_subscription):
            return bad_request("You already have an active subscription.")

        response_data = initiate_payment(request, user, plan)

        if response_data['status']:
            return success(data={"authorization_url": response_data['data']['authorization_url']})
        else:
            return bad_request("Payment initiation failed")


@api_view(['GET'])
def payment_callback(request):
    reference = request.GET.get('reference')
    trxref = request.GET.get('trxref')
    
    if not reference:
        return bad_request("Reference not found in the request.")

    if reference == trxref:
        data = verify_payment(reference)
        
        if data['status'] == 'success':
            customer_email = data['customer']['email']
            amount_paid = data['amount'] / 100  # Convert kobo to Naira
            plan_id = data['metadata']['plan_id']  # Extract plan ID from metadata
            paid_at = data['paidAt']
            status = data['status']
            
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
                user = User.objects.get(email=customer_email)
                user_subscription, _ = UserSubscription.objects.get_or_create(user=user)

                # Update the user's subscription
                update_user_subscription(user_subscription, plan)
                
                response_message = (
                    f"Payment successful! <br>"
                    f"Customer Email: {customer_email} <br>"
                    f"Amount Paid: {amount_paid} NGN <br>"
                    f"Subscription Plan: {plan} <br>"
                    f"Paid At: {paid_at} <br>"
                    f"Status: {status}"
                )
                
                return HttpResponse(response_message)
            except (SubscriptionPlan.DoesNotExist, User.DoesNotExist):
                return bad_request("Plan or User not found.")
        else:
            return bad_request("Payment verification failed.")
    else:
        return bad_request("Reference and trxref do not match.")



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
            return success()
        except (SubscriptionPlan.DoesNotExist, User.DoesNotExist):
            return bad_request("Plan or User not found")
    return bad_request("Invalid event")


class UnsubscribeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return bad_request("Email is required.")

        if email != request.user.email:
            return forbidden("You can only unsubscribe yourself.")

        try:
            user_subscription_instance = user_subscription(request.user)[0]
            free_plan = SubscriptionPlan.objects.get(name='Free Plan')
            
            if user_subscription_instance.plan == free_plan:
                return success("You are already on the Free Plan.")
            
            if not user_subscription_instance.will_renew:
                return success(
                    f"Subscription has already been deactivated. It will revert to the free plan after {user_subscription_instance.subscription_end_date}."
                )
            
            deactivate_user_subscription(user_subscription_instance)
            
            today = timezone.now().date()
            if is_user_subscription_active(user_subscription_instance) and today <= user_subscription_instance.subscription_end_date:
                return success(
                    f"Unsubscribed successfully. Your subscription will be deactivated after {user_subscription_instance.subscription_end_date}."
                )
            else:
                handle_subscription_deactivation(user_subscription_instance)
                
                return success("Subscription ended. Switched to the free plan.")
        
        except ObjectDoesNotExist:
            return not_found("Subscription record not found.")
        
        except Exception as e:
            return server_error(f"An error occurred: {str(e)}")
