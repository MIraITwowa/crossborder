"""
Celery tasks for recommendations
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_user_recommendations(user_id):
    """
    Generate personalized recommendations for a user based on their interactions
    """
    from recommendations.models import UserRecommendation, InteractionFeature, RecommendationModel
    from users.models import User, UserInteraction
    from products.models import Product
    from django.db.models import Count, Avg, Q
    
    try:
        user = User.objects.get(id=user_id)
        
        # Check if user has enough interactions
        from django.conf import settings
        min_interactions = settings.MIN_INTERACTIONS_FOR_RECOMMENDATION
        
        interaction_count = UserInteraction.objects.filter(user=user).count()
        if interaction_count < min_interactions:
            logger.info(f"User {user_id} has insufficient interactions ({interaction_count})")
            return {'status': 'skipped', 'reason': 'insufficient_interactions'}
        
        # Get active recommendation model
        model = RecommendationModel.objects.filter(is_active=True).first()
        if not model:
            logger.warning("No active recommendation model found")
            return {'status': 'error', 'reason': 'no_active_model'}
        
        # Simple collaborative filtering approach
        # Find products user interacted with
        user_products = UserInteraction.objects.filter(
            user=user
        ).values_list('product_id', flat=True).distinct()
        
        # Find similar users (users who interacted with same products)
        similar_users = User.objects.filter(
            interactions__product_id__in=user_products
        ).exclude(id=user_id).annotate(
            common_products=Count('interactions__product')
        ).filter(common_products__gte=2)[:10]
        
        # Get products similar users liked but current user hasn't seen
        recommended_products = Product.objects.filter(
            userinteraction__user__in=similar_users,
            is_active=True
        ).exclude(
            id__in=user_products
        ).annotate(
            score=Count('userinteraction')
        ).order_by('-score')[:20]
        
        # Create recommendations
        expires_at = timezone.now() + timedelta(days=7)
        recommendations_created = 0
        
        for product in recommended_products:
            score = min(product.score / 10.0, 1.0)  # Normalize score
            
            UserRecommendation.objects.update_or_create(
                user=user,
                product=product,
                model=model,
                defaults={
                    'score': score,
                    'reason': 'Based on similar users',
                    'expires_at': expires_at,
                }
            )
            recommendations_created += 1
        
        logger.info(f"Generated {recommendations_created} recommendations for user {user_id}")
        return {
            'status': 'success',
            'recommendations_count': recommendations_created
        }
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'status': 'error', 'reason': 'user_not_found'}
    except Exception as exc:
        logger.error(f"Error generating recommendations for user {user_id}: {str(exc)}")
        return {'status': 'error', 'reason': str(exc)}


@shared_task
def update_interaction_features():
    """
    Aggregate user interactions into features for ML
    """
    from recommendations.models import InteractionFeature
    from users.models import UserInteraction
    from django.db.models import Count, Avg, Max
    
    logger.info("Starting interaction features update")
    
    # Get all unique user-product pairs
    interactions = UserInteraction.objects.values(
        'user_id', 'product_id'
    ).annotate(
        views=Count('id', filter=Q(interaction_type='VIEW')),
        ar_tries=Count('id', filter=Q(interaction_type='AR_TRY')),
        interactions_3d=Count('id', filter=Q(interaction_type__in=['3D_ROTATE', 'ZOOM'])),
        avg_duration=Avg('duration_seconds'),
        last_interaction=Max('created_at')
    )
    
    updated = 0
    for item in interactions:
        engagement_score = (
            item['views'] * 1.0 +
            item['ar_tries'] * 5.0 +
            item['interactions_3d'] * 2.0 +
            (item['avg_duration'] or 0) / 60.0
        )
        
        InteractionFeature.objects.update_or_create(
            user_id=item['user_id'],
            product_id=item['product_id'],
            defaults={
                'total_views': item['views'],
                'total_ar_tries': item['ar_tries'],
                'total_3d_interactions': item['interactions_3d'],
                'avg_session_duration': item['avg_duration'] or 0,
                'last_interaction_date': item['last_interaction'],
                'engagement_score': engagement_score,
            }
        )
        updated += 1
    
    logger.info(f"Updated {updated} interaction features")
    return {'status': 'success', 'updated': updated}


@shared_task
def train_recommendation_model():
    """
    Train a new recommendation model (placeholder for ML training)
    """
    logger.info("Starting recommendation model training")
    # In production, this would train an actual ML model
    # using scikit-learn or other ML frameworks
    return {'status': 'success', 'message': 'Model training placeholder'}
