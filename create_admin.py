"""
Create admin user directly on production PostgreSQL database
"""
import os
import sys
from werkzeug.security import generate_password_hash

def create_admin(db_url, email, password, name="Admin"):
    """Create an admin user directly on production"""

    os.environ['DATABASE_URL'] = db_url
    os.environ['FLASK_ENV'] = 'production'

    from app.main import create_app

    app = create_app()

    with app.app_context():
        from database import db
        from database.models.user import User, AccountType
        from datetime import datetime, timezone

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            print(f"  ID: {existing_user.id}")
            print(f"  Name: {existing_user.name}")
            print(f"  Account Type: {existing_user.account_type.value}")
            return False

        # Create new admin user
        admin = User(
            name=name,
            email=email,
            phone=None,
            country='Cameroon',
            region='Centre',
            account_type=AccountType.ADMIN,
            created_at=datetime.now(timezone.utc)
        )
        admin.password_hash = generate_password_hash(password)

        db.session.add(admin)
        db.session.commit()

        print(f"Admin user created successfully!")
        print(f"  ID: {admin.id}")
        print(f"  Name: {admin.name}")
        print(f"  Email: {admin.email}")
        print(f"  Account Type: {admin.account_type.value}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_admin.py <db_url> <email> <password> [name]")
        print("\nExample:")
        print('  python create_admin.py "postgresql://..." "admin@agribot.com" "secure_password" "Admin"')
        sys.exit(1)

    db_url = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    name = sys.argv[4] if len(sys.argv) > 4 else "Admin"

    create_admin(db_url, email, password, name)
