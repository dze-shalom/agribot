"""
Migration: Update feedback.conversation_id to support string session IDs
Date: 2025-10-06
"""

import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def migrate():
    """Update feedback table to support string conversation IDs"""

    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'agribot.db')

    print(f"Migrating database: {db_path}")

    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check current schema
        cursor.execute("PRAGMA table_info(feedback)")
        columns = cursor.fetchall()
        print("\nCurrent feedback table schema:")
        for col in columns:
            print(f"  {col[1]} {col[2]}")

        # Get current data
        cursor.execute("SELECT COUNT(*) FROM feedback")
        count = cursor.fetchone()[0]
        print(f"\nTotal feedback records: {count}")

        # Sample some data to see types
        cursor.execute("SELECT id, conversation_id, typeof(conversation_id) FROM feedback LIMIT 5")
        samples = cursor.fetchall()
        print("\nSample conversation_id types:")
        for row in samples:
            print(f"  ID {row[0]}: {row[1]} (type: {row[2]})")

        # Create new table with STRING conversation_id
        print("\nCreating new feedback table with STRING conversation_id...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_new (
                id INTEGER PRIMARY KEY,
                conversation_id TEXT NOT NULL,
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
        """)

        # Copy data from old table to new table, converting all conversation_ids to strings
        print("Copying data to new table...")
        cursor.execute("""
            INSERT INTO feedback_new
            SELECT id, CAST(conversation_id AS TEXT), user_id, helpful, overall_rating,
                   accuracy_rating, completeness_rating, comment, improvement_suggestion, timestamp
            FROM feedback
        """)

        # Verify data was copied
        cursor.execute("SELECT COUNT(*) FROM feedback_new")
        new_count = cursor.fetchone()[0]
        print(f"Copied {new_count} records to new table")

        if new_count != count:
            print(f"WARNING: Record count mismatch! Original: {count}, New: {new_count}")
            conn.rollback()
            return False

        # Drop old table and rename new table
        print("Replacing old table with new table...")
        cursor.execute("DROP TABLE feedback")
        cursor.execute("ALTER TABLE feedback_new RENAME TO feedback")

        # Verify final schema
        cursor.execute("PRAGMA table_info(feedback)")
        new_columns = cursor.fetchall()
        print("\nNew feedback table schema:")
        for col in new_columns:
            print(f"  {col[1]} {col[2]}")

        # Sample the migrated data
        cursor.execute("SELECT id, conversation_id, typeof(conversation_id) FROM feedback LIMIT 5")
        new_samples = cursor.fetchall()
        print("\nSample conversation_id after migration:")
        for row in new_samples:
            print(f"  ID {row[0]}: {row[1]} (type: {row[2]})")

        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")

        conn.close()
        return True

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
