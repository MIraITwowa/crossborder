"""
Serializers for AR experience app
"""
from rest_framework import serializers
from .models import ARSession, ARModel


class ARSessionSerializer(serializers.ModelSerializer):
    """AR session serializer"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ARSession
        fields = [
            'id', 'user', 'user_username', 'product', 'product_name',
            'session_id', 'device_type', 'browser',
            'duration_seconds', 'screenshots_taken', 'rotation_count', 'zoom_count',
            'ar_data', 'started_at', 'ended_at'
        ]
        read_only_fields = ['id', 'started_at']


class ARModelSerializer(serializers.ModelSerializer):
    """AR model serializer"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ARModel
        fields = [
            'id', 'product', 'product_name', 'format', 'file', 'file_url',
            'file_size_mb', 'polygon_count', 'has_textures', 'has_animations',
            'is_optimized', 'optimization_level', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None
