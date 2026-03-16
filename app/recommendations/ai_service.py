from app.products.models import Product
from sqlalchemy import func
import random


def get_smart_recommendations(user_id, limit=10):
    """
    Get product recommendations based on user's recent browsing history.
    Returns a mix of products from categories the user has recently viewed.
    No strict limit per category - just relevant products.
    """
    from app.recommendations.models import BrowsingHistory
    from app import db
    
    # Get user's recent browsing history (last 10 items)
    recent_history = BrowsingHistory.query.filter_by(user_id=user_id)\
        .order_by(BrowsingHistory.viewed_at.desc())\
        .limit(10)\
        .all()
    
    if not recent_history:
        return []
    
    # Get product IDs they've already viewed
    viewed_product_ids = [h.product_id for h in recent_history]
    
    # Get all categories from recently viewed products
    recent_categories = []
    for history_item in recent_history:
        if history_item.product and history_item.product.category_id:
            recent_categories.append(history_item.product.category_id)
    
    if not recent_categories:
        return []
    
    # Get unique categories (keep order based on recency)
    unique_categories = []
    seen = set()
    for cat_id in recent_categories:
        if cat_id not in seen:
            unique_categories.append(cat_id)
            seen.add(cat_id)
    
    # Get products from these categories (that user hasn't viewed)
    recommendations = Product.query.filter(
        Product.category_id.in_(unique_categories),
        Product.id.notin_(viewed_product_ids),
        Product.is_active == True,
        Product.stock > 0
    ).limit(limit * 2).all()  # Get extra to shuffle
    
    # Shuffle for variety
    random.shuffle(recommendations)
    
    # Return up to limit (but flexible based on what's available)
    return recommendations[:limit] if len(recommendations) > limit else recommendations