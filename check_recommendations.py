from app import create_app, db
from app.recommendations.models import BrowsingHistory
from app.recommendations.ai_service import get_smart_recommendations
from app.auth.models import User

app = create_app()
with app.app_context():
    # Get the first user with browsing history
    users_with_history = db.session.query(BrowsingHistory.user_id).distinct().all()
    
    if not users_with_history:
        print("No users have browsing history!")
    else:
        user_id = users_with_history[0][0]
        user = User.query.get(user_id)
        
        print(f"Testing recommendations for: {user.username} (ID: {user_id})")
        print("="*60)
        
        # Get their browsing history
        history = BrowsingHistory.query.filter_by(user_id=user_id)\
            .order_by(BrowsingHistory.viewed_at.desc())\
            .limit(6)\
            .all()
        
        print(f"\nLast 6 products viewed:")
        for h in history:
            cat_name = h.product.category.name if h.product and h.product.category else "No Category"
            print(f"  - Product {h.product_id}: {h.product.name if h.product else 'Unknown'} (Category: {cat_name})")
        
        # Get recommendations
        recommendations = get_smart_recommendations(user_id, limit=6)
        
        print(f"\n{'='*60}")
        print(f"RECOMMENDATIONS GENERATED: {len(recommendations)}")
        print(f"{'='*60}")
        
        for i, rec in enumerate(recommendations, 1):
            cat_name = rec.category.name if rec.category else "No Category"
            print(f"{i}. {rec.name} (Category: {cat_name}, ID: {rec.id})")