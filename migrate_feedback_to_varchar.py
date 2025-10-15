"""
Simple migration - Change feedback.conversation_id to VARCHAR on Render PostgreSQL
Run this ONCE on your local machine to update the production database
"""
import psycopg2
import sys

# Render PostgreSQL URL
RENDER_DB = "postgresql://agribot:EArtWDtDBQc8zgqwKsRQKk70mnVtau9e@dpg-d3g0e46r433s738ql1fg-a.frankfurt-postgres.render.com/agribot_s68e"

print("Migrating feedback.conversation_id to VARCHAR on Render...")
print("="*60)

try:
    # Connect to Render PostgreSQL
    conn = psycopg2.connect(RENDER_DB)
    cursor = conn.cursor()

    # Check current state
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'feedback' AND column_name = 'conversation_id'
    """)
    result = cursor.fetchone()

    if result:
        print(f"Current type: {result[1]}")

        if 'varchar' in result[1].lower() or 'char' in result[1].lower():
            print("[OK] Already VARCHAR - migration not needed!")
            sys.exit(0)
    else:
        print("[ERROR] feedback table or conversation_id column not found!")
        sys.exit(1)

    # Count existing feedback
    cursor.execute("SELECT COUNT(*) FROM feedback")
    count_before = cursor.fetchone()[0]
    print(f"Feedback records before migration: {count_before}")

    # Step 1: Drop foreign key constraint (if exists)
    print("\nStep 1: Dropping foreign key constraint...")
    cursor.execute("""
        ALTER TABLE feedback
        DROP CONSTRAINT IF EXISTS feedback_conversation_id_fkey
    """)
    print("  [OK] FK constraint dropped")

    # Step 2: Change column type
    print("\nStep 2: Changing column type to VARCHAR(100)...")
    cursor.execute("""
        ALTER TABLE feedback
        ALTER COLUMN conversation_id TYPE VARCHAR(100)
        USING conversation_id::VARCHAR
    """)
    print("  [OK] Column type changed")

    # Commit changes
    conn.commit()
    print("\n[OK] Changes committed")

    # Verify
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'feedback' AND column_name = 'conversation_id'
    """)
    result = cursor.fetchone()
    print(f"\nNew type: {result[1]}")

    cursor.execute("SELECT COUNT(*) FROM feedback")
    count_after = cursor.fetchone()[0]
    print(f"Feedback records after migration: {count_after}")

    if count_before == count_after:
        print("\n" + "="*60)
        print("SUCCESS! Migration completed successfully!")
        print("="*60)
    else:
        print(f"\nWARNING: Record count changed ({count_before} -> {count_after})")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n[ERROR] Migration failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
