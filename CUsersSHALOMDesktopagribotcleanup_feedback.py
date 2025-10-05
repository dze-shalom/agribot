"""Clean up invalid feedback entries with string conversation_ids"""
import os
import psycopg2

# Render PostgreSQL URL
RENDER_DB = os.getenv('DATABASE_URL', 'postgresql://agribot:EArtWDtDBQc8zgqwKsRQKk70mnVtau9e@dpg-d3g0e46r433s738ql1fg-a.frankfurt-postgres.render.com/agribot_s68e')

print("Cleaning up invalid feedback entries...")
print("=" * 60)

# Connect to PostgreSQL
conn = psycopg2.connect(RENDER_DB)
cursor = conn.cursor()

# First, let's see what we're dealing with
cursor.execute("SELECT COUNT(*) FROM feedback")
total_before = cursor.fetchone()[0]
print(f"Total feedback entries before cleanup: {total_before}")

# Check how many have string session IDs (start with 'session_')
# In PostgreSQL, we need to cast conversation_id to text to check if it starts with 'session_'
cursor.execute("""
    SELECT COUNT(*) FROM feedback
    WHERE CAST(conversation_id AS TEXT) LIKE 'session_%'
""")
invalid_count = cursor.fetchone()[0]
print(f"Invalid feedback entries (string session IDs): {invalid_count}")

# Check how many have valid integer conversation_ids that match actual conversations
cursor.execute("""
    SELECT COUNT(*) FROM feedback f
    INNER JOIN conversations c ON f.conversation_id = c.id
""")
valid_count = cursor.fetchone()[0]
print(f"Valid feedback entries (matching conversations): {valid_count}")

# Show a sample of invalid entries before deletion
print("\nSample of invalid entries to be deleted:")
cursor.execute("""
    SELECT id, conversation_id, user_id, helpful, overall_rating, comment
    FROM feedback
    WHERE CAST(conversation_id AS TEXT) LIKE 'session_%'
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, ConvID: {row[1]}, User: {row[2]}, Helpful: {row[3]}, Rating: {row[4]}")

# Delete invalid feedback entries
print("\nDeleting invalid feedback entries...")
cursor.execute("""
    DELETE FROM feedback
    WHERE CAST(conversation_id AS TEXT) LIKE 'session_%'
""")
deleted_count = cursor.rowcount
print(f"Deleted {deleted_count} invalid feedback entries")

# Verify cleanup
cursor.execute("SELECT COUNT(*) FROM feedback")
total_after = cursor.fetchone()[0]
print(f"\nTotal feedback entries after cleanup: {total_after}")

# Commit changes
conn.commit()
cursor.close()
conn.close()

print("=" * 60)
print("Cleanup complete!")
print(f"Summary: Removed {deleted_count} invalid entries, {total_after} valid entries remain")
