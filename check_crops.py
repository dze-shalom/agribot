import sqlite3
from datetime import datetime, timedelta
import json

conn = sqlite3.connect('instance/agribot.db')
cursor = conn.cursor()

# Check current period (last 7 days)
cutoff = datetime.now() - timedelta(days=7)
cursor.execute("""
    SELECT id, mentioned_crops, start_time
    FROM conversations
    WHERE start_time >= ? AND mentioned_crops IS NOT NULL AND mentioned_crops != '[]'
    ORDER BY start_time DESC
""", (cutoff.isoformat(),))

print("CURRENT PERIOD (Last 7 days):")
print("=" * 80)
current_crops = {}
for row in cursor.fetchall():
    conv_id, crops_json, start_time = row
    crops = json.loads(crops_json) if crops_json else []
    print(f"ID: {conv_id} | Start: {start_time} | Crops: {crops}")
    for crop in crops:
        current_crops[crop.lower().capitalize()] = current_crops.get(crop.lower().capitalize(), 0) + 1

print(f"\nCurrent period crop counts: {current_crops}")

# Check previous period (7-14 days ago)
previous_cutoff = datetime.now() - timedelta(days=14)
cursor.execute("""
    SELECT id, mentioned_crops, start_time
    FROM conversations
    WHERE start_time >= ? AND start_time < ? AND mentioned_crops IS NOT NULL AND mentioned_crops != '[]'
    ORDER BY start_time DESC
""", (previous_cutoff.isoformat(), cutoff.isoformat()))

print("\n" + "=" * 80)
print("PREVIOUS PERIOD (7-14 days ago):")
print("=" * 80)
previous_crops = {}
for row in cursor.fetchall():
    conv_id, crops_json, start_time = row
    crops = json.loads(crops_json) if crops_json else []
    print(f"ID: {conv_id} | Start: {start_time} | Crops: {crops}")
    for crop in crops:
        previous_crops[crop.lower().capitalize()] = previous_crops.get(crop.lower().capitalize(), 0) + 1

print(f"\nPrevious period crop counts: {previous_crops}")

conn.close()
