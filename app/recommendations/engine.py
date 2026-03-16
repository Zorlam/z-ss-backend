"""
AI Recommendations Engine — Rule-Based Placeholder
----------------------------------------------------
This module implements a lightweight, rule-based recommendation engine.
It is designed to be swapped out for a proper ML model (collaborative
filtering, content-based, or hybrid) in the future.

Current strategy:
  1. Same-category products the user hasn't viewed yet
  2. Top-selling products across the platform
  3. Trending products (recently purchased frequently)
"""

from sqlalchemy import func
from app.products.models import Product
from app.orders.models import OrderItem
from app.recommendations.models import BrowsingHistory


def get_recommendations_for_user(user_id: int, limit: int = 10) -> list:
    """
    Returns a list of recommended Product objects for a given user.
    Strategy: category affinity → top sellers → fill with latest products.
    """
    # Step 1: Get categories the user has browsed
    viewed_product_ids = _get_viewed_product_ids(user_id)
    preferred_categories = _get_preferred_categories(user_id, viewed_product_ids)

    recommendations = []
    seen_ids = set(viewed_product_ids)

    # Step 2: Recommend from preferred categories (unseen)
    if preferred_categories:
        category_recs = (
            Product.query.filter(
                Product.category_id.in_(preferred_categories),
                Product.id.notin_(seen_ids),
                Product.is_active == True,
                Product.stock > 0,
            )
            .order_by(Product.created_at.desc())
            .limit(limit)
            .all()
        )
        for p in category_recs:
            if p.id not in seen_ids:
                recommendations.append(p)
                seen_ids.add(p.id)

    # Step 3: Top-selling products not yet seen
    if len(recommendations) < limit:
        needed = limit - len(recommendations)
        top_sellers = _get_top_sellers(seen_ids, needed)
        for p in top_sellers:
            if p.id not in seen_ids:
                recommendations.append(p)
                seen_ids.add(p.id)

    # Step 4: Fill with latest active products
    if len(recommendations) < limit:
        needed = limit - len(recommendations)
        fillers = (
            Product.query.filter(
                Product.id.notin_(seen_ids),
                Product.is_active == True,
                Product.stock > 0,
            )
            .order_by(Product.created_at.desc())
            .limit(needed)
            .all()
        )
        recommendations.extend(fillers)

    return recommendations[:limit]


def get_similar_products(product_id: int, limit: int = 6) -> list:
    """Returns products in the same category, excluding the current product."""
    product = Product.query.get(product_id)
    if not product:
        return []

    query = Product.query.filter(
        Product.id != product_id,
        Product.is_active == True,
        Product.stock > 0,
    )

    if product.category_id:
        query = query.filter(Product.category_id == product.category_id)

    return query.order_by(Product.created_at.desc()).limit(limit).all()


def get_trending_products(limit: int = 10) -> list:
    """Returns the most purchased products in the last 30 days."""
    from datetime import datetime, timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    top_ids = (
        OrderItem.query.with_entities(
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label("total_sold"),
        )
        .join(OrderItem.order)
        .filter(
            OrderItem.order.has(
                __import__("app.orders.models", fromlist=["Order"]).Order.created_at >= cutoff
            )
        )
        .group_by(OrderItem.product_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )

    product_ids = [row.product_id for row in top_ids]
    if not product_ids:
        return Product.query.filter_by(is_active=True).order_by(
            Product.created_at.desc()
        ).limit(limit).all()

    # Preserve order
    id_to_product = {p.id: p for p in Product.query.filter(Product.id.in_(product_ids)).all()}
    return [id_to_product[pid] for pid in product_ids if pid in id_to_product]


# ── Internal helpers ─────────────────────────────────────────────────────────

def _get_viewed_product_ids(user_id: int) -> list:
    rows = (
        BrowsingHistory.query.filter_by(user_id=user_id)
        .with_entities(BrowsingHistory.product_id)
        .distinct()
        .all()
    )
    return [r.product_id for r in rows]


def _get_preferred_categories(user_id: int, viewed_ids: list) -> list:
    if not viewed_ids:
        return []
    rows = (
        Product.query.filter(Product.id.in_(viewed_ids))
        .with_entities(Product.category_id, func.count(Product.id).label("cnt"))
        .group_by(Product.category_id)
        .order_by(func.count(Product.id).desc())
        .limit(3)
        .all()
    )
    return [r.category_id for r in rows if r.category_id is not None]


def _get_top_sellers(exclude_ids: set, limit: int) -> list:
    rows = (
        OrderItem.query.with_entities(
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label("total_sold"),
        )
        .group_by(OrderItem.product_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit + len(exclude_ids))
        .all()
    )
    product_ids = [r.product_id for r in rows if r.product_id not in exclude_ids]
    if not product_ids:
        return []
    id_to_product = {p.id: p for p in Product.query.filter(
        Product.id.in_(product_ids),
        Product.is_active == True,
    ).all()}
    return [id_to_product[pid] for pid in product_ids if pid in id_to_product][:limit]