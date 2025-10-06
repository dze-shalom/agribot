# Quick Deployment Steps

## ⚠️ CRITICAL: Database Will NOT Be Reset

Your Render database is **persistent and separate from the code**. This deployment:
- ✅ Will NOT delete existing data
- ✅ Will NOT reset the database
- ✅ Requires a one-time migration after deployment

## Step-by-Step

### 1. Backup (1 minute)
```
Render Dashboard → PostgreSQL Database → Backups → Create Manual Backup
```

### 2. Push to GitHub (30 seconds)
```bash
git add .
git commit -m "Fix analytics and feedback system"
git push origin main
```

### 3. Wait for Auto-Deploy (2-5 minutes)
Render will automatically deploy when it detects the push.

### 4. Run Migration (1 minute)
**After deployment completes:**
```
Render Dashboard → Your Web Service → Shell → Type:
python migrations/update_feedback_postgres.py
```

Expected output:
```
Starting PostgreSQL migration...
Found 28 feedback records
Migration completed successfully!
```

### 5. Verify (30 seconds)
- Visit: `https://your-app.onrender.com/analytics.html`
- Check: User Satisfaction shows "3.3/5" or percentage (not "No data available")
- Test: Export ML Dataset and verify feedback columns have data

## That's It! 🎉

Your existing data is safe. The migration just changes how conversation IDs are stored to support both real IDs and temporary session IDs.

## Quick Rollback (if needed)
```
Render Dashboard → Manual Deploy → Select previous deployment
```
