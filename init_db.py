from app import create_app
from app.extensions import db
from app.auth.models import User
from app.products.models import Product, Category
from app.cart.models import CartItem
from app.orders.models import Order, OrderItem
from app.recommendations.models import BrowsingHistory
from app.wishlist.models import Wishlist

def init_database():
    """Initialize the database with all tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@clothingai.com').first()
        if not admin:
            from app.extensions import bcrypt
            admin = User(
                username='admin',
                email='admin@clothingai.com',
                password_hash=bcrypt.generate_password_hash('Admin123!').decode('utf-8'),
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created!")
            print("   Email: admin@clothingai.com")
            print("   Password: Admin123!")
        else:
            print("ℹ️  Admin user already exists")

if __name__ == '__main__':
    init_database()
