from app.extensions import db
from datetime import datetime, timezone


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    products = db.relationship("Product", back_populates="category", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # REMOVED "color": self.color, ← This was wrong
        }

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(100), unique=True)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    color = db.Column(db.String(100))
    
    # New fields for size, material, and care
    sizes = db.Column(db.String(200))  # Store as comma-separated: "S,M,L,XL,XXL"
    material = db.Column(db.String(255))  # e.g., "100% Cotton"
    care_instructions = db.Column(db.Text)  # Washing/care info

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    category = db.relationship("Category", back_populates="products")

    # Relationships with other models
    cart_items = db.relationship("CartItem", back_populates="product", lazy="dynamic")
    browsing_history = db.relationship("BrowsingHistory", back_populates="product", lazy="dynamic")
    order_items = db.relationship("OrderItem", back_populates="product", lazy="dynamic")

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        from flask import request
        
        # Get the current request's host dynamically
        image_url = self.image_url
        if image_url and image_url.startswith('/static/'):
            # Build URL using the current request's host
            if request:
                scheme = request.scheme  # http or https
                host = request.host  # Will be 172.20.10.X:5000 or 127.0.0.1:5000
                image_url = f"{scheme}://{host}{image_url}"
        
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "stock": self.stock,
            "sku": self.sku,
            "image_url": image_url,
            "is_active": self.is_active,
            "color": self.color,  # ← ADDED HERE (in Product, not Category)
            "sizes": self.sizes.split(',') if self.sizes else [],  # Convert to array
            "material": self.material,
            "care_instructions": self.care_instructions,
            "category": self.category.to_dict() if self.category else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Product {self.name}>"