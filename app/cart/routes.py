from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from .models import CartItem
from .schemas import AddToCartSchema, UpdateCartSchema
from app.products.models import Product

cart_bp = Blueprint("cart", __name__)

add_schema = AddToCartSchema()
update_schema = UpdateCartSchema()


@cart_bp.route("/", methods=["GET"])
@jwt_required()
def view_cart():
    user_id = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=user_id).all()

    total = sum(
        float(item.product.price) * item.quantity
        for item in items
        if item.product
    )

    return jsonify({
        "cart_items": [item.to_dict() for item in items],
        "total_items": len(items),
        "total_price": round(total, 2),
    }), 200


@cart_bp.route("/", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())

    try:
        data = add_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    product = Product.query.get(data["product_id"])
    if not product or not product.is_active:
        return jsonify({"error": "Product not found"}), 404

    if product.stock < data["quantity"]:
        return jsonify({"error": f"Insufficient stock. Available: {product.stock}"}), 400

    existing = CartItem.query.filter_by(
        user_id=user_id, product_id=data["product_id"]
    ).first()

    if existing:
        new_qty = existing.quantity + data["quantity"]
        if product.stock < new_qty:
            return jsonify({"error": f"Insufficient stock. Available: {product.stock}"}), 400
        existing.quantity = new_qty
        db.session.commit()
        return jsonify({"message": "Cart updated", "cart_item": existing.to_dict()}), 200

    cart_item = CartItem(
        user_id=user_id,
        product_id=data["product_id"],
        quantity=data["quantity"],
    )
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({"message": "Item added to cart", "cart_item": cart_item.to_dict()}), 201


@cart_bp.route("/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()

    try:
        data = update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if item.product.stock < data["quantity"]:
        return jsonify({"error": f"Insufficient stock. Available: {item.product.stock}"}), 400

    item.quantity = data["quantity"]
    db.session.commit()
    return jsonify({"message": "Cart item updated", "cart_item": item.to_dict()}), 200


@cart_bp.route("/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart"}), 200


@cart_bp.route("/clear", methods=["DELETE"])
@jwt_required()
def clear_cart():
    user_id = int(get_jwt_identity())
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared"}), 200