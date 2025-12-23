from django.db import models
from django.conf import settings


class RecommendationModel(models.Model):
    """Store trained recommendation model metadata"""
    
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    algorithm = models.CharField(max_length=50, help_text='e.g., collaborative_filtering, content_based')
    
    # Model parameters
    parameters = models.JSONField(default=dict)
    
    # Performance metrics
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    precision = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    recall = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Model file
    model_file_path = models.CharField(max_length=255, blank=True, null=True)
    
    is_active = models.BooleanField(default=False)
    trained_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendation_models'
        ordering = ['-trained_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class UserRecommendation(models.Model):
    """Store personalized recommendations for users"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    model = models.ForeignKey(RecommendationModel, on_delete=models.SET_NULL, null=True)
    
    # Recommendation score
    score = models.DecimalField(max_digits=5, decimal_places=4, help_text='Recommendation confidence score')
    
    # Factors
    reason = models.CharField(max_length=255, blank=True, help_text='Why this was recommended')
    based_on_interactions = models.JSONField(default=list, help_text='List of interaction IDs used')
    
    # Status
    shown_to_user = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text='When this recommendation expires')
    
    class Meta:
        db_table = 'user_recommendations'
        ordering = ['-score', '-created_at']
        unique_together = [['user', 'product', 'model']]
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['user', 'shown_to_user']),
        ]
    
    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.product.name} (score: {self.score})"


class InteractionFeature(models.Model):
    """Extracted features from user interactions for ML"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interaction_features')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    
    # Aggregated features
    total_views = models.IntegerField(default=0)
    total_ar_tries = models.IntegerField(default=0)
    total_3d_interactions = models.IntegerField(default=0)
    avg_session_duration = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_interaction_date = models.DateTimeField()
    
    # Computed features
    engagement_score = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'interaction_features'
        unique_together = [['user', 'product']]
        indexes = [
            models.Index(fields=['user', '-engagement_score']),
        ]
    
    def __str__(self):
        return f"Features: {self.user.username} - {self.product.name}"
