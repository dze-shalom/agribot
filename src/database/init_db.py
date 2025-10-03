"""
Database initialization script
Run this to set up your database for the first time
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from database.models import db
from database.database_manager import DatabaseManager
from config import Config

def initialize_database():
    """Initialize database with all tables and basic data"""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db_manager = DatabaseManager(app)
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Populating geographic data...")
        db_manager.populate_geographic_data()
        
        print("Database initialized successfully!")
        print(f"Database location: {Config.SQLALCHEMY_DATABASE_URI}")
        
        # Test the database
        from database.models import GeographicData
        region_count = GeographicData.query.count()
        print(f"Geographic data entries: {region_count}")

if __name__ == '__main__':
    initialize_database()