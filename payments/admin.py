from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_groups', 'max_emails_per_group', 'max_email_sessions_per_month', 'price')
    search_fields = ('name',)
    ordering = ('name',)

class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'email_sessions_used', 'subscription_start_date', 'subscription_end_date', 'will_renew')
    search_fields = ('user__username', 'plan__name')
    list_filter = ('plan', 'will_renew')
    ordering = ('user',)

admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
