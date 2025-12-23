"""
Serializers for users app
"""
from rest_framework import serializers
from .models import User, UserInteraction


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'vip_level', 'phone_number', 'country', 'preferred_currency',
            'wallet_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserInteractionSerializer(serializers.ModelSerializer):
    """User interaction serializer"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = UserInteraction
        fields = [
            'id', 'user', 'product', 'product_name',
            'interaction_type', 'duration_seconds', 'metadata',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
