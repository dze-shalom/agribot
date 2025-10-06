# Deployment Guide - Analytics & Feedback Fixes

## Changes Summary

This update fixes critical issues with analytics dashboard and feedback system:

1. **User Satisfaction now displays correctly** (was showing "No data available")
2. **ML Dataset exports now include all feedback data** (was missing feedback records)
3. **Analytics page loads properly** (improved error handling)
4. **Feedback system now accepts temporary session IDs** (prevents data loss)

## Files Changed

- `database/models/analytics.py` - Updated Feedback model to accept string conversation IDs
- `database/repositories/analytics_repository.py` - Enhanced feedback handling
- `app/routes/chat.py` - Fixed feedback submission validation
- `app/routes/admin.py` - Improved ML dataset export matching
- `app/routes/auth.py` - Added better error logging
- `migrations/update_feedback_postgres.py` - New migration script for PostgreSQL

## Pre-Deployment Checklist

### 1. Backup Production Database (IMPORTANT!)

Before deploying, backup your Render database:

```bash
# SSH into your Render service or use Render dashboard
# Go to your database service -> Backups -> Create Manual Backup
```

**OR** from Render Shell:
```bash
pg_dump $DATABASE_URL > backup_before_feedback_migration.sql
```

### 2. Push Changes to GitHub

```bash
git add .
git commit -m "Fix: Analytics dashboard and feedback system - handle session IDs properly"
git push origin main
```

Render will automatically detect the push and start deploying.

## Post-Deployment Steps

### Step 1: Verify Deployment Success

1. Wait for Render deployment to complete (check Render dashboard)
2. Check deployment logs for any errors
3. Verify the app is running: `https://your-app.onrender.com`

### Step 2: Run Database Migration

**Option A: Using Render Shell (Recommended)**

1. Go to Render Dashboard → Your Service → Shell
2. Run the migration:

```bash
python migrations/update_feedback_postgres.py
```

3. You should see output like:
```
Starting PostgreSQL migration...
Current conversation_id type: INTEGER
Found 28 feedback records
Applying migration...
Migration completed successfully!
New conversation_id type: VARCHAR(100)
```

**Option B: Using Local Migration (if you have access to production DB URL)**

```bash
# Set production database URL
export DATABASE_URL="your_render_postgres_url"
python migrations/update_feedback_postgres.py
```

### Step 3: Verify Migration Success

1. Check that feedback data is preserved:
```bash
# In Render Shell
python -c "from app.main import create_app; from database import db; from database.models.analytics import Feedback; app = create_app(); app.app_context().push(); print(f'Total feedback: {Feedback.query.count()}'); print(f'Sample IDs: {[f.conversation_id for f in Feedback.query.limit(5).all()]}')"
```

2. Test the analytics dashboard:
   - Visit `https://your-app.onrender.com/analytics.html`
   - Check if "User Satisfaction" shows data (not "No data available")
   - Verify charts load properly

3. Test ML dataset export:
   - Go to analytics page
   - Export ML Dataset
   - Verify feedback columns have data

### Step 4: Test New Feedback Submission

1. Log in as a regular user
2. Chat with the bot
3. Submit feedback with ratings
4. Verify feedback appears in analytics immediately

## Rollback Plan

If something goes wrong:

### Quick Rollback:
1. In Render Dashboard → Manual Deploy → Select previous deployment
2. Render will redeploy the old code

### Database Rollback (if needed):
1. Restore from the backup you created:
```bash
psql $DATABASE_URL < backup_before_feedback_migration.sql
```

## Expected Results

After successful deployment:

- ✅ **28 existing feedback records** preserved and accessible
- ✅ **User Satisfaction**: Should show "3.3/5" or "43%" (based on your current data)
- ✅ **ML Dataset**: Will include feedback in "Has Feedback", "Feedback Helpful", and rating columns
- ✅ **New feedback**: Will be accepted with both real conversation IDs and temp session IDs
- ✅ **Analytics dashboard**: Loads without infinite "Loading..." state

## Monitoring

After deployment, monitor:

1. **Error logs** in Render dashboard for any database errors
2. **Analytics page** - should load within 2-3 seconds
3. **User feedback submissions** - check if new feedback is being saved
4. **ML dataset exports** - verify feedback data is included

## Troubleshooting

### Issue: Migration fails with "column does not exist"
**Solution**: Migration might have run already. Check column type:
```sql
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'feedback' AND column_name = 'conversation_id';
```

### Issue: Foreign key constraint error
**Solution**: The migration removes the FK constraint. If you see this, the migration is working correctly.

### Issue: Analytics still shows "No data available"
**Possible causes**:
1. Migration didn't run - verify with Step 3 above
2. Cache issue - hard refresh browser (Ctrl+Shift+R)
3. Check browser console for JavaScript errors

### Issue: New feedback not saving
**Check**:
1. Browser console for errors
2. Render logs for backend errors
3. Database connection is working

## Questions?

If you encounter issues:
1. Check Render deployment logs
2. Check browser console (F12)
3. Verify migration ran successfully
4. Check database connectivity

---

**IMPORTANT**: Don't skip the database backup step! While this migration is designed to be safe, always backup production data before schema changes.
