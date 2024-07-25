import requests
from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import SubscriptionPlan, UserSubscription

def get_all_subscription_plans():
    return SubscriptionPlan.objects.all()

def get_subscription_plan_by_id(plan_id):
    try:
        return SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return None

def user_subscription(user):
    return UserSubscription.objects.get_or_create(user=user)

def is_user_subscription_active(user_subscription):
    return user_subscription.subscription_end_date >= timezone.now().date()

def initiate_payment(user, plan):
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'email': user.email,
        'amount': int(plan.price * 100),  # amount in kobo
        'metadata': {
            'plan_id': plan.id
        }
    }
    response = requests.post(
        'https://api.paystack.co/transaction/initialize',
        headers=headers, 
        json=data
        )
    response_data = response.json()

    return response_data

def update_user_subscription(user_subscription, plan):
    user_subscription.plan = plan
    user_subscription.subscription_end_date = (
        timezone.now().date() + relativedelta(months=1)
    )
    user_subscription.save()

def deactivate_user_subscription(user_subscription):
    # Deactivate now but do not switch plan until end date
    user_subscription.will_renew = False
    user_subscription.save()

def transition_to_free_plan(user_subscription):
    free_plan = SubscriptionPlan.objects.get(name='Free Plan')
    user_subscription.plan = free_plan
    # Assign 1 month for the free plan
    user_subscription.subscription_end_date = timezone.now().date() + relativedelta(months=1)
    user_subscription.save()

def handle_subscription_deactivation(user_subscription):
    if not is_user_subscription_active(user_subscription):
        # If subscription has ended, transition to free plan
        transition_to_free_plan(user_subscription)



def check_and_update_subscriptions():
    # Get today's date
    today = timezone.now().date()
    
    # Query for subscriptions that:
    # 1. Are marked as not renewing (will_renew=False).
    # 2. Have an end date that is today or has already passed (subscription_end_date__lte=today).
    subscriptions = UserSubscription.objects.filter(
        will_renew=False,
        subscription_end_date__lte=today
    )

    # Retrieve the Free Plan object from the database
    # This assumes there is a SubscriptionPlan object with the name 'Free Plan'
    free_plan = SubscriptionPlan.objects.get(name='Free Plan')

    for subscription in subscriptions:
        # Update the user subscription to the Free Plan
        subscription.plan = free_plan
        
        # Set a new subscription end date to 1 month from today
        subscription.subscription_end_date = today + relativedelta(months=1)
        
        # Mark the subscription as renewing (will_renew=True) since it's now on the Free Plan
        subscription.will_renew = True
        
        # Save the updated subscription details to the database
        subscription.save()
