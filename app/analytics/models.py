from app.extensions import db
from datetime import datetime, timezone


class BrowsingHistory(db.Model):
    __tablename__ = 'browsing_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref='browsing_history')
    product = db.relationship('Product', backref='browsing_history')
    
    def __repr__(self):
        return f'<BrowsingHistory user_id={self.user_id} product_id={self.product_id}>'