"""
Update Supabase database with uploaded file metadata
"""

from supabase import create_client
from datetime import datetime

# Supabase configuration
SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw"

# Initialize client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Timestamp from upload
TIMESTAMP = "20251106_114233"

print("=" * 60)
print("UPDATING SUPABASE DATABASE")
print("=" * 60)

# Prepare database record
database_record = {
    'mining_area_ha': 0.39,  # From multiclass mask size
    'new_mining_ha': 0.0,  # No change detection in this upload
    'change_percentage': 0.0,
    'num_sites': 8,  # From your geojson
    'status': 'completed',
    'notes': f'Uploaded from local machine at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. Files: mask, visualization, edge analysis.',
    'ai_model_version': 'UNet-v1.0',
    'prediction_tiff_url': f'{SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/predictions/chingola_multiclass_mask_{TIMESTAMP}.tif',
    'before_tiff_url': None,
    'after_tiff_url': None,
    'prediction_geojson_url': None
}

try:
    # Insert into database
    response = supabase.table('mining_updates').insert(database_record).execute()
    
    if response.data:
        record_id = response.data[0]['id']
        print(f"\n Database updated successfully!")
        print(f"   Record ID: {record_id}")
        print(f"   Mining Area: {database_record['mining_area_ha']} ha")
        print(f"   Status: {database_record['status']}")
        print(f"\n Prediction URL:")
        print(f"   {database_record['prediction_tiff_url']}")
        print(f"\n Visualizations:")
        print(f"   Mask: {SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/visualizations/mask_visualization_{TIMESTAMP}.png")
        print(f"   Edge: {SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/visualizations/mask_edge_analysis_{TIMESTAMP}.png")
        
        print("\n" + "=" * 60)
        print(" COMPLETE! Files uploaded and database updated")
        print("=" * 60)
        print("\n Your mobile app can now fetch these files from the cloud!")
        
    else:
        print("\n  Database update returned no data")
        
except Exception as e:
    print(f"\n Failed to update database: {e}")
