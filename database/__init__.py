"""
Database Package Initialization
Location: agribot/database/__init__.py

Initializes the database package and provides setup functions
for database initialization and configuration.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app"""
    # Import all models to ensure they're registered with SQLAlchemy
    from database.models.user import User
    from database.models.conversation import Conversation, Message
    from database.models.analytics import Feedback, UsageAnalytics, ErrorLog
    from database.models.geographic import GeographicData, ClimateData
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created")
    
    return db

def get_db():
    """Get database instance"""
    return db