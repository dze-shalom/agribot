"""
Fix feedback matching by adding session_id to conversations table
and creating a mapping
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'agribot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if session_id column exists in conversations
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'session_id' not in columns:
        print("Adding 'session_id' column to conversations table...")
        cursor.execute("ALTER TABLE conversations ADD COLUMN session_id VARCHAR(100)")
        conn.commit()
        print("[OK] Added 'session_id' column")
    else:
        print("[OK] 'session_id' column already exists")

    print("\n[INFO] Feedback entries use session IDs like 'session_XXXXX'")
    print("[INFO] But conversations and messages use integer IDs")
    print("[INFO] The chatbot needs to be updated to store session_id when creating conversations")

    print("\n[SOLUTION] The best fix is:")
    print("1. Update chatbot to save session_id when creating conversations")
    print("2. Then feedback can be matched properly")

    # Show current mismatch
    cursor.execute("SELECT COUNT(*) FROM feedback")
    fb_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM feedback f
        LEFT JOIN conversations c ON f.conversation_id = CAST(c.id AS TEXT)
        WHERE c.id IS NOT NULL
    """)
    matched = cursor.fetchone()[0]

    print(f"\n[STATUS] Total feedback: {fb_count}")
    print(f"[STATUS] Matched with conversations: {matched}")
    print(f"[STATUS] Unmatched: {fb_count - matched}")

except Exception as e:
    print(f"[ERROR] {e}")
    conn.rollback()
finally:
    conn.close()
