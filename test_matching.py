"""Test if feedback matching is working"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'agribot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("TESTING FEEDBACK MATCHING")
print("=" * 60)

# Get sample message with its conversation
cursor.execute("""
    SELECT m.id, m.conversation_id, c.session_id, c.user_id, m.content
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.id
    WHERE m.message_type = 'user'
      AND c.session_id IS NOT NULL
    LIMIT 1
""")
msg = cursor.fetchone()

if msg:
    print(f"\nSample Message:")
    print(f"  Message ID: {msg[0]}")
    print(f"  Conversation ID: {msg[1]}")
    print(f"  Session ID: {msg[2]}")
    print(f"  User ID: {msg[3]}")
    print(f"  Content: {msg[4][:50]}...")

    # Check if there's matching feedback
    cursor.execute("""
        SELECT id, helpful, overall_rating, accuracy_rating, completeness_rating, comment
        FROM feedback
        WHERE conversation_id = ?
    """, (msg[2],))

    fb = cursor.fetchone()
    if fb:
        print(f"\n[OK] MATCHED FEEDBACK:")
        print(f"  Feedback ID: {fb[0]}")
        print(f"  Helpful: {fb[1]}")
        print(f"  Overall Rating: {fb[2]}")
        print(f"  Accuracy Rating: {fb[3]}")
        print(f"  Completeness Rating: {fb[4]}")
        print(f"  Comment: {fb[5]}")
    else:
        print(f"\n[FAIL] NO FEEDBACK MATCH for session_id: {msg[2]}")
else:
    print("\n[FAIL] No messages with session_id found")

# Count total matches
cursor.execute("""
    SELECT COUNT(DISTINCT m.id)
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.id
    JOIN feedback f ON c.session_id = f.conversation_id
    WHERE m.message_type = 'user'
""")
match_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM messages WHERE message_type = 'user'")
total_messages = cursor.fetchone()[0]

print(f"\n[SUMMARY]")
print(f"  Total user messages: {total_messages}")
print(f"  Messages with feedback: {match_count}")
print(f"  Match rate: {match_count}/{total_messages} ({100*match_count/total_messages if total_messages > 0 else 0:.1f}%)")

conn.close()
