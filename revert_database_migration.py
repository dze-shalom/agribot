"""
REVERT: Change feedback.conversation_id back to INTEGER on Render
"""
import psycopg2
import sys

# Render PostgreSQL URL
RENDER_DB = "postgresql://agribot:EArtWDtDBQc8zgqwKsRQKk70mnVtau9e@dpg-d3g0e46r433s738ql1fg-a.frankfurt-postgres.render.com/agribot_s68e"

print("REVERTING feedback.conversation_id back to INTEGER...")
print("="*60)

try:
    conn = psycopg2.connect(RENDER_DB)
    cursor = conn.cursor()

    # Check current state
    cursor.execute("""
        SELECT data_type FROM information_schema.columns
        WHERE table_name = 'feedback' AND column_name = 'conversation_id'
    """)
    current_type = cursor.fetchone()[0]
    print(f"Current type: {current_type}")

    if 'int' in current_type.lower():
        print("[OK] Already INTEGER - revert not needed!")
        sys.exit(0)

    # Count records
    cursor.execute("SELECT COUNT(*) FROM feedback")
    count = cursor.fetchone()[0]
    print(f"Feedback records: {count}")

    # Change back to INTEGER
    print("\nChanging column back to INTEGER...")
    cursor.execute("""
        ALTER TABLE feedback
        ALTER COLUMN conversation_id TYPE INTEGER
        USING CASE
            WHEN conversation_id ~ '^[0-9]+$' THEN conversation_id::INTEGER
            ELSE NULL
        END
    """)
    print("  [OK] Column changed to INTEGER")

    # Restore FK constraint
    print("\nRestoring foreign key constraint...")
    cursor.execute("""
        ALTER TABLE feedback
        ADD CONSTRAINT feedback_conversation_id_fkey
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    """)
    print("  [OK] FK constraint restored")

    conn.commit()

    # Verify
    cursor.execute("""
        SELECT data_type FROM information_schema.columns
        WHERE table_name = 'feedback' AND column_name = 'conversation_id'
    """)
    new_type = cursor.fetchone()[0]
    print(f"\n[OK] New type: {new_type}")

    cursor.execute("SELECT COUNT(*) FROM feedback")
    new_count = cursor.fetchone()[0]
    print(f"[OK] Records after revert: {new_count}")

    print("\n" + "="*60)
    print("SUCCESS! Database reverted to original state")
    print("="*60)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n[ERROR] Revert failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
