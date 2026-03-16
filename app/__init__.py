from flask import Flask
from .config import get_config
from .extensions import db, jwt, bcrypt, cors, migrate, limiter
from app.wishlist.routes import wishlist_bp


def create_app():
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)  # ← THIS LINE WAS MISSING!

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    # Register blueprints
    from .auth.routes import auth_bp
    from .products.routes import products_bp
    from .cart.routes import cart_bp
    from .orders.routes import orders_bp
    from .recommendations.routes import recommendations_bp
    from .analytics.routes import analytics_bp
    from .search.routes import search_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(recommendations_bp, url_prefix="/api/recommendations")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(search_bp, url_prefix="/api/search")
    app.register_blueprint(wishlist_bp, url_prefix="/api/wishlist")

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "ClothingAI API is running"}, 200

    # Import all models so Flask-Migrate can detect them
    with app.app_context():
        from .auth import models as auth_models  # noqa: F401
        from .products import models as product_models  # noqa: F401
        from .cart import models as cart_models  # noqa: F401
        from .orders import models as order_models  # noqa: F401
        from .recommendations import models as rec_models  # noqa: F401

    return app