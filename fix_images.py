from app import create_app
from app.extensions import db
from app.products.models import Product

app = create_app()

with app.app_context():
    products = Product.query.all()
    
    for product in products:
        if product.image_url and ('http://127.0.0.1:5000' in product.image_url or 'http://172.20.10.2:5000' in product.image_url):
            # Replace old IPs with new IP
            product.image_url = product.image_url.replace('http://127.0.0.1:5000', 'http://172.20.10.3:5000')
            product.image_url = product.image_url.replace('http://172.20.10.2:5000', 'http://172.20.10.3:5000')
            print(f"Updated {product.name}: {product.image_url}")
    
    db.session.commit()
    print(f"\nDone!")