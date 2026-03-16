from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from .models import Wishlist
from app.products.models import Product

wishlist_bp = Blueprint("wishlist", __name__)


@wishlist_bp.route("/", methods=["GET"])
@jwt_required()
def get_wishlist():
    """Get user's wishlist"""
    user_id = get_jwt_identity()
    
    wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "wishlist_items": [item.to_dict() for item in wishlist_items]
    }), 200


@wishlist_bp.route("/<int:product_id>", methods=["POST"])
@jwt_required()
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    user_id = get_jwt_identity()
    
    # Check if product exists
    product = Product.query.get_or_404(product_id)
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        return jsonify({"message": "Product already in wishlist"}), 200
    
    # Add to wishlist
    wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
    db.session.add(wishlist_item)
    db.session.commit()
    
    return jsonify({
        "message": "Added to wishlist",
        "wishlist_item": wishlist_item.to_dict()
    }), 201


@wishlist_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def remove_from_wishlist(product_id):
    """Remove product from wishlist"""
    user_id = get_jwt_identity()
    
    wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first_or_404()
    
    db.session.delete(wishlist_item)
    db.session.commit()
    
    return jsonify({"message": "Removed from wishlist"}), 200


@wishlist_bp.route("/check/<int:product_id>", methods=["GET"])
@jwt_required()
def check_wishlist(product_id):
    """Check if product is in wishlist"""
    user_id = get_jwt_identity()
    
    exists = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first() is not None
    
    return jsonify({"in_wishlist": exists}), 200