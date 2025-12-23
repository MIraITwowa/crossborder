"""
API views for AR experience app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import ARSession, ARModel
from .serializers import ARSessionSerializer, ARModelSerializer
from users.models import UserInteraction
import uuid


class ARSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AR Session management
    """
    queryset = ARSession.objects.all()
    serializer_class = ARSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter sessions by current user"""
        if self.request.user.is_staff:
            return ARSession.objects.all()
        return ARSession.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """Start a new AR session"""
        product_id = request.data.get('product_id')
        device_type = request.data.get('device_type', 'unknown')
        browser = request.data.get('browser', 'unknown')
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = ARSession.objects.create(
            user=request.user,
            product_id=product_id,
            session_id=str(uuid.uuid4()),
            device_type=device_type,
            browser=browser
        )
        
        # Create user interaction
        UserInteraction.objects.create(
            user=request.user,
            product_id=product_id,
            interaction_type='AR_TRY',
            duration_seconds=0
        )
        
        serializer = ARSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """End an AR session"""
        session = self.get_object()
        
        if session.ended_at:
            return Response(
                {'error': 'Session already ended'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.ended_at = timezone.now()
        session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
        
        # Update with any additional data
        if 'screenshots_taken' in request.data:
            session.screenshots_taken = request.data['screenshots_taken']
        if 'rotation_count' in request.data:
            session.rotation_count = request.data['rotation_count']
        if 'zoom_count' in request.data:
            session.zoom_count = request.data['zoom_count']
        if 'ar_data' in request.data:
            session.ar_data = request.data['ar_data']
        
        session.save()
        
        serializer = ARSessionSerializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_metrics(self, request, pk=None):
        """Update session metrics during an active session"""
        session = self.get_object()
        
        if session.ended_at:
            return Response(
                {'error': 'Cannot update ended session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update metrics
        if 'screenshots_taken' in request.data:
            session.screenshots_taken = request.data['screenshots_taken']
        if 'rotation_count' in request.data:
            session.rotation_count = request.data['rotation_count']
        if 'zoom_count' in request.data:
            session.zoom_count = request.data['zoom_count']
        
        session.save()
        
        serializer = ARSessionSerializer(session)
        return Response(serializer.data)


class ARModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AR Model access (read-only for clients)
    """
    queryset = ARModel.objects.all()
    serializer_class = ARModelSerializer
    
    def get_queryset(self):
        """Filter by product if provided"""
        queryset = ARModel.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
