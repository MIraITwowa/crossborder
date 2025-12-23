from django.contrib import admin
from .models import ARSession, ARModel


@admin.register(ARSession)
class ARSessionAdmin(admin.ModelAdmin):
    """Admin configuration for ARSession model"""
    
    list_display = [
        'session_id', 'user', 'product', 'duration_seconds',
        'device_type', 'started_at', 'ended_at'
    ]
    list_filter = ['device_type', 'browser', 'started_at']
    search_fields = ['session_id', 'user__username', 'product__name']
    readonly_fields = ['started_at', 'ended_at']
    date_hierarchy = 'started_at'


@admin.register(ARModel)
class ARModelAdmin(admin.ModelAdmin):
    """Admin configuration for ARModel model"""
    
    list_display = [
        'product', 'format', 'file_size_mb', 'optimization_level',
        'has_textures', 'has_animations', 'is_optimized'
    ]
    list_filter = ['format', 'optimization_level', 'is_optimized', 'has_textures', 'has_animations']
    search_fields = ['product__name']
    readonly_fields = ['created_at', 'updated_at']
