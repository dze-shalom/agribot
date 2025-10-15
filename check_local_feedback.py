import sqlite3
import os

db_path = r'instance\agribot.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    print("\nChecking other locations...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'agribot.db':
                print(f"Found database at: {os.path.join(root, file)}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check feedback
    cursor.execute('SELECT COUNT(*) FROM feedback')
    total = cursor.fetchone()[0]
    print(f'Total feedback records: {total}')

    if total > 0:
        cursor.execute('SELECT id, conversation_id, helpful, overall_rating FROM feedback LIMIT 5')
        print('\nSample feedback:')
        for row in cursor.fetchall():
            print(f'  ID: {row[0]}, Conv: {row[1]}, Helpful: {row[2]}, Rating: {row[3]}')

        # Check if there are session IDs
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE CAST(conversation_id AS TEXT) LIKE 'session_%'")
        session_ids = cursor.fetchone()[0]
        print(f'\nFeedback with session IDs: {session_ids}')

        # Calculate satisfaction
        cursor.execute('SELECT COUNT(*) FROM feedback WHERE helpful = 1')
        helpful = cursor.fetchone()[0]
        print(f'\nHelpful feedback: {helpful}')
        print(f'Satisfaction rate: {(helpful/total*100):.1f}%')

        cursor.execute('SELECT AVG(overall_rating) FROM feedback WHERE overall_rating IS NOT NULL')
        avg_rating = cursor.fetchone()[0]
        if avg_rating:
            print(f'Average rating: {avg_rating:.2f}/5')

    conn.close()
