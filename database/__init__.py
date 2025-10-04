"""
Database Package Initialization
Location: agribot/database/__init__.py

Initializes the database package and provides setup functions
for database initialization and configuration.
"""

import os
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
    # This is safe for both development and production
    with app.app_context():
        db.create_all()
        env = os.environ.get('FLASK_ENV', app.config.get('ENV', 'development'))
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'unknown')
        db_type = 'PostgreSQL' if 'postgresql' in db_url else 'SQLite'
        app.logger.info(f"Database tables created/verified - {db_type} ({env} mode)")

    return db

def get_db():
    """Get database instance"""
    return db