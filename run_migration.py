"""
Run Database Migration
Standalone script to add image fields to messages table
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import create_app
from database import db
from sqlalchemy import text, inspect

def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def run_migration():
    """Add image-related columns to messages table"""

    app = create_app()

    with app.app_context():
        # List of columns to add
        columns_to_add = [
            ('image_path', 'VARCHAR(500)'),
            ('image_filename', 'VARCHAR(255)'),
            ('image_url', 'VARCHAR(500)'),
            ('has_image', 'BOOLEAN DEFAULT FALSE'),
            ('image_analysis', 'TEXT'),
        ]

        print("=" * 60)
        print("AgriBot Database Migration")
        print("Adding image fields to messages table")
        print("=" * 60)
        print()

        success_count = 0
        skip_count = 0
        error_count = 0

        for column_name, column_def in columns_to_add:
            try:
                if column_exists('messages', column_name):
                    print(f"[SKIP] Column '{column_name}' already exists")
                    skip_count += 1
                else:
                    migration_sql = f"ALTER TABLE messages ADD COLUMN {column_name} {column_def}"
                    db.session.execute(text(migration_sql))
                    print(f"[OK] Added column '{column_name}'")
                    success_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to add '{column_name}': {str(e)}")
                error_count += 1
                # Continue with other migrations even if one fails

        try:
            db.session.commit()
            print()
            print("=" * 60)
            print(f"Migration completed!")
            print(f"Added: {success_count} | Skipped: {skip_count} | Errors: {error_count}")
            print("=" * 60)
            print()
            if success_count > 0 or skip_count > 0:
                print("Image storage is now enabled. You can:")
                print("- Upload images with messages using /chat/message-with-image endpoint")
                print("- Export images using /api/auth/admin/analytics/export/messages-with-images")
            print()
        except Exception as e:
            db.session.rollback()
            print()
            print(f"[ERROR] Migration commit failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migration()
