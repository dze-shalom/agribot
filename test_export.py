"""Test ML dataset export to see what's being returned"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'agribot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("TESTING ML DATASET EXPORT")
print("=" * 60)

# Check messages
cursor.execute("SELECT COUNT(*) FROM messages WHERE message_type='user'")
user_count = cursor.fetchone()[0]
print(f"\nUser messages: {user_count}")

# Sample user messages
cursor.execute("""
    SELECT m.id, m.conversation_id, m.content, m.timestamp
    FROM messages m
    WHERE m.message_type = 'user'
    LIMIT 5
""")
print("\nSample user messages:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Conv: {row[1]}, Content: {row[2][:50]}..., Time: {row[3]}")

# Check if conversations have data
cursor.execute("SELECT id, session_id, user_id FROM conversations LIMIT 5")
print("\nSample conversations:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Session: {row[1]}, User: {row[2]}")

# Check feedback
cursor.execute("SELECT id, conversation_id, helpful, overall_rating FROM feedback LIMIT 5")
print("\nSample feedback:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Session: {row[1]}, Helpful: {row[2]}, Rating: {row[3]}")

conn.close()
