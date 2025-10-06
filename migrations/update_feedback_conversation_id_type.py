"""
Change feedback.conversation_id from INTEGER to VARCHAR
Migration to support session IDs like 'session_1234' in addition to integer IDs
"""

from database import db
from sqlalchemy import text, inspect

def upgrade():
    """Change conversation_id column type to VARCHAR"""
    try:
        engine = db.engine
        engine_name = engine.name

        print(f"Database engine: {engine_name}")

        # Check current column type
        inspector = inspect(engine)
        columns = inspector.get_columns('feedback')
        conv_col = next((c for c in columns if c['name'] == 'conversation_id'), None)

        if not conv_col:
            print("✗ conversation_id column not found!")
            return

        current_type = str(conv_col['type']).upper()
        print(f"Current type: {current_type}")

        # Check if already migrated
        if 'VARCHAR' in current_type or 'TEXT' in current_type or 'CHAR' in current_type:
            print("✓ conversation_id is already VARCHAR - migration not needed")
            return

        with engine.connect() as conn:
            # Count records before migration
            result = conn.execute(text("SELECT COUNT(*) FROM feedback"))
            count_before = result.scalar()
            print(f"Feedback records before migration: {count_before}")

            if engine_name == 'postgresql':
                print("\nMigrating PostgreSQL database...")

                # Drop foreign key constraint
                conn.execute(text("""
                    ALTER TABLE feedback
                    DROP CONSTRAINT IF EXISTS feedback_conversation_id_fkey
                """))
                print("  ✓ Dropped FK constraint")

                # Change column type
                conn.execute(text("""
                    ALTER TABLE feedback
                    ALTER COLUMN conversation_id TYPE VARCHAR(100)
                    USING conversation_id::VARCHAR
                """))
                print("  ✓ Changed to VARCHAR(100)")

                conn.commit()

            elif engine_name == 'sqlite':
                print("\nMigrating SQLite database...")

                # SQLite requires table recreation
                conn.execute(text("""
                    CREATE TABLE feedback_new (
                        id INTEGER PRIMARY KEY,
                        conversation_id VARCHAR(100) NOT NULL,
                        user_id INTEGER NOT NULL,
                        helpful BOOLEAN,
                        overall_rating INTEGER,
                        accuracy_rating INTEGER,
                        completeness_rating INTEGER,
                        comment TEXT,
                        improvement_suggestion TEXT,
                        timestamp DATETIME,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """))
                print("  ✓ Created new table")

                # Copy data
                conn.execute(text("""
                    INSERT INTO feedback_new
                    SELECT id, CAST(conversation_id AS VARCHAR), user_id, helpful,
                           overall_rating, accuracy_rating, completeness_rating,
                           comment, improvement_suggestion, timestamp
                    FROM feedback
                """))
                print("  ✓ Copied data")

                # Replace table
                conn.execute(text("DROP TABLE feedback"))
                conn.execute(text("ALTER TABLE feedback_new RENAME TO feedback"))
                print("  ✓ Replaced table")

                conn.commit()

            # Verify
            result = conn.execute(text("SELECT COUNT(*) FROM feedback"))
            count_after = result.scalar()
            print(f"\nFeedback records after migration: {count_after}")

            if count_before == count_after:
                print("✓ Migration successful - all records preserved!")
            else:
                print(f"⚠ WARNING: Record count mismatch ({count_before} -> {count_after})")

    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def downgrade():
    """Revert conversation_id back to INTEGER (not recommended)"""
    print("⚠ Downgrade not implemented")
    print("  Reverting would lose session ID data")
    print("  If needed, restore from backup")

if __name__ == '__main__':
    print("=" * 60)
    print("Migration: Update feedback.conversation_id to VARCHAR")
    print("=" * 60)
    upgrade()
    print("=" * 60)
