from datetime import datetime, timezone
from app.extensions import db


class BrowsingHistory(db.Model):
    __tablename__ = "browsing_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    viewed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship("User", back_populates="browsing_history")
    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product": self.product.to_dict() if self.product else None,
            "viewed_at": self.viewed_at.isoformat() if self.viewed_at else None,
        }

    def __repr__(self):
        return f"<BrowsingHistory user={self.user_id} product={self.product_id}>"