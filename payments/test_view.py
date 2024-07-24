from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from rest_framework import status
from .models import SubscriptionPlan, UserSubscription

User = get_user_model()

class UserSubscriptionTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.create_subscription_plans()
        cls.create_users()

    @classmethod
    def create_users(cls):
        cls.users = []
        for i in range(3):  # Create 3 users for testing
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                first_name=f'First{i}',
                last_name=f'Last{i}',
                password='password123'
            )
            cls.users.append(user)
            
            # Ensure no duplicate subscriptions for the same user
            plan = cls.subscription_plans[0]  # Assign the first plan
            if not UserSubscription.objects.filter(user=user).exists():
                UserSubscription.objects.create(
                    user=user,
                    plan=plan,
                    subscription_end_date=timezone.now().date() + relativedelta(months=1)
                )

    @classmethod
    def create_subscription_plans(cls):
        cls.subscription_plans = [
            SubscriptionPlan.objects.create(
                name='Basic Plan',
                max_groups=10,
                max_emails_per_group=100,
                max_email_sessions_per_month=1000,
                price=9.99
            ),
            SubscriptionPlan.objects.create(
                name='Premium Plan',
                max_groups=50,
                max_emails_per_group=500,
                max_email_sessions_per_month=5000,
                price=29.99
            ),
            SubscriptionPlan.objects.create(
                name='Free Plan',
                max_groups=1,
                max_emails_per_group=10,
                max_email_sessions_per_month=100,
                price=0.00
            )
        ]

    def setUp(self):
        self.client = self.client  # APIClient is used by default in APITestCase
        self.authenticated_user = self.users[0]
        self.client.force_authenticate(user=self.authenticated_user)  # Authenticate the client

    def test_subscription_plan_list(self):
        url = reverse('subscription_plans')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)  # Should include all 3 plans


    def test_subscription_status(self):
        url = reverse('subscription_status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data.get('user'), self.authenticated_user.id)  # Use get() to avoid KeyError




    def test_unsubscribe(self):
        url = reverse('unsubscribe')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('detail', response_data)
        self.assertFalse(UserSubscription.objects.get(user=self.authenticated_user).will_renew)

   
    def test_unsubscribe_already_deactivated(self):
        # Manually deactivate the subscription
        subscription = UserSubscription.objects.get(user=self.authenticated_user)
        subscription.will_renew = False
        subscription.save()

        url = reverse('unsubscribe')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('Subscription has already been deactivated', response_data.get('detail'))

    def test_unsubscribe_subscription_ended(self):
        # Set subscription end date to past
        subscription = UserSubscription.objects.get(user=self.authenticated_user)
        subscription.subscription_end_date = timezone.now().date() - relativedelta(days=1)
        subscription.save()

        url = reverse('unsubscribe')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('Switched to the free plan', response_data.get('detail'))
