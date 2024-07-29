import requests
from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import SubscriptionPlan, UserSubscription
from django.core.exceptions import ValidationError
from django.http import Http404
from django.contrib.sites.shortcuts import get_current_site
import uuid

def get_all_subscription_plans():
    return SubscriptionPlan.objects.all()

def get_subscription_plan_by_id(plan_id):
    try:
        return SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return None

def user_subscription(user):
    try:
        # Attempt to get the UserSubscription for the user
        subscription = UserSubscription.objects.get(user=user)
        return subscription
    except UserSubscription.DoesNotExist:
        # Handle the case where no subscription exists for the user
        raise Http404("User is currently not subscribed to any subscription.")
    except ValidationError as e:
        # Handle validation errors, such as missing required fields
        print(f"Validation Error: {e}")
        raise e
    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred: {e}")
        raise e

def is_user_subscription_active(user_subscription):
    return user_subscription.subscription_end_date >= timezone.now().date()

def initiate_payment(request,user, plan):
    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_KEY}',
        'Content-Type': 'application/json',
    }
    plan_id = plan.id
    domain = get_current_site(request).domain
    data = {
        'email': user.email,
        "currency" : "NGN",
        'amount': int(plan.price * 100),  # amount in kobo
        'callback_url' : f"http://{domain}/payments/call-back/",
        'metadata': {
            'plan_id': plan_id
        }
    }
    print('sending the data...')
    response = requests.post(paystack_url,headers=headers,json=data)
    response_data = response.json()

    return response_data


def verify_payment(reference):
    """
    Verify payment with Paystack using the provided reference.
    """
    verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.get(verify_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        verify_data = response.json()
        
        if verify_data.get('status') and verify_data.get('data').get('status') == 'success':
            return verify_data['data']
        else:
            return None
    except requests.RequestException as e:
        print(f"Error verifying payment: {e}")
        return None

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
    # 1. Exist and marked as not renewing (will_renew=False).
    # 2. Have an end date that is today or has already passed (subscription_end_date__lte=today).
    subscriptions = UserSubscription.objects.filter(
        plan__isnull=False,
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
