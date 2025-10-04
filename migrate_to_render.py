#!/usr/bin/env python
"""
Quick Migration Script to Render PostgreSQL
Run this to migrate your local SQLite data to Render
"""
import sys
import os

def main():
    print("=" * 60)
    print("AGRIBOT - Migrate Local Database to Render PostgreSQL")
    print("=" * 60)

    # Check if local database exists
    local_db = "instance/agribot.db"
    if not os.path.exists(local_db):
        print(f"\n❌ Error: Local database not found at {local_db}")
        print("   Make sure you're in the agribot directory")
        sys.exit(1)

    # Get database stats
    import sqlite3
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM conversations')
    conv_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM messages')
    msg_count = cursor.fetchone()[0]

    conn.close()

    print(f"\n📊 Local Database Stats:")
    print(f"   Users: {user_count}")
    print(f"   Conversations: {conv_count}")
    print(f"   Messages: {msg_count}")

    # Get Render database URL
    print("\n" + "=" * 60)
    print("STEP 1: Get Your Render Database URL")
    print("=" * 60)
    print("\n1. Go to: https://dashboard.render.com")
    print("2. Click on your 'agribot-db' PostgreSQL database")
    print("3. Copy the 'Internal Database URL'")
    print("   (starts with postgresql://)")
    print("\nExample:")
    print("postgresql://agribot:xyz123@dpg-xxx.oregon-postgres.render.com/agribot")

    render_db_url = input("\n📝 Paste your Render Database URL here: ").strip()

    if not render_db_url.startswith('postgresql://'):
        print("\n❌ Error: Invalid PostgreSQL URL")
        print("   It should start with 'postgresql://'")
        sys.exit(1)

    # Confirm migration
    print("\n" + "=" * 60)
    print("STEP 2: Confirm Migration")
    print("=" * 60)
    print(f"\n⚠️  This will migrate:")
    print(f"   FROM: {local_db}")
    print(f"   TO:   {render_db_url[:50]}...")
    print(f"\n   {user_count} users, {conv_count} conversations, {msg_count} messages")

    confirm = input("\n⚙️  Proceed with migration? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("\n❌ Migration cancelled")
        sys.exit(0)

    # Run migration
    print("\n" + "=" * 60)
    print("STEP 3: Running Migration...")
    print("=" * 60)

    from migrate_db_auto import migrate_database

    success = migrate_database(local_db, render_db_url)

    if success:
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Verify data on Render:")
        print(f"   python list_users.py \"{render_db_url}\"")
        print("\n2. Your local database is safe in: instance/agribot.db")
        print("3. This local DB will NOT be pushed to git (protected by .gitignore)")
        print("\n4. Redeploy on Render if needed:")
        print("   git add .")
        print("   git commit -m 'Updated config'")
        print("   git push")
    else:
        print("\n❌ Migration failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
