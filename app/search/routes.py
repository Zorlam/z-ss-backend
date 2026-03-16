from flask import Blueprint, request, jsonify
from app.products.models import Product, Category
from sqlalchemy import or_, and_

search_bp = Blueprint('search', __name__, url_prefix='/api/search')


@search_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """Get search suggestions as user types"""
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 5, type=int)
    
    if not query or len(query) < 2:
        return jsonify({"suggestions": []}), 200
    
    # Search products by name (most relevant for suggestions)
    products = Product.query.filter(
        Product.is_active == True,
        Product.name.ilike(f'%{query}%')
    ).limit(limit).all()
    
    suggestions = [
        {
            "id": p.id,
            "name": p.name,
            "image_url": p.image_url,
            "price": float(p.price),
            "category": p.category.name if p.category else None
        }
        for p in products
    ]
    
    return jsonify({"suggestions": suggestions}), 200


@search_bp.route('/products', methods=['GET'])
def search_products():
    """Advanced keyword-based product search"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"products": [], "query": query}), 200
    
    # Split query into keywords
    keywords = [k.strip().lower() for k in query.split() if k.strip()]
    
    if not keywords:
        return jsonify({"products": [], "query": query}), 200
    
    # Build search conditions for each keyword
    search_conditions = []
    
    for keyword in keywords:
        keyword_pattern = f'%{keyword}%'
        
        # Search in name, description, category
        keyword_condition = or_(
            Product.name.ilike(keyword_pattern),
            Product.description.ilike(keyword_pattern),
            Product.category.has(Category.name.ilike(keyword_pattern))
        )
        search_conditions.append(keyword_condition)
    
    # Combine all keyword conditions with AND (all keywords must match)
    final_condition = and_(
        Product.is_active == True,
        *search_conditions
    )
    
    # Execute search
    products = Product.query.filter(final_condition).all()
    
    # If no results with AND, try with OR (any keyword matches)
    if not products:
        or_condition = and_(
            Product.is_active == True,
            or_(*search_conditions)
        )
        products = Product.query.filter(or_condition).all()
    
    return jsonify({
        "query": query,
        "keywords": keywords,
        "products": [p.to_dict() for p in products]
    }), 200


@search_bp.route('/ai', methods=['GET'])
def ai_search():
    """Redirect AI search to keyword search (no AI needed)"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"products": [], "query": query}), 200
    
    # Just use keyword search instead of AI
    return search_products()