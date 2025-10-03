"""Debug feedback matching"""
import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'agribot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("DEBUG: Feedback Matching")
print("=" * 60)

# Get sample message
cursor.execute("""
    SELECT m.id, m.conversation_id, m.timestamp, c.user_id as conv_user_id
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.id
    WHERE m.message_type = 'user'
    LIMIT 1
""")
msg = cursor.fetchone()
print(f"\nSample Message:")
print(f"  Message ID: {msg[0]}")
print(f"  Conversation ID: {msg[1]}")
print(f"  Message timestamp: {msg[2]}")
print(f"  Conversation user_id: {msg[3]}")

# Get feedback for that user
cursor.execute("""
    SELECT id, conversation_id, user_id, timestamp, helpful, overall_rating
    FROM feedback
    WHERE user_id = ?
""", (msg[3],))
feedbacks = cursor.fetchall()

print(f"\nFeedback for user {msg[3]}:")
for fb in feedbacks:
    print(f"  Feedback ID: {fb[0]}")
    print(f"    Session ID: {fb[1]}")
    print(f"    User ID: {fb[2]}")
    print(f"    Timestamp: {fb[3]}")
    print(f"    Helpful: {fb[4]}, Rating: {fb[5]}")

    # Calculate time difference
    if fb[3] and msg[2]:
        fb_time = datetime.fromisoformat(fb[3])
        msg_time = datetime.fromisoformat(msg[2])
        time_diff = (fb_time - msg_time).total_seconds()
        print(f"    Time diff from message: {time_diff} seconds ({time_diff/60:.1f} minutes)")
        print(f"    Within 1 hour? {0 <= time_diff <= 3600}")
    print()

conn.close()
