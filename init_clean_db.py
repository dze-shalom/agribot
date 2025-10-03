#!/usr/bin/env python3
"""
Initialize a clean database with proper enum values
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from database import db
from database.models.user import User, CameroonRegion, AccountType, UserStatus
from app.main import create_app
from werkzeug.security import generate_password_hash

def init_clean_database():
    """Initialize a clean database with proper users"""
    print("Creating clean AgriBot application...")
    app = create_app()

    with app.app_context():
        # Drop all existing tables and recreate them
        print("Dropping existing tables...")
        db.drop_all()

        print("Creating new tables...")
        db.create_all()

        # Create admin user with proper enum values (lowercase)
        print("Creating admin user...")
        admin_user = User(
            name='Admin',
            email='admin@agribot.com',
            password_hash=generate_password_hash('admin123'),
            region=CameroonRegion.CENTRE,  # This will store 'centre'
            account_type=AccountType.ADMIN,  # This will store 'admin'
            status=UserStatus.ACTIVE  # This will store 'active'
        )

        # Create test user with proper enum values (lowercase)
        print("Creating test user...")
        test_user = User(
            name='Test User',
            email='user@agribot.com',
            password_hash=generate_password_hash('user123'),
            region=CameroonRegion.CENTRE,  # This will store 'centre'
            account_type=AccountType.USER,  # This will store 'user'
            status=UserStatus.ACTIVE  # This will store 'active'
        )

        # Add users to the database
        db.session.add(admin_user)
        db.session.add(test_user)
        db.session.commit()

        print("Database initialized successfully!")
        print(f"Admin user: admin@agribot.com / admin123")
        print(f"Test user: user@agribot.com / user123")

        # Verify the data was saved correctly
        print("\nVerifying stored enum values:")
        for user in User.query.all():
            print(f"User {user.id}: {user.name} - region={user.region.value}, type={user.account_type.value}, status={user.status.value}")

if __name__ == "__main__":
    init_clean_database()