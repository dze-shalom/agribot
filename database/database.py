# setup_database.py
"""
Database setup script for AgriBot
Run this script to initialize the database with tables and initial data
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from database.seeders.initial_data import seed_initial_data
from config.settings import get_config

def setup_database():
    """Setup database with tables and initial data"""
    
    config = get_config()
    
    print("🗄️  Setting up AgriBot database...")
    
    # Create database engine
    engine = create_engine(config.database.url)
    
    # Test connection
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Run migrations
    try:
        print("🔄 Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    # Seed initial data
    try:
        print("🌱 Seeding initial data...")
        seed_initial_data()
        print("✅ Initial data seeded")
    except Exception as e:
        print(f"❌ Data seeding failed: {e}")
        return False
    
    print("\n🎉 Database setup completed successfully!")
    print("\n📋 Summary:")
    print("- All tables created")
    print("- Admin user: admin@agribot.cm (password: admin123)")
    print("- Demo farmer: farmer@test.cm (password: farmer123)")
    print("- Crop knowledge base initialized")
    
    return True

if __name__ == "__main__":
    if setup_database():
        print("\n🚀 You can now start the application with: python run.py")
    else:
        print("\n💥 Setup failed. Please check the errors above.")
        sys.exit(1)