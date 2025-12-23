from django.db import models
from django.conf import settings


class ARSession(models.Model):
    """Track AR try-on sessions"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ar_sessions')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='ar_sessions')
    
    # Session data
    session_id = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    
    # Interaction metrics
    duration_seconds = models.IntegerField(default=0)
    screenshots_taken = models.IntegerField(default=0)
    rotation_count = models.IntegerField(default=0)
    zoom_count = models.IntegerField(default=0)
    
    # AR-specific data
    ar_data = models.JSONField(default=dict, help_text='AR session metadata and measurements')
    
    # Session status
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ar_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['product', '-started_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"AR Session: {self.user.username} - {self.product.name}"


class ARModel(models.Model):
    """3D/AR Model assets for products"""
    
    FORMAT_CHOICES = [
        ('GLB', 'GLB Format'),
        ('GLTF', 'GLTF Format'),
        ('USDZ', 'USDZ Format (iOS)'),
    ]
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='ar_models')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file = models.FileField(upload_to='ar_models/')
    file_size_mb = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Model properties
    polygon_count = models.IntegerField(null=True, blank=True)
    has_textures = models.BooleanField(default=True)
    has_animations = models.BooleanField(default=False)
    
    # Optimization
    is_optimized = models.BooleanField(default=False)
    optimization_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low Quality'),
        ('MEDIUM', 'Medium Quality'),
        ('HIGH', 'High Quality'),
    ], default='MEDIUM')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ar_models'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'format']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.format}"
