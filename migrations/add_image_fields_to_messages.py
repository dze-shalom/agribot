"""
Database Migration: Add image fields to messages table
Run this to update your existing database
"""

from database import db
from sqlalchemy import text

def upgrade():
    """Add image-related columns to messages table"""

    migrations = [
        # Add image storage fields
        "ALTER TABLE messages ADD COLUMN IF NOT EXISTS image_path VARCHAR(500)",
        "ALTER TABLE messages ADD COLUMN IF NOT EXISTS image_filename VARCHAR(255)",
        "ALTER TABLE messages ADD COLUMN IF NOT EXISTS image_url VARCHAR(500)",
        "ALTER TABLE messages ADD COLUMN IF NOT EXISTS has_image BOOLEAN DEFAULT FALSE",
        "ALTER TABLE messages ADD COLUMN IF NOT EXISTS image_analysis TEXT",
    ]

    print("Starting database migration: Adding image fields to messages table...")

    for i, migration_sql in enumerate(migrations, 1):
        try:
            db.session.execute(text(migration_sql))
            print(f"✓ Migration {i}/{len(migrations)} successful")
        except Exception as e:
            print(f"✗ Migration {i}/{len(migrations)} failed: {str(e)}")
            # Continue with other migrations even if one fails

    try:
        db.session.commit()
        print("\n✓ All migrations committed successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Migration commit failed: {str(e)}")
        raise

def downgrade():
    """Remove image-related columns from messages table"""

    rollback_migrations = [
        "ALTER TABLE messages DROP COLUMN IF EXISTS image_path",
        "ALTER TABLE messages DROP COLUMN IF EXISTS image_filename",
        "ALTER TABLE messages DROP COLUMN IF EXISTS image_url",
        "ALTER TABLE messages DROP COLUMN IF EXISTS has_image",
        "ALTER TABLE messages DROP COLUMN IF EXISTS image_analysis",
    ]

    print("Rolling back database migration: Removing image fields from messages table...")

    for migration_sql in rollback_migrations:
        try:
            db.session.execute(text(migration_sql))
        except Exception as e:
            print(f"Rollback error: {str(e)}")

    db.session.commit()
    print("✓ Rollback completed!")

if __name__ == "__main__":
    from app.main import create_app

    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("AgriBot Database Migration")
        print("=" * 60)

        choice = input("\nDo you want to (u)pgrade or (d)owngrade? [u/d]: ").lower()

        if choice == 'u':
            upgrade()
        elif choice == 'd':
            downgrade()
        else:
            print("Invalid choice. Exiting.")
