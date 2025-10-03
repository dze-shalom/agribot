"""Check conversation IDs in messages vs feedback"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'agribot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("MESSAGES - Sample conversation_id values")
print("=" * 60)
cursor.execute("SELECT DISTINCT conversation_id FROM messages LIMIT 10")
msg_conv_ids = cursor.fetchall()
for cid in msg_conv_ids:
    print(f"  {cid[0]} (type: {type(cid[0]).__name__})")

print("\n" + "=" * 60)
print("FEEDBACK - Sample conversation_id values")
print("=" * 60)
cursor.execute("SELECT conversation_id FROM feedback LIMIT 10")
feedback_conv_ids = cursor.fetchall()
for cid in feedback_conv_ids:
    print(f"  {cid[0]} (type: {type(cid[0]).__name__})")

print("\n" + "=" * 60)
print("CONVERSATIONS - Sample id values")
print("=" * 60)
cursor.execute("SELECT id FROM conversations LIMIT 10")
conversations_ids = cursor.fetchall()
for cid in conversations_ids:
    print(f"  {cid[0]} (type: {type(cid[0]).__name__})")

# Check if any feedback conversation_ids match message conversation_ids
print("\n" + "=" * 60)
print("MATCHING CHECK")
print("=" * 60)
cursor.execute("""
    SELECT COUNT(*)
    FROM feedback f
    JOIN messages m ON f.conversation_id = m.conversation_id
""")
matches = cursor.fetchone()[0]
print(f"Feedback entries that match message conversation_ids: {matches}")

conn.close()
