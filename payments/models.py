from django.db import models
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
from django.utils import timezone


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    max_groups = models.PositiveIntegerField()
    max_emails_per_group = models.PositiveIntegerField()
    max_email_sessions_per_month = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    email_sessions_used = models.PositiveIntegerField(default=0)
    subscription_start_date = models.DateField(auto_now_add=True)
    subscription_end_date = models.DateField()
    # will_renew = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} - {self.plan.name}'
