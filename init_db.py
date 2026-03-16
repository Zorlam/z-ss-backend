from app import create_app
from app.extensions import db, migrate
from flask_migrate import init, migrate as mig, upgrade

app = create_app()

with app.app_context():
    # Initialize migrations
    try:
        init()
        print("✅ Migrations folder created")
    except:
        print("ℹ️  Migrations folder already exists")
    
    # Create migration
    mig(message="Initial schema")
    print("✅ Migration files created")
    
    # Apply migration
    upgrade()
    print("✅ Database tables created")
    print("🎉 Database setup complete!")