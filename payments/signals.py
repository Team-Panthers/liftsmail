from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from payments.models import UserSubscription, SubscriptionPlan
from users.models import CustomUser

@receiver(post_save, sender=CustomUser)
def create_user_subscription(sender, instance, created, **kwargs):
    if created:
        try:
            # Retrieve or create the free plan
            free_plan = SubscriptionPlan.objects.get(name='Free Plan')
        except SubscriptionPlan.DoesNotExist:
            # Handle case where 'Free Plan' does not exist
            print("Error: 'Free Plan' does not exist. Please create a 'Free Plan' subscription plan.")
            return

        # Calculate the subscription end date (12 months from now)
        subscription_start_date = timezone.now().date()
        subscription_end_date = subscription_start_date + relativedelta(months=1)
        
        try:
            # Create or update the UserSubscription
            UserSubscription.objects.get_or_create(
                user=instance,
                defaults={
                    'plan': free_plan,
                    'subscription_start_date': subscription_start_date,
                    'subscription_end_date': subscription_end_date,
                    'will_renew': True
                }
            )
        except Exception as e:
            # Log or handle any other exceptions that might occur
            print(f"Error creating UserSubscription: {e}")
