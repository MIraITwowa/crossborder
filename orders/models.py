from django.db import models
from django.conf import settings
from decimal import Decimal


class Order(models.Model):
    """Customer orders"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Shipping
    shipping_address = models.JSONField()
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    """Items in an order"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # NFT Certificate (assigned after purchase)
    nft_certificate = models.ForeignKey(
        'blockchain.NFTCertificate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class PriorityQueue(models.Model):
    """VIP priority queue for limited edition releases"""
    
    STATUS_CHOICES = [
        ('QUEUED', 'In Queue'),
        ('PROCESSING', 'Being Processed'),
        ('COMPLETED', 'Completed'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='queue_entries')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='queue_entries')
    
    # Priority calculation
    priority_score = models.IntegerField(help_text='Lower is higher priority')
    vip_level = models.CharField(max_length=20)
    
    # Queue metadata
    queue_position = models.IntegerField(null=True, blank=True)
    estimated_wait_seconds = models.IntegerField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='QUEUED')
    
    # Timestamps
    queued_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(help_text='When this queue entry expires')
    
    # Result
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='queue_entries'
    )
    
    class Meta:
        db_table = 'priority_queue'
        ordering = ['priority_score', 'queued_at']
        indexes = [
            models.Index(fields=['product', 'status', 'priority_score']),
            models.Index(fields=['user', '-queued_at']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"Queue: {self.user.username} - {self.product.name} (Priority: {self.priority_score})"
    
    def save(self, *args, **kwargs):
        # Set priority score based on VIP level
        if not self.priority_score:
            self.priority_score = self.user.priority_score
        if not self.vip_level:
            self.vip_level = self.user.vip_level
        super().save(*args, **kwargs)
