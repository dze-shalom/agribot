"""Check if feedback data exists in database"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'agribot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check feedback table
print("=" * 60)
print("FEEDBACK TABLE")
print("=" * 60)
cursor.execute("SELECT * FROM feedback")
feedbacks = cursor.fetchall()
print(f"Total feedback entries: {len(feedbacks)}")

if feedbacks:
    # Get column names
    cursor.execute("PRAGMA table_info(feedback)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\nColumns: {', '.join(columns)}")

    print("\nFirst 5 feedback entries:")
    for i, feedback in enumerate(feedbacks[:5], 1):
        print(f"\n{i}. Feedback ID: {feedback[0]}")
        for col_name, value in zip(columns, feedback):
            print(f"   {col_name}: {value}")
else:
    print("\nNo feedback data found!")

# Check messages table for context
print("\n" + "=" * 60)
print("MESSAGES TABLE (for context)")
print("=" * 60)
cursor.execute("SELECT COUNT(*) FROM messages")
msg_count = cursor.fetchone()[0]
print(f"Total messages: {msg_count}")

cursor.execute("SELECT COUNT(*) FROM messages WHERE message_type='user'")
user_msg_count = cursor.fetchone()[0]
print(f"User messages: {user_msg_count}")

cursor.execute("SELECT COUNT(*) FROM messages WHERE message_type='bot'")
bot_msg_count = cursor.fetchone()[0]
print(f"Bot messages: {bot_msg_count}")

# Check conversations
print("\n" + "=" * 60)
print("CONVERSATIONS TABLE")
print("=" * 60)
cursor.execute("SELECT COUNT(*) FROM conversations")
conv_count = cursor.fetchone()[0]
print(f"Total conversations: {conv_count}")

conn.close()
