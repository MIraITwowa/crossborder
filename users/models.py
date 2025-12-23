from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with VIP membership levels"""
    
    VIP_LEVELS = [
        ('REGULAR', 'Regular'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
    ]
    
    vip_level = models.CharField(
        max_length=20,
        choices=VIP_LEVELS,
        default='REGULAR',
        help_text='VIP membership level for priority access'
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    preferred_currency = models.CharField(max_length=3, default='USD')
    wallet_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Blockchain wallet address for NFT storage'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.vip_level})"
    
    @property
    def priority_score(self):
        """Get priority score for queue management"""
        from django.conf import settings
        return settings.VIP_PRIORITY_LEVELS.get(self.vip_level, 999)


class UserInteraction(models.Model):
    """Track user interactions with products for AI recommendations"""
    
    INTERACTION_TYPES = [
        ('VIEW', 'View'),
        ('AR_TRY', 'AR Try-on'),
        ('3D_ROTATE', '3D Rotation'),
        ('ZOOM', 'Zoom'),
        ('SAVE', 'Save to Wishlist'),
        ('SHARE', 'Share'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    duration_seconds = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['product', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.product.name}"
