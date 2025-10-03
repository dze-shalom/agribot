"""
Reset admin user password on production database
"""
import os
import sys
from werkzeug.security import generate_password_hash

def reset_password(db_url, email, new_password):
    """Reset password for an admin user"""

    os.environ['DATABASE_URL'] = db_url
    os.environ['FLASK_ENV'] = 'production'

    from app.main import create_app

    app = create_app()

    with app.app_context():
        from database import db
        from database.models.user import User

        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"ERROR: User with email {email} not found!")
            return False

        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        print(f"Password reset successfully!")
        print(f"  User: {user.name}")
        print(f"  Email: {user.email}")
        print(f"  Account Type: {user.account_type.value}")
        print(f"\nNew credentials:")
        print(f"  Email: {user.email}")
        print(f"  Password: {new_password}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python reset_admin_password.py <db_url> <email> <new_password>")
        print("\nExample:")
        print('  python reset_admin_password.py "postgresql://user:pass@host/db" "admin@example.com" "newpassword123"')
        print("\nFor Render deployment:")
        print('  python reset_admin_password.py "$DATABASE_URL" "shalom.dze-kum@aims-cameroon.org" "your_new_password"')
        sys.exit(1)

    db_url = sys.argv[1]
    email = sys.argv[2]
    new_password = sys.argv[3]

    reset_password(db_url, email, new_password)
