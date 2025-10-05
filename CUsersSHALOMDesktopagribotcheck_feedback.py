"""Check feedback data in production database"""
import os
import psycopg2
from datetime import datetime, timedelta

# Render PostgreSQL URL
RENDER_DB = os.getenv('DATABASE_URL', 'postgresql://agribot:EArtWDtDBQc8zgqwKsRQKk70mnVtau9e@dpg-d3g0e46r433s738ql1fg-a.frankfurt-postgres.render.com/agribot_s68e')

print("Checking feedback data in production database...")
print("=" * 60)

# Connect to PostgreSQL
conn = psycopg2.connect(RENDER_DB)
cursor = conn.cursor()

# Check total feedback count
cursor.execute("SELECT COUNT(*) FROM feedback")
total_feedback = cursor.fetchone()[0]
print(f"\nTotal feedback entries: {total_feedback}")

# Check feedback with ratings
cursor.execute("SELECT COUNT(*) FROM feedback WHERE overall_rating IS NOT NULL")
rated_feedback = cursor.fetchone()[0]
print(f"Feedback with ratings: {rated_feedback}")

# Check feedback with helpful flag
cursor.execute("SELECT COUNT(*) FROM feedback WHERE helpful IS NOT NULL")
helpful_feedback = cursor.fetchone()[0]
print(f"Feedback with helpful flag: {helpful_feedback}")

# Check feedback with comments
cursor.execute("SELECT COUNT(*) FROM feedback WHERE comment IS NOT NULL AND comment != ''")
commented_feedback = cursor.fetchone()[0]
print(f"Feedback with comments: {commented_feedback}")

# Check recent feedback (last 30 days)
cutoff_date = datetime.utcnow() - timedelta(days=30)
cursor.execute("SELECT COUNT(*) FROM feedback WHERE timestamp >= %s", (cutoff_date,))
recent_feedback = cursor.fetchone()[0]
print(f"\nFeedback in last 30 days: {recent_feedback}")

# Check conversation_id values
cursor.execute("SELECT id, conversation_id, helpful, overall_rating, accuracy_rating, timestamp FROM feedback ORDER BY timestamp DESC LIMIT 10")
print("\nMost recent feedback entries:")
print("-" * 60)
for row in cursor.fetchall():
    fb_id, conv_id, helpful, overall, accuracy, timestamp = row
    print(f"ID: {fb_id}, ConvID: {conv_id}, Helpful: {helpful}, Rating: {overall}/{accuracy}, Time: {timestamp}")

# Check if conversation_ids are valid (exist in conversations table)
cursor.execute("""
    SELECT
        COUNT(*) as total,
        COUNT(CASE WHEN c.id IS NOT NULL THEN 1 END) as valid,
        COUNT(CASE WHEN c.id IS NULL THEN 1 END) as invalid
    FROM feedback f
    LEFT JOIN conversations c ON f.conversation_id = c.id
""")
valid_check = cursor.fetchone()
print(f"\nConversation ID validity check:")
print(f"  Total feedback: {valid_check[0]}")
print(f"  Valid conversation_id: {valid_check[1]}")
print(f"  Invalid conversation_id: {valid_check[2]}")

# Check messages for confidence scores
cursor.execute("""
    SELECT COUNT(*) FROM messages
    WHERE message_type = 'bot'
    AND confidence_score IS NOT NULL
    AND timestamp >= %s
""", (cutoff_date,))
confidence_messages = cursor.fetchone()[0]
print(f"\nBot messages with confidence scores (last 30 days): {confidence_messages}")

cursor.execute("""
    SELECT AVG(confidence_score) FROM messages
    WHERE message_type = 'bot'
    AND confidence_score IS NOT NULL
    AND timestamp >= %s
""", (cutoff_date,))
avg_confidence = cursor.fetchone()[0]
print(f"Average confidence score: {avg_confidence}")
if avg_confidence:
    print(f"AI Accuracy would be: {round(avg_confidence * 100, 1)}%")

cursor.close()
conn.close()

print("=" * 60)
print("Check complete!")
