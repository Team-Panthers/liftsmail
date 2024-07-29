from django.core.management.base import BaseCommand
from payments.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Create subscription plans if they do not exist'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Free Plan',
                'max_groups': 1,
                'max_emails_per_group': 50,
                'max_email_sessions_per_month': 5,
                'price': 0.00
            },
            {
                'name': 'Plan 1',
                'max_groups': 3,
                'max_emails_per_group': 150,
                'max_email_sessions_per_month': 10,
                'price': 2500.00
            },
            {
                'name': 'Plan 2',
                'max_groups': 7,
                'max_emails_per_group': 500,
                'max_email_sessions_per_month': 20,
                'price': 5000.00
            },
            {
                'name': 'Plan 3',
                'max_groups': 15,
                'max_emails_per_group': 1500,
                'max_email_sessions_per_month': 30,
                'price': 10000.00
            }
        ]

        for plan in plans:
            obj, created = SubscriptionPlan.objects.get_or_create(
                name=plan['name'],
                defaults={
                    'max_groups': plan['max_groups'],
                    'max_emails_per_group': plan['max_emails_per_group'],
                    'max_email_sessions_per_month': plan['max_email_sessions_per_month'],
                    'price': plan['price']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {plan["name"]}.'))
            else:
                self.stdout.write(f'{plan["name"]} already exists.')
