from django.contrib import admin
from .models import Group, Contact

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')
    search_fields = ('name', 'user__email')
    list_filter = ('created_at', 'updated_at')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'is_subscribed', 'is_valid', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'group__name')
    list_filter = ('is_subscribed', 'is_valid', 'created_at', 'updated_at')
