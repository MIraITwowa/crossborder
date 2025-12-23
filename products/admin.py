from django.contrib import admin
from .models import Category, Product, ProductImage, PriceHistory


class ProductImageInline(admin.TabularInline):
    """Inline for product images"""
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model"""
    
    list_display = ['name', 'slug', 'parent', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model"""
    
    list_display = [
        'name', 'brand', 'category', 'current_price', 'stock_quantity',
        'has_ar_support', 'has_nft_certificate', 'is_limited_edition', 'is_active'
    ]
    list_filter = [
        'category', 'brand', 'product_type', 'has_ar_support',
        'has_nft_certificate', 'is_limited_edition', 'is_active', 'is_featured'
    ]
    search_fields = ['name', 'brand', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'product_type', 'brand')
        }),
        ('Pricing', {
            'fields': ('base_price', 'current_price', 'currency')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'is_limited_edition', 'max_quantity_per_order')
        }),
        ('3D/AR', {
            'fields': ('has_3d_model', 'has_ar_support', 'model_3d_file', 'model_thumbnail')
        }),
        ('Blockchain', {
            'fields': ('has_nft_certificate', 'nft_contract_address', 'nft_token_id')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'created_at', 'updated_at')
        }),
    )


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for PriceHistory model"""
    
    list_display = ['product', 'old_price', 'new_price', 'reason', 'demand_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
