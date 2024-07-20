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
    user_subscription.will_renew = False
    user_subscription.save()
