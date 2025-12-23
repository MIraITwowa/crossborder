from django.contrib import admin
from .models import RecommendationModel, UserRecommendation, InteractionFeature


@admin.register(RecommendationModel)
class RecommendationModelAdmin(admin.ModelAdmin):
    """Admin configuration for RecommendationModel"""
    
    list_display = ['name', 'version', 'algorithm', 'accuracy', 'is_active', 'trained_at']
    list_filter = ['is_active', 'algorithm', 'trained_at']
    search_fields = ['name', 'version']
    readonly_fields = ['trained_at']


@admin.register(UserRecommendation)
class UserRecommendationAdmin(admin.ModelAdmin):
    """Admin configuration for UserRecommendation"""
    
    list_display = [
        'user', 'product', 'score', 'shown_to_user',
        'clicked', 'purchased', 'created_at', 'expires_at'
    ]
    list_filter = ['shown_to_user', 'clicked', 'purchased', 'created_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(InteractionFeature)
class InteractionFeatureAdmin(admin.ModelAdmin):
    """Admin configuration for InteractionFeature"""
    
    list_display = [
        'user', 'product', 'total_views', 'total_ar_tries',
        'total_3d_interactions', 'engagement_score', 'last_interaction_date'
    ]
    list_filter = ['last_interaction_date']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
