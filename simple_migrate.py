"""Simple migration script - copies users from local SQLite to Render PostgreSQL"""
import sqlite3
import psycopg2
import sys

# Render PostgreSQL URL
RENDER_DB = "postgresql://agribot:EArtWDtDBQc8zgqwKsRQKk70mnVtau9e@dpg-d3g0e46r433s738ql1fg-a.frankfurt-postgres.render.com/agribot_s68e"

# Local SQLite
LOCAL_DB = "instance/agribot.db"

print("Migrating users from local SQLite to Render PostgreSQL...")
print("="*60)

# Connect to local SQLite
sqlite_conn = sqlite3.connect(LOCAL_DB)
sqlite_cursor = sqlite_conn.cursor()

# Get all users
sqlite_cursor.execute("SELECT * FROM users")
users = sqlite_cursor.fetchall()

print(f"Found {len(users)} users in local database")

# Connect to Render PostgreSQL
pg_conn = psycopg2.connect(RENDER_DB)
pg_cursor = pg_conn.cursor()

# Migrate each user
migrated = 0
skipped = 0

for user in users:
    # Unpack all columns
    (user_id, name, email, password_hash, phone, region, account_type, status,
     preferred_language, notification_preferences, profile_data, created_at,
     last_active, last_login, total_conversations, country) = user

    try:
        # Check if user already exists
        pg_cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing = pg_cursor.fetchone()

        if existing:
            print(f"  [SKIP] {email} - already exists")
            skipped += 1
            continue

        # Insert user (let PostgreSQL auto-generate ID)
        pg_cursor.execute("""
            INSERT INTO users (name, email, password_hash, phone, region, country,
                             account_type, status, preferred_language, notification_preferences,
                             profile_data, created_at, last_active, last_login, total_conversations)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (name, email, password_hash, phone, region, country, account_type, status,
              preferred_language, notification_preferences, profile_data, created_at,
              last_active, last_login, total_conversations))

        print(f"  [OK] {email} - {name}")
        migrated += 1

    except Exception as e:
        print(f"  [ERROR] {email}: {str(e)}")

# Commit changes
pg_conn.commit()

print("="*60)
print(f"Migration complete!")
print(f"  Migrated: {migrated} users")
print(f"  Skipped:  {skipped} users (already existed)")

# Close connections
sqlite_conn.close()
pg_conn.close()
