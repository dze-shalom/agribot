"""
Backfill session_id in conversations table based on feedback data
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'agribot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("=" * 60)
    print("BACKFILLING SESSION IDs")
    print("=" * 60)

    # Get all feedback with session IDs and user IDs
    cursor.execute("""
        SELECT DISTINCT conversation_id, user_id, timestamp
        FROM feedback
        WHERE conversation_id LIKE 'session_%'
        ORDER BY timestamp ASC
    """)
    feedbacks = cursor.fetchall()

    print(f"\nFound {len(feedbacks)} unique session IDs in feedback")

    updated_count = 0
    for fb in feedbacks:
        session_id = fb[0]
        user_id = fb[1]
        fb_timestamp = fb[2]

        # Find conversation for this user closest in time to feedback
        # (feedback is submitted after conversation starts)
        cursor.execute("""
            SELECT id, start_time
            FROM conversations
            WHERE user_id = ?
              AND session_id IS NULL
              AND start_time <= ?
            ORDER BY start_time DESC
            LIMIT 1
        """, (user_id, fb_timestamp))

        conv = cursor.fetchone()
        if conv:
            conv_id = conv[0]
            # Update conversation with session_id
            cursor.execute("""
                UPDATE conversations
                SET session_id = ?
                WHERE id = ?
            """, (session_id, conv_id))
            updated_count += 1
            print(f"  Updated conversation {conv_id} -> {session_id}")

    conn.commit()
    print(f"\n[SUCCESS] Updated {updated_count} conversations with session IDs")

    # Verify matches
    cursor.execute("""
        SELECT COUNT(*)
        FROM feedback f
        JOIN conversations c ON f.conversation_id = c.session_id
    """)
    matched = cursor.fetchone()[0]
    print(f"[VERIFY] {matched} feedbacks now match conversations")

except Exception as e:
    print(f"[ERROR] {e}")
    conn.rollback()
finally:
    conn.close()
