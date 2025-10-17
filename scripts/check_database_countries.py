"""
Diagnostic script to check what country and region data is actually in the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from database.models.user import User, UserStatus
from sqlalchemy import func

def check_country_distribution():
    """Check what countries are actually in the database"""
    print("=" * 60)
    print("COUNTRY DISTRIBUTION CHECK")
    print("=" * 60)

    # Get all users grouped by country
    country_dist = db.session.query(
        User.country,
        func.count(User.id).label('count')
    ).filter(User.status != UserStatus.DELETED).group_by(User.country).all()

    print(f"\nUsers by Country:")
    print("-" * 60)
    total_users = 0
    for country, count in country_dist:
        print(f"  {country or 'NULL'}: {count} users")
        total_users += count

    print(f"\nTotal users (excluding deleted): {total_users}")

    # Check if all users have country set
    users_without_country = User.query.filter(
        User.country.is_(None),
        User.status != UserStatus.DELETED
    ).count()

    if users_without_country > 0:
        print(f"\nWARNING: {users_without_country} users have NULL country!")

    return country_dist


def check_regional_distribution():
    """Check regional distribution by country"""
    print("\n" + "=" * 60)
    print("REGIONAL DISTRIBUTION BY COUNTRY")
    print("=" * 60)

    # Get distribution grouped by BOTH country and region
    regional_dist = db.session.query(
        User.country,
        User.region,
        func.count(User.id).label('count')
    ).filter(User.status != UserStatus.DELETED).group_by(User.country, User.region).all()

    # Organize by country
    by_country = {}
    for country, region, count in regional_dist:
        country_name = country or 'NULL'
        region_name = region if region else 'NULL'

        if country_name not in by_country:
            by_country[country_name] = []
        by_country[country_name].append((region_name, count))

    # Print organized results
    for country, regions in sorted(by_country.items()):
        print(f"\n{country}:")
        print("-" * 60)
        for region, count in sorted(regions, key=lambda x: x[1], reverse=True):
            print(f"  {region}: {count} users")

    return by_country


def check_sample_users():
    """Show sample users to understand data structure"""
    print("\n" + "=" * 60)
    print("SAMPLE USERS (First 10)")
    print("=" * 60)

    users = User.query.filter(User.status != UserStatus.DELETED).limit(10).all()

    print(f"\n{'ID':<6} {'Name':<20} {'Country':<15} {'Region':<20} {'Account':<10}")
    print("-" * 80)

    for user in users:
        account_type = user.account_type.value if hasattr(user.account_type, 'value') else user.account_type
        print(f"{user.id:<6} {user.name[:19]:<20} {(user.country or 'NULL')[:14]:<15} {(user.region or 'NULL')[:19]:<20} {account_type:<10}")


def main():
    """Run all checks"""
    try:
        # Initialize database
        from app.main import create_app
        app = create_app()

        with app.app_context():
            print("\nChecking database for country and regional distribution issues...\n")

            # Run checks
            country_dist = check_country_distribution()
            regional_dist = check_regional_distribution()
            check_sample_users()

            # Analysis
            print("\n" + "=" * 60)
            print("ANALYSIS & RECOMMENDATIONS")
            print("=" * 60)

            if len(country_dist) == 1:
                country_name = country_dist[0][0] or 'NULL'
                print(f"\nISSUE FOUND: All users are from '{country_name}'")
                print("   This explains why country distribution chart only shows one country!")
                print("\nSOLUTIONS:")
                print("   1. Import test users from other countries")
                print("   2. Update existing users to have different countries")
                print("   3. Ensure registration form allows country selection")
            elif len(country_dist) > 1:
                print(f"\nMultiple countries detected ({len(country_dist)} countries)")
                print("   Country distribution should work correctly!")

            # Check for NULL values
            null_countries = [c for c, count in country_dist if c is None]
            if null_countries:
                print(f"\nWARNING: Some users have NULL country")
                print("   These users won't appear in country distribution!")

            print("\n" + "=" * 60)
            print("Diagnostic complete!")
            print("=" * 60 + "\n")

    except Exception as e:
        import traceback
        print(f"\nError: {str(e)}")
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
