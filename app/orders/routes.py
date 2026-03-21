from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from .models import Order, OrderItem
from .schemas import CreateOrderSchema, UpdateOrderStatusSchema
from app.cart.models import CartItem
from app.common.decorators import admin_required

orders_bp = Blueprint("orders", __name__)

create_schema = CreateOrderSchema()
status_schema = UpdateOrderStatusSchema()


@orders_bp.route("/", methods=["POST"])
@jwt_required()
def create_order():
    user_id = int(get_jwt_identity())

    try:
        data = create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    # Validate stock for all items before creating order
    for item in cart_items:
        if not item.product or not item.product.is_active:
            return jsonify({"error": f"Product {item.product_id} is unavailable"}), 400
        if item.product.stock < item.quantity:
            return jsonify({
                "error": f"Insufficient stock for '{item.product.name}'. Available: {item.product.stock}"
            }), 400

    total_price = sum(float(item.product.price) * item.quantity for item in cart_items)

    order = Order(
        user_id=user_id,
        status="pending",
        total_price=total_price,
        shipping_address=data["shipping_address"],
        notes=data.get("notes"),
    )
    db.session.add(order)
    db.session.flush()  # Get order.id before committing

    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.price,
        )
        db.session.add(order_item)

        # Deduct stock
        cart_item.product.stock -= cart_item.quantity

    # Clear cart
    CartItem.query.filter_by(user_id=user_id).delete()

    db.session.commit()
    return jsonify({"message": "Order created successfully", "order": order.to_dict()}), 201


@orders_bp.route("/", methods=["GET"])
@jwt_required()
def get_my_orders():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    paginated = (
        Order.query.filter_by(user_id=user_id)
        .order_by(Order.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "orders": [o.to_dict() for o in paginated.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages,
        },
    }), 200


@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get_or_404(order_id)

    # Users can only see their own orders; admins can see all
    from app.auth.models import User
    user = User.query.get(int(user_id))
    if order.user_id != int(user_id) and user.role != "admin":
        return jsonify({"error": "Access denied"}), 403

    return jsonify({"order": order.to_dict()}), 200


@orders_bp.route("/<int:order_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

    if order.status not in ["pending", "confirmed"]:
        return jsonify({"error": f"Cannot cancel order with status '{order.status}'"}), 400

    # Restore stock
    for item in order.items:
        if item.product:
            item.product.stock += item.quantity

    order.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Order cancelled", "order": order.to_dict()}), 200


# ── ADMIN ORDER MANAGEMENT ───────────────────────────────────────────────────

@orders_bp.route("/admin/all", methods=["GET"])
@admin_required
def admin_list_orders():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")

    query = Order.query
    if status:
        query = query.filter_by(status=status)

    paginated = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "orders": [o.to_dict() for o in paginated.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages,
        },
    }), 200


@orders_bp.route("/admin/<int:order_id>/status", methods=["PATCH"])
@admin_required
def admin_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)

    try:
        data = status_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    order.status = data["status"]
    db.session.commit()
    return jsonify({"message": "Order status updated", "order": order.to_dict()}), 200