from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from .models import Product, Category
from .schemas import ProductSchema, ProductUpdateSchema, CategorySchema
from app.common.decorators import admin_required
from app.recommendations.models import BrowsingHistory
from datetime import datetime, timezone

products_bp = Blueprint("products", __name__)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_update_schema = ProductUpdateSchema()
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


# ── CATEGORIES ──────────────────────────────────────────────────────────────

@products_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify({"categories": [c.to_dict() for c in categories]}), 200


@products_bp.route("/categories", methods=["POST"])
@admin_required
def create_category():
    try:
        data = category_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if Category.query.filter_by(slug=data["slug"]).first():
        return jsonify({"error": "Category slug already exists"}), 409

    category = Category(**data)
    db.session.add(category)
    db.session.commit()
    return jsonify({"message": "Category created", "category": category.to_dict()}), 201


@products_bp.route("/categories/<int:category_id>", methods=["PUT"])
@admin_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    try:
        data = category_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    for key, value in data.items():
        setattr(category, key, value)

    db.session.commit()
    return jsonify({"message": "Category updated", "category": category.to_dict()}), 200


@products_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"}), 200


# ── PRODUCTS ─────────────────────────────────────────────────────────────────

@products_bp.route("/", methods=["GET"])
def get_products():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    category_id = request.args.get("category_id", type=int)
    search = request.args.get("search", "")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    in_stock = request.args.get("in_stock", "false").lower() == "true"

    query = Product.query.filter_by(is_active=True)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if in_stock:
        query = query.filter(Product.stock > 0)

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "products": [p.to_dict() for p in paginated.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev,
        },
    }), 200


@products_bp.route("/<int:product_id>", methods=["GET"])
@jwt_required(optional=True)
def get_product(product_id):
    product = Product.query.get_or_404(product_id)

    # Track browsing history if user is authenticated
    user_id = get_jwt_identity()
    if user_id:
        history = BrowsingHistory(
            user_id=user_id,
            product_id=product_id,
            viewed_at=datetime.now(timezone.utc),
        )
        db.session.add(history)
        db.session.commit()

    return jsonify({"product": product.to_dict()}), 200


@products_bp.route("/", methods=["POST"])
@admin_required
def create_product():
    try:
        data = product_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422
    
    # BACKEND VALIDATION
    name = data.get('name', '').strip()
    price = data.get('price')
    stock = data.get('stock', 0)
    
    # Validate name
    if not name or len(name) < 2 or len(name) > 255:
        return jsonify({"error": "Product name must be 2-255 characters"}), 400
    
    # Validate price
    if price is None or float(price) < 0 or float(price) > 1000000:
        return jsonify({"error": "Price must be between 0 and 1,000,000"}), 400
    
    # Validate stock
    if stock < 0 or stock > 100000:
        return jsonify({"error": "Stock must be between 0 and 100,000"}), 400
    
    # Update data with cleaned values
    data['name'] = name

    if data.get("sku") and Product.query.filter_by(sku=data["sku"]).first():
        return jsonify({"error": "SKU already exists"}), 409

    # Remove nested objects before creating
    data.pop("category", None)
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product created", "product": product.to_dict()}), 201


@products_bp.route("/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        data = product_update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    for key, value in data.items():
        setattr(product, key, value)

    db.session.commit()
    return jsonify({"message": "Product updated", "product": product.to_dict()}), 200


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False  # Soft delete
    db.session.commit()
    return jsonify({"message": "Product deactivated"}), 200


@products_bp.route("/<int:product_id>/stock", methods=["PATCH"])
@admin_required
def update_stock(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    stock = data.get("stock")

    if stock is None or not isinstance(stock, int) or stock < 0:
        return jsonify({"error": "Valid stock value required (non-negative integer)"}), 422

    product.stock = stock
    db.session.commit()
    return jsonify({"message": "Stock updated", "product": product.to_dict()}), 200


from flask import request
from app.common.file_utils import save_product_image

@products_bp.route("/upload-image", methods=["POST"])
@admin_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files['image']
    
    try:
        image_url = save_product_image(file)
        if not image_url:
            return jsonify({"error": "Failed to save image"}), 400
        
        # Return full URL with host - Use HTTPS in production
        scheme = 'https' if request.host != 'localhost' and request.host != '127.0.0.1' else 'http'
        host = f"{scheme}://{request.host}"
        full_url = f"{host}{image_url}"
        return jsonify({"image_url": full_url}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to upload image"}), 500