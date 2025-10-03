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
    from database.models import user, conversation, analytics, geographic
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import all models to ensure they're registered
    from database.models.user import User
    from database.models.conversation import Conversation, Message
    from database.models.analytics import Feedback, UsageAnalytics, ErrorLog
    from database.models.geographic import GeographicData
    
    return db