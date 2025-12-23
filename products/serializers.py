"""
Serializers for products app
"""
from rest_framework import serializers
from .models import Category, Product, ProductImage, PriceHistory


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """Product image serializer"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']
        read_only_fields = ['id']


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified product serializer for list views"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand', 'category_name',
            'current_price', 'currency', 'primary_image',
            'has_3d_model', 'has_ar_support', 'has_nft_certificate',
            'is_limited_edition', 'is_in_stock', 'is_featured'
        ]
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer"""
    
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    demand_score = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'product_type',
            'brand', 'base_price', 'current_price', 'currency',
            'stock_quantity', 'is_limited_edition', 'max_quantity_per_order',
            'has_3d_model', 'has_ar_support', 'model_3d_file', 'model_thumbnail',
            'has_nft_certificate', 'nft_contract_address', 'nft_token_id',
            'is_active', 'is_featured', 'is_in_stock', 'demand_score',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'demand_score']


class PriceHistorySerializer(serializers.ModelSerializer):
    """Price history serializer"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = PriceHistory
        fields = [
            'id', 'product', 'product_name', 'old_price', 'new_price',
            'reason', 'demand_score', 'stock_level', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
