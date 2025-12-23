from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Category(models.Model):
    """Product category"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Luxury product with 3D/AR support"""
    
    PRODUCT_TYPES = [
        ('WATCH', 'Watch'),
        ('JEWELRY', 'Jewelry'),
        ('BAG', 'Bag'),
        ('SHOES', 'Shoes'),
        ('CLOTHING', 'Clothing'),
        ('ACCESSORIES', 'Accessories'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPES)
    brand = models.CharField(max_length=100)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='USD')
    
    # Inventory
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_limited_edition = models.BooleanField(default=False)
    max_quantity_per_order = models.IntegerField(default=1)
    
    # 3D/AR Support
    has_3d_model = models.BooleanField(default=False)
    has_ar_support = models.BooleanField(default=False)
    model_3d_file = models.FileField(upload_to='3d_models/', null=True, blank=True)
    model_thumbnail = models.ImageField(upload_to='product_thumbnails/', null=True, blank=True)
    
    # Blockchain/NFT
    has_nft_certificate = models.BooleanField(default=False)
    nft_contract_address = models.CharField(max_length=255, blank=True, null=True)
    nft_token_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['brand']),
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['is_limited_edition', 'stock_quantity']),
        ]
    
    def __str__(self):
        return f"{self.brand} - {self.name}"
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def demand_score(self):
        """Calculate demand score for dynamic pricing"""
        from users.models import UserInteraction
        views = UserInteraction.objects.filter(product=self, interaction_type='VIEW').count()
        ar_tries = UserInteraction.objects.filter(product=self, interaction_type='AR_TRY').count()
        return views + (ar_tries * 3)  # Weight AR tries more heavily


class ProductImage(models.Model):
    """Product images"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class PriceHistory(models.Model):
    """Track price changes for dynamic pricing"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    demand_score = models.IntegerField(default=0)
    stock_level = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'price_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.product.name}: {self.old_price} -> {self.new_price}"
