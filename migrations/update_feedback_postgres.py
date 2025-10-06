"""
Migration: Update feedback.conversation_id to support string session IDs (PostgreSQL)
Date: 2025-10-06

For use on Render/production PostgreSQL databases
"""

import os
import sys

def migrate():
    """Update feedback table to support string conversation IDs on PostgreSQL"""

    try:
        # Import after path setup
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

        from app.main import create_app
        from database import db

        app = create_app()

        with app.app_context():
            print("Starting PostgreSQL migration...")

            # Check if migration is needed
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)

            # Get current column type
            columns = inspector.get_columns('feedback')
            conv_id_col = next((col for col in columns if col['name'] == 'conversation_id'), None)

            if not conv_id_col:
                print("Error: conversation_id column not found!")
                return False

            current_type = str(conv_id_col['type'])
            print(f"Current conversation_id type: {current_type}")

            # Check if already migrated
            if 'VARCHAR' in current_type.upper() or 'TEXT' in current_type.upper():
                print("Migration already applied - conversation_id is already a string type")
                return True

            # Count existing feedback
            result = db.session.execute(text("SELECT COUNT(*) FROM feedback"))
            count = result.scalar()
            print(f"Found {count} feedback records")

            # Sample some data
            if count > 0:
                result = db.session.execute(text("SELECT id, conversation_id FROM feedback LIMIT 5"))
                print("\nSample conversation_ids:")
                for row in result:
                    print(f"  ID {row[0]}: {row[1]}")

            print("\nApplying migration...")

            # PostgreSQL approach: ALTER COLUMN type
            try:
                # First, drop the foreign key constraint if it exists
                db.session.execute(text("""
                    ALTER TABLE feedback
                    DROP CONSTRAINT IF EXISTS feedback_conversation_id_fkey
                """))

                # Change column type to VARCHAR
                db.session.execute(text("""
                    ALTER TABLE feedback
                    ALTER COLUMN conversation_id TYPE VARCHAR(100)
                    USING conversation_id::VARCHAR
                """))

                db.session.commit()
                print("Migration completed successfully!")

                # Verify
                inspector = inspect(db.engine)
                columns = inspector.get_columns('feedback')
                conv_id_col = next((col for col in columns if col['name'] == 'conversation_id'), None)
                print(f"New conversation_id type: {conv_id_col['type']}")

                # Verify record count
                result = db.session.execute(text("SELECT COUNT(*) FROM feedback"))
                new_count = result.scalar()
                print(f"Verified {new_count} feedback records after migration")

                if new_count != count:
                    print(f"WARNING: Record count changed from {count} to {new_count}")

                return True

            except Exception as e:
                print(f"Error during ALTER: {str(e)}")
                db.session.rollback()
                raise

    except Exception as e:
        print(f"[ERROR] Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
