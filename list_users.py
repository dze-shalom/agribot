"""
List all users in the database to find admin accounts
"""
import os
import sys

def list_users(db_url):
    """List all users in the database"""

    os.environ['DATABASE_URL'] = db_url
    os.environ['FLASK_ENV'] = 'production'

    from app.main import create_app

    app = create_app()

    with app.app_context():
        from database.models.user import User

        # Get all users
        users = User.query.all()

        if not users:
            print("No users found in database!")
            return

        print(f"\nFound {len(users)} user(s):\n")
        print("-" * 80)

        for user in users:
            account_type = user.account_type.value if hasattr(user.account_type, 'value') else user.account_type
            print(f"ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")
            print(f"Account Type: {account_type}")
            print(f"Region: {user.region}")
            print(f"Created: {user.created_at}")
            print("-" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python list_users.py <database_url>")
        print("\nExample:")
        print('  python list_users.py "postgresql://user:pass@host/db"')
        sys.exit(1)

    db_url = sys.argv[1]
    list_users(db_url)
