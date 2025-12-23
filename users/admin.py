from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserInteraction


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model"""
    
    list_display = ['username', 'email', 'vip_level', 'country', 'created_at']
    list_filter = ['vip_level', 'is_staff', 'is_active', 'country']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('VIP & Profile', {
            'fields': ('vip_level', 'phone_number', 'country', 'preferred_currency', 'wallet_address')
        }),
    )


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    """Admin configuration for UserInteraction model"""
    
    list_display = ['user', 'product', 'interaction_type', 'duration_seconds', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
