"""
API views for products app
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage, PriceHistory
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductImageSerializer, PriceHistorySerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category model
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model
    """
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'product_type', 'is_limited_edition', 'has_ar_support']
    search_fields = ['name', 'description', 'brand']
    ordering_fields = ['current_price', 'created_at', 'name']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer
    
    @action(detail=True, methods=['get'])
    def price_history(self, request, slug=None):
        """Get price history for a product"""
        product = self.get_object()
        history = PriceHistory.objects.filter(product=product).order_by('-created_at')[:20]
        serializer = PriceHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def ar_model(self, request, slug=None):
        """Get AR model information"""
        product = self.get_object()
        if not product.has_ar_support:
            return Response(
                {'error': 'This product does not have AR support'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'has_ar_support': product.has_ar_support,
            'model_file': request.build_absolute_uri(product.model_3d_file.url) if product.model_3d_file else None,
            'thumbnail': request.build_absolute_uri(product.model_thumbnail.url) if product.model_thumbnail else None,
        })
    
    @action(detail=True, methods=['get'])
    def nft_info(self, request, slug=None):
        """Get NFT certificate information"""
        product = self.get_object()
        if not product.has_nft_certificate:
            return Response(
                {'error': 'This product does not have NFT certificate'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'has_nft_certificate': product.has_nft_certificate,
            'contract_address': product.nft_contract_address,
            'token_id': product.nft_token_id,
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = Product.objects.filter(is_active=True, is_featured=True)[:10]
        serializer = ProductListSerializer(featured_products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def limited_edition(self, request):
        """Get limited edition products"""
        limited = Product.objects.filter(
            is_active=True,
            is_limited_edition=True,
            stock_quantity__gt=0
        ).order_by('stock_quantity')[:10]
        serializer = ProductListSerializer(limited, many=True, context={'request': request})
        return Response(serializer.data)
