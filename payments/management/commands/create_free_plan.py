from django.core.management.base import BaseCommand
from payments.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Create a Free Plan if it does not exist'

    def handle(self, *args, **kwargs):
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Free Plan',
            defaults={
                'max_groups': 1,
                'max_emails_per_group': 50,
                'max_email_sessions_per_month': 5,
                'price': 0.00
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Free Plan.'))
        else:
            self.stdout.write('Free Plan already exists.')
