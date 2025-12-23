"""
Celery tasks for dynamic pricing
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_product_pricing():
    """
    Update product pricing based on demand and inventory
    """
    from products.models import Product, PriceHistory
    
    if not settings.DYNAMIC_PRICING_ENABLED:
        return {'status': 'skipped', 'reason': 'dynamic_pricing_disabled'}
    
    logger.info("Starting dynamic pricing update")
    
    products = Product.objects.filter(is_active=True, is_limited_edition=True)
    updated_count = 0
    
    for product in products:
        old_price = product.current_price
        base_price = product.base_price
        
        # Calculate demand-based adjustment
        demand_score = product.demand_score
        stock_ratio = product.stock_quantity / max(product.max_quantity_per_order, 1)
        
        # Pricing algorithm
        # Higher demand + lower stock = higher price
        demand_factor = min(demand_score / 100.0, 1.0)
        stock_factor = 1.0 - min(stock_ratio, 1.0)
        
        adjustment = (demand_factor * 0.5 + stock_factor * 0.5) * settings.PRICE_ADJUSTMENT_THRESHOLD
        
        new_price = base_price * (Decimal('1.0') + Decimal(str(adjustment)))
        
        # Ensure price doesn't deviate too much from base price
        max_price = base_price * Decimal('1.2')  # Max 20% increase
        min_price = base_price * Decimal('0.8')  # Max 20% decrease
        
        new_price = max(min_price, min(new_price, max_price))
        new_price = new_price.quantize(Decimal('0.01'))
        
        if new_price != old_price:
            product.current_price = new_price
            product.save(update_fields=['current_price', 'updated_at'])
            
            # Record price change
            PriceHistory.objects.create(
                product=product,
                old_price=old_price,
                new_price=new_price,
                reason='Dynamic pricing based on demand',
                demand_score=demand_score,
                stock_level=product.stock_quantity
            )
            
            updated_count += 1
            logger.info(f"Updated price for {product.name}: {old_price} -> {new_price}")
    
    logger.info(f"Dynamic pricing updated {updated_count} products")
    return {'status': 'success', 'updated_count': updated_count}


@shared_task
def publish_price_update_event(product_id, old_price, new_price):
    """
    Publish price update event to Kafka
    """
    # In production, this would publish to Kafka
    logger.info(f"Publishing price update event for product {product_id}")
    return {'status': 'success', 'product_id': product_id}
