"""Check feedback on Render PostgreSQL database"""
import psycopg2

# Render PostgreSQL URL
RENDER_DB = "postgresql://agribot:EArtWDtDBQc8zgqwKsRQKk70mnVtau9e@dpg-d3g0e46r433s738ql1fg-a.frankfurt-postgres.render.com/agribot_s68e"

print("Checking Render PostgreSQL feedback...")
print("="*60)

try:
    conn = psycopg2.connect(RENDER_DB)
    cursor = conn.cursor()

    # Total feedback
    cursor.execute("SELECT COUNT(*) FROM feedback")
    total = cursor.fetchone()[0]
    print(f"Total feedback records: {total}")

    if total > 0:
        # Sample feedback
        cursor.execute("SELECT id, conversation_id, helpful, overall_rating FROM feedback LIMIT 5")
        print("\nSample feedback:")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Conv: {row[1]}, Helpful: {row[2]}, Rating: {row[3]}")

        # Check for session IDs
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE conversation_id::text LIKE 'session_%'")
        session_ids = cursor.fetchone()[0]
        print(f"\nFeedback with session IDs: {session_ids}")

        # Calculate satisfaction
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE helpful = true")
        helpful = cursor.fetchone()[0]
        print(f"\nHelpful feedback: {helpful}")
        print(f"Satisfaction rate: {(helpful/total*100):.1f}%")

        cursor.execute("SELECT AVG(overall_rating) FROM feedback WHERE overall_rating IS NOT NULL")
        avg_rating = cursor.fetchone()[0]
        if avg_rating:
            print(f"Average rating: {float(avg_rating):.2f}/5")
    else:
        print("\n[IMPORTANT] No feedback records in Render database!")
        print("This explains why analytics shows 'No data available'")

    # Check column type
    cursor.execute("""
        SELECT data_type FROM information_schema.columns
        WHERE table_name = 'feedback' AND column_name = 'conversation_id'
    """)
    col_type = cursor.fetchone()[0]
    print(f"\nColumn type on Render: {col_type}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

print("="*60)
