"""
API views for users app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, UserInteraction
from .serializers import UserSerializer, UserInteractionSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def interactions(self, request, pk=None):
        """Get user's interaction history"""
        user = self.get_object()
        interactions = UserInteraction.objects.filter(user=user).order_by('-created_at')[:50]
        serializer = UserInteractionSerializer(interactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def vip_status(self, request, pk=None):
        """Get user's VIP status and benefits"""
        user = self.get_object()
        return Response({
            'vip_level': user.vip_level,
            'priority_score': user.priority_score,
            'benefits': {
                'priority_queue_access': user.vip_level in ['SILVER', 'GOLD', 'PLATINUM'],
                'early_access': user.vip_level in ['GOLD', 'PLATINUM'],
                'exclusive_products': user.vip_level == 'PLATINUM',
            }
        })


class UserInteractionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserInteraction model
    """
    queryset = UserInteraction.objects.all()
    serializer_class = UserInteractionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter interactions by current user"""
        if self.request.user.is_staff:
            return UserInteraction.objects.all()
        return UserInteraction.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user to current user when creating interaction"""
        serializer.save(user=self.request.user)
