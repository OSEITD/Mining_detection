"""
Upload Existing Predictions to Supabase
Uploads your current TIFFs and GeoJSON to Supabase storage
"""

from supabase import create_client
import os
from datetime import datetime

# Configuration
SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw"

# Files to upload
FILES_TO_UPLOAD = [
    {
        'local': 'Mining_Analysis_Results/prediction_2016.tif',
        'remote': 'predictions/prediction_2016.tif',
        'type': 'image/tiff'
    },
    {
        'local': 'Mining_Analysis_Results/prediction_2025.tif',
        'remote': 'predictions/prediction_2025.tif',
        'type': 'image/tiff'
    },
    {
        'local': 'Mining_Analysis_Results/change_map.tif',
        'remote': 'predictions/change_map.tif',
        'type': 'image/tiff'
    },
    {
        'local': 'Mining_Analysis_Results/inference_results.png',
        'remote': 'visualizations/inference_results.png',
        'type': 'image/png'
    },
    {
        'local': 'Mining_Analysis_Results/mask_visualization.png',
        'remote': 'visualizations/mask_visualization.png',
        'type': 'image/png'
    },
    {
        'local': 'data/lable/chingola_mines.geojson',
        'remote': 'geojson/chingola_mines.geojson',
        'type': 'application/json'
    }
]

def upload_file(supabase, local_path, remote_path, content_type):
    """Upload a single file to Supabase"""
    
    if not os.path.exists(local_path):
        print(f"     File not found: {local_path}")
        return None
    
    # Get file size
    size_mb = os.path.getsize(local_path) / (1024 * 1024)
    
    if size_mb > 50:
        print(f"    File too large: {size_mb:.1f} MB (limit: 50 MB)")
        return None
    
    print(f"    Uploading {os.path.basename(local_path)} ({size_mb:.1f} MB)...")
    
    try:
        # Read file
        with open(local_path, 'rb') as f:
            file_content = f.read()
        
        # Upload to Supabase
        response = supabase.storage.from_('illegal-mining-data').upload(
            remote_path,
            file_content,
            {'content-type': content_type}
        )
        
        # Generate public URL
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/{remote_path}"
        
        print(f"    Uploaded: {public_url}")
        return public_url
        
    except Exception as e:
        error_msg = str(e)
        if 'Duplicate' in error_msg or '409' in error_msg:
            # File already exists - that's ok!
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/{remote_path}"
            print(f"    Already exists: {public_url}")
            return public_url
        else:
            print(f"    Upload failed: {e}")
            return None

def update_database(supabase, urls):
    """Update database with file URLs"""
    
    print("\n Updating database...")
    
    try:
        # Insert record into mining_updates
        response = supabase.table('mining_updates').insert({
            'before_tiff_url': 'https://ntkzaobvbsppxbljamvb.supabase.co/storage/v1/object/public/illegal-mining-data/before/chingola_Before_2016.tif',
            'after_tiff_url': 'https://ntkzaobvbsppxbljamvb.supabase.co/storage/v1/object/public/illegal-mining-data/after/chingola_After_2025.tif',
            'prediction_tiff_url': urls.get('prediction_2025'),
            'prediction_geojson_url': urls.get('geojson'),
            'mining_area_ha': 450.5,  # Update with actual value
            'new_mining_ha': 75.3,
            'num_sites': 23,
            'status': 'completed',
            'notes': 'Initial upload of existing predictions'
        }).execute()
        
        if response.data:
            print(f" Database updated (Record ID: {response.data[0]['id']})")
        
    except Exception as e:
        print(f"  Database update failed: {e}")

def main():
    print("=" * 60)
    print(" UPLOADING PREDICTIONS TO SUPABASE")
    print("=" * 60)
    
    # Initialize Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    urls = {}
    uploaded_count = 0
    
    # Upload each file
    for file_info in FILES_TO_UPLOAD:
        print(f"\n {file_info['local']}")
        url = upload_file(
            supabase,
            file_info['local'],
            file_info['remote'],
            file_info['type']
        )
        
        if url:
            uploaded_count += 1
            # Store URL for database update
            if 'prediction_2025' in file_info['remote']:
                urls['prediction_2025'] = url
            elif 'geojson' in file_info['remote']:
                urls['geojson'] = url
    
    # Update database
    if urls:
        update_database(supabase, urls)
    
    # Summary
    print("\n" + "=" * 60)
    print(f" UPLOAD COMPLETE!")
    print("=" * 60)
    print(f"\n Summary:")
    print(f"   Files processed: {len(FILES_TO_UPLOAD)}")
    print(f"   Successfully uploaded: {uploaded_count}")
    print(f"\n View files:")
    print(f"   https://supabase.com/dashboard/project/ntkzaobvbsppxbljamvb/storage/buckets/illegal-mining-data")
    print(f"\n Your mobile app can now fetch these predictions!")

if __name__ == "__main__":
    main()
