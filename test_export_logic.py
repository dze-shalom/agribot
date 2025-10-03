"""Test the exact export logic with feedback matching"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'agribot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("TESTING EXPORT LOGIC")
print("=" * 60)

# Simulate the export logic
# 1. Pre-load all feedback organized by conversation
cursor.execute("SELECT * FROM feedback")
all_feedback = cursor.fetchall()
print(f"\nLoaded {len(all_feedback)} feedback entries")

feedback_by_conv = {}
for fb in all_feedback:
    fb_id, conversation_id, user_id, helpful, overall_rating, accuracy_rating, completeness_rating, comment, improvement_suggestion, timestamp = fb
    if conversation_id not in feedback_by_conv:
        feedback_by_conv[conversation_id] = []
    feedback_by_conv[conversation_id].append({
        'id': fb_id,
        'helpful': helpful,
        'overall_rating': overall_rating,
        'accuracy_rating': accuracy_rating,
        'completeness_rating': completeness_rating,
        'comment': comment,
        'timestamp': timestamp
    })

print(f"Organized into {len(feedback_by_conv)} unique session IDs")
print(f"Session IDs: {list(feedback_by_conv.keys())[:3]}...")

# 2. Get messages and their conversations
cursor.execute("""
    SELECT m.id, m.conversation_id, m.content, c.session_id
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.id
    WHERE m.message_type = 'user'
    LIMIT 5
""")

messages = cursor.fetchall()
print(f"\nProcessing {len(messages)} sample messages:")

matched_count = 0
for msg in messages:
    msg_id, conv_id, content, session_id = msg

    # Check if conversation has matching feedback
    feedback = None
    if session_id and session_id in feedback_by_conv:
        session_feedbacks = feedback_by_conv[session_id]
        if session_feedbacks:
            feedback = session_feedbacks[0]
            matched_count += 1

    print(f"\nMessage {msg_id}:")
    print(f"  Conv ID: {conv_id}, Session ID: {session_id}")
    print(f"  Content: {content[:40]}...")
    if feedback:
        print(f"  ✓ MATCHED - Helpful: {feedback['helpful']}, Rating: {feedback['overall_rating']}")
    else:
        print(f"  ✗ NO MATCH")

print(f"\n[RESULT] Matched {matched_count}/{len(messages)} messages with feedback")

conn.close()
