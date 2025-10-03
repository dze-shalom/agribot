"""
Add title column to conversations table
Migration script to add title field to existing conversations
"""

from database import db
from sqlalchemy import text

def upgrade():
    """Add title column to conversations table"""
    try:
        # Check if column already exists
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('conversations')
                WHERE name='title'
            """))
            exists = result.scalar() > 0

            if not exists:
                # Add title column
                conn.execute(text("""
                    ALTER TABLE conversations
                    ADD COLUMN title VARCHAR(200) DEFAULT 'New Conversation'
                """))
                conn.commit()
                print("✓ Successfully added 'title' column to conversations table")
            else:
                print("✓ 'title' column already exists in conversations table")

    except Exception as e:
        print(f"✗ Error adding title column: {str(e)}")
        raise

def downgrade():
    """Remove title column from conversations table"""
    try:
        with db.engine.connect() as conn:
            # SQLite doesn't support DROP COLUMN directly
            # Would need to recreate table without the column
            print("⚠ Downgrade not implemented for SQLite")
            print("  To remove title column, backup data and recreate table")

    except Exception as e:
        print(f"✗ Error removing title column: {str(e)}")
        raise

if __name__ == '__main__':
    print("Running migration: Add conversation title column")
    upgrade()
