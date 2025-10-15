"""
Migration: Change feedback.conversation_id from INTEGER to VARCHAR
Run this on Render AFTER deploying the model change
"""
import os
import sys

def migrate():
    """Migrate feedback.conversation_id to VARCHAR on PostgreSQL"""
    try:
        # Import Flask app
        from app.main import create_app
        from database import db
        from sqlalchemy import text, inspect

        app = create_app()

        with app.app_context():
            print("Checking database type...")

            # Check if we're using PostgreSQL or SQLite
            engine_name = db.engine.name
            print(f"Database engine: {engine_name}")

            # Get current schema
            inspector = inspect(db.engine)
            columns = inspector.get_columns('feedback')
            conv_col = next((c for c in columns if c['name'] == 'conversation_id'), None)

            if not conv_col:
                print("ERROR: conversation_id column not found!")
                return False

            current_type = str(conv_col['type']).upper()
            print(f"Current conversation_id type: {current_type}")

            # Check if already migrated
            if 'VARCHAR' in current_type or 'TEXT' in current_type or 'CHAR' in current_type:
                print("✓ Already migrated - conversation_id is already a string type")
                return True

            # Count existing feedback
            result = db.session.execute(text("SELECT COUNT(*) FROM feedback"))
            count = result.scalar()
            print(f"Found {count} feedback records")

            if engine_name == 'postgresql':
                print("\nMigrating PostgreSQL database...")

                # Drop foreign key constraint first
                try:
                    db.session.execute(text("""
                        ALTER TABLE feedback
                        DROP CONSTRAINT IF EXISTS feedback_conversation_id_fkey
                    """))
                    print("✓ Dropped foreign key constraint")
                except Exception as e:
                    print(f"Note: {e}")

                # Change column type
                db.session.execute(text("""
                    ALTER TABLE feedback
                    ALTER COLUMN conversation_id TYPE VARCHAR(100)
                    USING conversation_id::VARCHAR
                """))
                print("✓ Changed column type to VARCHAR(100)")

                db.session.commit()

            elif engine_name == 'sqlite':
                print("\nSQLite detected - no migration needed")
                print("SQLite already supports strings in INTEGER columns")
                return True

            # Verify
            inspector = inspect(db.engine)
            columns = inspector.get_columns('feedback')
            conv_col = next((c for c in columns if c['name'] == 'conversation_id'), None)
            new_type = str(conv_col['type']).upper()
            print(f"\n✓ New conversation_id type: {new_type}")

            # Verify count
            result = db.session.execute(text("SELECT COUNT(*) FROM feedback"))
            new_count = result.scalar()
            print(f"✓ Verified {new_count} feedback records preserved")

            if new_count != count:
                print(f"WARNING: Record count mismatch! Was {count}, now {new_count}")
                return False

            print("\n✓✓✓ Migration completed successfully! ✓✓✓")
            return True

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Feedback Column Migration")
    print("=" * 60)
    success = migrate()
    print("=" * 60)
    sys.exit(0 if success else 1)
