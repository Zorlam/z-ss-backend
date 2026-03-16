from app import create_app
from app.recommendations.models import BrowsingHistory
from app.extensions import db

app = create_app()
with app.app_context():
    history = BrowsingHistory.query.all()
    print(f"Total browsing history entries: {len(history)}")
    for h in history[-5:]:  # Last 5 entries
        print(f"User {h.user_id} viewed product {h.product_id} at {h.viewed_at}")