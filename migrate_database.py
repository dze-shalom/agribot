"""
Database Migration Script
Adds 'country' column to users table and updates existing users
"""

import sqlite3
import os

def migrate_database():
    """Add country column to users table"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'agribot.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    print(f"Migrating database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if country column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'country' not in columns:
            print("Adding 'country' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN country VARCHAR(100) DEFAULT 'Cameroon'")

            # Update all existing users to have country = 'Cameroon'
            cursor.execute("UPDATE users SET country = 'Cameroon' WHERE country IS NULL")

            conn.commit()
            print("[OK] Added 'country' column successfully")
        else:
            print("[OK] 'country' column already exists")

        # Show current user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"[OK] Database has {user_count} users")

        print("\n[OK] Migration completed successfully!")

    except Exception as e:
        print(f"[ERROR] Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
