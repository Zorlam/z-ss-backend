from flask import Blueprint, request, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.orders.models import Order, OrderItem
from app.products.models import Product
from app.auth.models import User
from app.recommendations.models import BrowsingHistory
from app.common.decorators import admin_required

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/sales/summary", methods=["GET"])
@admin_required
def sales_summary():
    """Overall sales metrics."""
    days = request.args.get("days", 30, type=int)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    total_orders = Order.query.filter(Order.created_at >= cutoff).count()
    completed_orders = Order.query.filter(
        Order.created_at >= cutoff,
        Order.status.in_(["delivered", "shipped"]),
    ).count()
    cancelled_orders = Order.query.filter(
        Order.created_at >= cutoff,
        Order.status == "cancelled",
    ).count()

    total_revenue = db.session.query(
        func.coalesce(func.sum(Order.total_price), 0)
    ).filter(
        Order.created_at >= cutoff,
        Order.status.notin_(["cancelled"]),
    ).scalar()

    avg_order_value = (
        db.session.query(func.avg(Order.total_price))
        .filter(
            Order.created_at >= cutoff,
            Order.status.notin_(["cancelled"]),
        )
        .scalar()
    )

    return jsonify({
        "period_days": days,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "total_revenue": float(total_revenue or 0),
        "average_order_value": float(avg_order_value or 0),
    }), 200


@analytics_bp.route("/products/top", methods=["GET"])
@admin_required
def top_products():
    """Most purchased products."""
    limit = request.args.get("limit", 10, type=int)
    days = request.args.get("days", 30, type=int)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.session.query(
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_revenue"),
        )
        .join(Order, OrderItem.order_id == Order.id)
        .filter(
            Order.created_at >= cutoff,
            Order.status.notin_(["cancelled"]),
        )
        .group_by(OrderItem.product_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )

    results = []
    for row in rows:
        product = Product.query.get(row.product_id)
        if product:
            results.append({
                "product": product.to_dict(),
                "total_sold": int(row.total_sold),
                "total_revenue": float(row.total_revenue),
            })

    return jsonify({"top_products": results, "period_days": days}), 200


@analytics_bp.route("/users/activity", methods=["GET"])
@admin_required
def user_activity():
    """User registration and activity summary."""
    days = request.args.get("days", 30, type=int)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    new_users = User.query.filter(User.created_at >= cutoff).count()
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()

    # Users who placed orders in the period
    buying_users = (
        db.session.query(func.count(func.distinct(Order.user_id)))
        .filter(Order.created_at >= cutoff)
        .scalar()
    )

    # Top browsers
    top_browsers = (
        db.session.query(
            BrowsingHistory.user_id,
            func.count(BrowsingHistory.id).label("views"),
        )
        .filter(BrowsingHistory.viewed_at >= cutoff)
        .group_by(BrowsingHistory.user_id)
        .order_by(func.count(BrowsingHistory.id).desc())
        .limit(10)
        .all()
    )

    top_browser_data = []
    for row in top_browsers:
        user = User.query.get(row.user_id)
        if user:
            top_browser_data.append({
                "user_id": row.user_id,
                "username": user.username,
                "page_views": row.views,
            })

    return jsonify({
        "period_days": days,
        "total_users": total_users,
        "active_users": active_users,
        "new_users_in_period": new_users,
        "buying_users_in_period": buying_users,
        "top_browsers": top_browser_data,
    }), 200


@analytics_bp.route("/orders/status-breakdown", methods=["GET"])
@admin_required
def order_status_breakdown():
    """Order count grouped by status."""
    rows = (
        db.session.query(Order.status, func.count(Order.id).label("count"))
        .group_by(Order.status)
        .all()
    )
    return jsonify({
        "status_breakdown": {row.status: row.count for row in rows}
    }), 200


@analytics_bp.route("/products/low-stock", methods=["GET"])
@admin_required
def low_stock_products():
    """Products with stock below a threshold."""
    threshold = request.args.get("threshold", 10, type=int)
    products = (
        Product.query.filter(
            Product.stock <= threshold,
            Product.is_active == True,
        )
        .order_by(Product.stock.asc())
        .all()
    )
    return jsonify({
        "low_stock_products": [p.to_dict() for p in products],
        "threshold": threshold,
        "count": len(products),
    }), 200