from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin

from app.products.models import Product
from app.recommendations.models import BrowsingHistory
from app.recommendations.ai_service import get_smart_recommendations

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/ai', methods=['GET'])
@cross_origin()
@jwt_required()
def get_recommendations():
    """Get smart product recommendations based on browsing history (no AI required)"""
    user_id = get_jwt_identity()
    
    try:
        recommendations = get_smart_recommendations(user_id, limit=6)  # Changed to 6
        
        return jsonify({
            "recommendations": [p.to_dict() for p in recommendations]
        }), 200
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return jsonify({"error": "Failed to get recommendations", "recommendations": []}), 200
    
    # Get user's browsing history (last 10 items)
    browsing_history = BrowsingHistory.query.filter_by(user_id=user_id)\
        .order_by(BrowsingHistory.viewed_at.desc())\
        .limit(10)\
        .all()
    
    # If no browsing history, return empty
    if not browsing_history:
        return jsonify({"recommendations": []}), 200
    
    # Get products from browsing history
    viewed_products = [item.product.to_dict() for item in browsing_history]
    
    # Get all active products
    all_products = Product.query.filter_by(is_active=True).all()
    products_dict = [p.to_dict() for p in all_products]
    
    # Get smart recommendations (no AI)
    recommended_ids = get_smart_recommendations(viewed_products, products_dict, limit=6)
    
    if recommended_ids:
        # Fetch recommended products in order
        recommended_products = Product.query.filter(Product.id.in_(recommended_ids)).all()
        recommended_products.sort(key=lambda p: recommended_ids.index(p.id))
        
        return jsonify({
            "recommendations": [p.to_dict() for p in recommended_products]
        }), 200
    
    return jsonify({"recommendations": []}), 200