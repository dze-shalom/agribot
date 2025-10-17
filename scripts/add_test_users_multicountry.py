"""
Add test users from multiple countries to demonstrate multi-country analytics
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from database.models.user import User, AccountType
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

def add_multicountry_users():
    """Add test users from Kenya and Nigeria"""
    from app.main import create_app
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 60)
        print("ADDING MULTI-COUNTRY TEST USERS")
        print("=" * 60)

        # Test users from different countries
        test_users = [
            # Kenya users
            {
                'name': 'James Kimani',
                'email': 'james.kimani@test-kenya.com',
                'country': 'Kenya',
                'region': 'Nairobi',
                'account_type': AccountType.USER
            },
            {
                'name': 'Mary Wanjiku',
                'email': 'mary.wanjiku@test-kenya.com',
                'country': 'Kenya',
                'region': 'Nakuru',
                'account_type': AccountType.USER
            },
            {
                'name': 'Peter Ochieng',
                'email': 'peter.ochieng@test-kenya.com',
                'country': 'Kenya',
                'region': 'Kisumu',
                'account_type': AccountType.USER
            },
            # Nigeria users
            {
                'name': 'Chidinma Okafor',
                'email': 'chidinma.okafor@test-nigeria.com',
                'country': 'Nigeria',
                'region': 'Lagos',
                'account_type': AccountType.USER
            },
            {
                'name': 'Ibrahim Yusuf',
                'email': 'ibrahim.yusuf@test-nigeria.com',
                'country': 'Nigeria',
                'region': 'Kano',
                'account_type': AccountType.USER
            },
            {
                'name': 'Funmilayo Adeyemi',
                'email': 'funmilayo.adeyemi@test-nigeria.com',
                'country': 'Nigeria',
                'region': 'Oyo (Ibadan)',
                'account_type': AccountType.USER
            },
        ]

        added = 0
        skipped = 0

        for user_data in test_users:
            # Check if user already exists
            existing = User.query.filter_by(email=user_data['email']).first()
            if existing:
                print(f"  SKIP: {user_data['name']} ({user_data['country']}) - already exists")
                skipped += 1
                continue

            # Create new user
            new_user = User(
                name=user_data['name'],
                email=user_data['email'],
                country=user_data['country'],
                region=user_data['region'],
                account_type=user_data['account_type'],
                password_hash=generate_password_hash('password123'),  # Default test password
                phone=None,
                created_at=datetime.now(timezone.utc)
            )

            db.session.add(new_user)
            print(f"  ADD: {user_data['name']} ({user_data['country']} - {user_data['region']})")
            added += 1

        # Commit all changes
        db.session.commit()

        print("\n" + "=" * 60)
        print(f"SUMMARY:")
        print(f"  Added: {added} users")
        print(f"  Skipped: {skipped} users (already exist)")
        print("=" * 60)

        # Show updated distribution
        print("\nUpdated Country Distribution:")
        print("-" * 60)
        from sqlalchemy import func
        from database.models.user import UserStatus

        country_dist = db.session.query(
            User.country,
            func.count(User.id).label('count')
        ).filter(User.status != UserStatus.DELETED).group_by(User.country).all()

        for country, count in country_dist:
            print(f"  {country}: {count} users")

        print("\n" + "=" * 60)
        print("TEST USERS ADDED SUCCESSFULLY!")
        print("=" * 60)
        print("\nTest Login Credentials:")
        print("  Email: james.kimani@test-kenya.com")
        print("  Password: password123")
        print("\n  (Same password for all test users)")
        print("=" * 60 + "\n")


if __name__ == '__main__':
    add_multicountry_users()
