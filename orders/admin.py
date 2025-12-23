from django.contrib import admin
from .models import Order, OrderItem, PriorityQueue


class OrderItemInline(admin.TabularInline):
    """Inline for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model"""
    
    list_display = [
        'order_number', 'user', 'status', 'total',
        'currency', 'created_at', 'paid_at'
    ]
    list_filter = ['status', 'created_at', 'currency']
    search_fields = ['order_number', 'user__username', 'tracking_number']
    readonly_fields = ['created_at', 'paid_at', 'shipped_at', 'delivered_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Info', {
            'fields': ('user', 'order_number', 'status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'shipping_fee', 'total', 'currency')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'tracking_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'paid_at', 'shipped_at', 'delivered_at')
        }),
    )


@admin.register(PriorityQueue)
class PriorityQueueAdmin(admin.ModelAdmin):
    """Admin configuration for PriorityQueue model"""
    
    list_display = [
        'user', 'product', 'vip_level', 'priority_score',
        'queue_position', 'status', 'queued_at', 'expires_at'
    ]
    list_filter = ['status', 'vip_level', 'queued_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['queued_at', 'processed_at']
    date_hierarchy = 'queued_at'
    
    fieldsets = (
        ('User & Product', {
            'fields': ('user', 'product')
        }),
        ('Priority', {
            'fields': ('priority_score', 'vip_level', 'queue_position', 'estimated_wait_seconds')
        }),
        ('Status', {
            'fields': ('status', 'queued_at', 'processed_at', 'expires_at')
        }),
        ('Result', {
            'fields': ('order',)
        }),
    )
