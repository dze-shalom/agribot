# Safe Migration Plan - Fix Feedback System

## The Problem
- Feedback button sends session IDs like "session_1759240848418"
- Backend validation rejects them → 400 error
- Backend model expects INTEGER → 500 error on PostgreSQL
- Result: No feedback can be saved

## The Solution (3 Steps)

### Step 1: Update Model (Code Change)
Change `database/models/analytics.py`:
```python
# FROM:
conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)

# TO:
conversation_id = db.Column(db.String(100), nullable=False)
```

### Step 2: Update Validation (Code Change)
Change `app/routes/chat.py` to accept session IDs:
```python
# Simply remove the validation that rejects session IDs
# Just check it exists
if not conversation_id:
    return jsonify({'error': 'Conversation ID is required'}), 400
```

### Step 3: Run Database Migration (One-Time)
Run locally (connects to Render database):
```bash
python migrate_feedback_to_varchar.py
```

This changes the column from INTEGER to VARCHAR on production database.

### Step 4: Deploy Code
```bash
git add database/models/analytics.py app/routes/chat.py
git commit -m "Fix: Support session IDs in feedback"
git push origin main
```

## Order is Important!

**WRONG ORDER (will break):**
1. Deploy code first
2. Run migration later
→ Code expects VARCHAR but DB has INTEGER → Errors!

**CORRECT ORDER:**
1. Run migration first (DB ready for VARCHAR)
2. Deploy code (code uses VARCHAR)
→ Everything works!

## Safety
- Migration preserves all existing data
- If anything fails, we can rollback the code deploy
- Database migration is non-destructive

## Ready to proceed?
Say "yes" and I'll make the changes and run the migration.
