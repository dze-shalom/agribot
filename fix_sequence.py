"""Fix PostgreSQL sequence for conversations table after migration"""
import os
import psycopg2

# Render PostgreSQL URL
RENDER_DB = os.getenv('DATABASE_URL', 'postgresql://agribot:EArtWDtDBQc8zgqwKsRQKk70mnVtau9e@dpg-d3g0e46r433s738ql1fg-a.frankfurt-postgres.render.com/agribot_s68e')

print("Fixing PostgreSQL sequences after migration...")
print("=" * 60)

# Connect to PostgreSQL
conn = psycopg2.connect(RENDER_DB)
cursor = conn.cursor()

# Fix conversations table sequence
cursor.execute("SELECT MAX(id) FROM conversations")
max_id = cursor.fetchone()[0]

if max_id:
    new_seq_value = max_id + 1
    cursor.execute(f"SELECT setval('conversations_id_seq', {new_seq_value}, false)")
    print(f"[OK] conversations_id_seq reset to {new_seq_value}")
else:
    print("[INFO] conversations table is empty, no sequence fix needed")

# Fix messages table sequence (might have same issue)
cursor.execute("SELECT MAX(id) FROM messages")
max_id = cursor.fetchone()[0]

if max_id:
    new_seq_value = max_id + 1
    cursor.execute(f"SELECT setval('messages_id_seq', {new_seq_value}, false)")
    print(f"[OK] messages_id_seq reset to {new_seq_value}")
else:
    print("[INFO] messages table is empty, no sequence fix needed")

# Commit and close
conn.commit()
cursor.close()
conn.close()

print("=" * 60)
print("Sequence fix complete!")
