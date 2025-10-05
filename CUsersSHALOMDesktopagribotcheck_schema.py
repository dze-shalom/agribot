"""Check feedback table schema"""
import os
import psycopg2

RENDER_DB = os.getenv('DATABASE_URL', 'postgresql://agribot:EArtWDtDBQc8zgqwKsRQKk70mnVtau9e@dpg-d3g0e46r433s738ql1fg-a.frankfurt-postgres.render.com/agribot_s68e')

conn = psycopg2.connect(RENDER_DB)
cursor = conn.cursor()

# Get table schema
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'feedback'
    ORDER BY ordinal_position
""")

print("Feedback table schema:")
print("=" * 80)
print(f"{'Column':<30} {'Type':<20} {'Max Length':<15} {'Nullable':<10}")
print("-" * 80)
for row in cursor.fetchall():
    col_name, data_type, max_len, nullable = row
    max_len_str = str(max_len) if max_len else 'N/A'
    print(f"{col_name:<30} {data_type:<20} {max_len_str:<15} {nullable:<10}")

cursor.close()
conn.close()
