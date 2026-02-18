"""
Check what files are currently in Supabase storage
"""

from supabase import create_client

SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("FILES IN SUPABASE STORAGE")
print("=" * 60)

# Check predictions folder
try:
    pred_files = supabase.storage.from_('illegal-mining-data').list('predictions')
    print(f"\n📂 Predictions folder: {len(pred_files)} files")
    for f in pred_files:
        size_mb = f.get('metadata', {}).get('size', 0) / (1024 * 1024)
        print(f"   • {f['name']} ({size_mb:.2f} MB)")
except Exception as e:
    print(f"\n❌ Predictions folder: {e}")

# Check visualizations folder
try:
    viz_files = supabase.storage.from_('illegal-mining-data').list('visualizations')
    print(f"\n📊 Visualizations folder: {len(viz_files)} files")
    for f in viz_files:
        size_mb = f.get('metadata', {}).get('size', 0) / (1024 * 1024)
        print(f"   • {f['name']} ({size_mb:.2f} MB)")
except Exception as e:
    print(f"\n❌ Visualizations folder: {e}")

# Check database records
try:
    records = supabase.table('mining_updates').select('id, update_time, status, mining_area_ha').order('update_time', desc=True).limit(3).execute()
    print(f"\n💾 Recent database records: {len(records.data)} records")
    for r in records.data:
        print(f"   • ID {r['id']}: {r['update_time'][:19]} - {r['status']} ({r['mining_area_ha']} ha)")
except Exception as e:
    print(f"\n❌ Database: {e}")

print("\n" + "=" * 60)
