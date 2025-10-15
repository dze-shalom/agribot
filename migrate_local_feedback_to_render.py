"""
Migrate feedback from local SQLite to Render PostgreSQL
This will copy your 28 local feedback records to production
"""
import sqlite3
import psycopg2

# Local SQLite
LOCAL_DB = "instance/agribot.db"

# Render PostgreSQL
RENDER_DB = "postgresql://agribot:EArtWDtDBQc8zgqwKsRQKk70mnVtau9e@dpg-d3g0e46r433s738ql1fg-a.frankfurt-postgres.render.com/agribot_s68e"

print("Migrating feedback from local to Render...")
print("="*60)

try:
    # Connect to local SQLite
    sqlite_conn = sqlite3.connect(LOCAL_DB)
    sqlite_cursor = sqlite_conn.cursor()

    # Get all feedback
    sqlite_cursor.execute("SELECT * FROM feedback")
    local_feedbacks = sqlite_cursor.fetchall()
    print(f"Found {len(local_feedbacks)} feedback records in local database")

    if len(local_feedbacks) == 0:
        print("No feedback to migrate!")
        exit(0)

    # Connect to Render PostgreSQL
    pg_conn = psycopg2.connect(RENDER_DB)
    pg_cursor = pg_conn.cursor()

    # Check current count on Render
    pg_cursor.execute("SELECT COUNT(*) FROM feedback")
    render_count_before = pg_cursor.fetchone()[0]
    print(f"Current feedback on Render: {render_count_before}")

    # Sample local feedback
    print("\nSample local feedback:")
    for i, fb in enumerate(local_feedbacks[:3]):
        print(f"  {i+1}. Conv: {fb[1]}, Helpful: {fb[3]}, Rating: {fb[4]}")

    # Migrate each feedback
    migrated = 0
    skipped = 0

    for fb in local_feedbacks:
        # Unpack: id, conversation_id, user_id, helpful, overall_rating,
        #         accuracy_rating, completeness_rating, comment, improvement_suggestion, timestamp
        (fb_id, conversation_id, user_id, helpful, overall_rating,
         accuracy_rating, completeness_rating, comment, improvement_suggestion, timestamp) = fb

        try:
            # Check if feedback already exists (by conversation_id and user_id)
            pg_cursor.execute(
                "SELECT id FROM feedback WHERE conversation_id = %s AND user_id = %s",
                (str(conversation_id), user_id)
            )
            existing = pg_cursor.fetchone()

            if existing:
                skipped += 1
                continue

            # Insert feedback (let PostgreSQL auto-generate ID)
            pg_cursor.execute("""
                INSERT INTO feedback
                (conversation_id, user_id, helpful, overall_rating, accuracy_rating,
                 completeness_rating, comment, improvement_suggestion, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (str(conversation_id), user_id, helpful, overall_rating, accuracy_rating,
                  completeness_rating, comment, improvement_suggestion, timestamp))

            migrated += 1

        except Exception as e:
            print(f"  [ERROR] Failed to migrate feedback {fb_id}: {str(e)}")

    # Commit changes
    pg_conn.commit()

    # Verify
    pg_cursor.execute("SELECT COUNT(*) FROM feedback")
    render_count_after = pg_cursor.fetchone()[0]

    print("\n" + "="*60)
    print(f"Migration Complete!")
    print(f"  Migrated: {migrated} feedback records")
    print(f"  Skipped:  {skipped} (already existed)")
    print(f"  Total on Render: {render_count_after} (was {render_count_before})")
    print("="*60)

    # Close connections
    sqlite_conn.close()
    pg_cursor.close()
    pg_conn.close()

except Exception as e:
    print(f"\n[ERROR] Migration failed: {str(e)}")
    import traceback
    traceback.print_exc()
