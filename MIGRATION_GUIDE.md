# Migrate Local Database to Render PostgreSQL

## Step 1: Get Render Database URL

1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your **agribot-db** PostgreSQL database
3. Copy the **Internal Database URL** (starts with `postgresql://`)
   - It looks like: `postgresql://agribot:PASSWORD@dpg-xxx.oregon-postgres.render.com/agribot`

## Step 2: Run Migration

```bash
# Make sure you're in the agribot directory
cd C:\Users\SHALOM\Desktop\agribot

# Run the migration script
python migrate_db_auto.py instance/agribot.db "YOUR_RENDER_DATABASE_URL"
```

**Example:**
```bash
python migrate_db_auto.py instance/agribot.db "postgresql://agribot:abcd1234@dpg-xxx.oregon-postgres.render.com/agribot"
```

## Step 3: Verify Migration

After migration completes, verify on Render:
```bash
python list_users.py "YOUR_RENDER_DATABASE_URL"
```

## Step 4: Update .gitignore to Prevent Database Push

Add to `.gitignore`:
```
*.db
*.db-journal
instance/
```

## Step 5: Fix Local Development Setup

Update `config/settings.py` line 17:
```python
url: str = os.getenv('DATABASE_URL', 'sqlite:///instance/agribot.db')
```

This ensures:
- **Local dev**: Uses SQLite at `instance/agribot.db`
- **Render production**: Uses PostgreSQL from DATABASE_URL env var

## Troubleshooting

### If migration fails with "table already exists":
```bash
# Connect to Render PostgreSQL and drop all tables first
python -c "
from sqlalchemy import create_engine, text
engine = create_engine('YOUR_RENDER_DATABASE_URL')
with engine.connect() as conn:
    conn.execute(text('DROP SCHEMA public CASCADE'))
    conn.execute(text('CREATE SCHEMA public'))
    conn.commit()
print('Database cleared, run migration again')
"
```

### If you lose data on Render:
- **Always keep local SQLite as backup**
- Re-run migration script to restore data
- Consider setting up automated backups

## Prevention: Never Push Database Files

1. Check `.gitignore` includes:
   ```
   *.db
   *.db-journal
   instance/
   ```

2. Remove any committed database files:
   ```bash
   git rm --cached agribot.db
   git rm --cached instance/agribot.db
   git commit -m "Remove database files from git"
   ```

3. On Render, database is managed separately via PostgreSQL service
