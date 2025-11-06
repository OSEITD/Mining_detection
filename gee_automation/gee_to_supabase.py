"""
Complete GEE to Supabase Automation Pipeline
Downloads satellite data from GEE and uploads to Supabase
"""

import ee
import datetime
import os
from pathlib import Path
from supabase import create_client
import json

# ============================================
# CONFIGURATION
# ============================================

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ntkzaobvbsppxbljamvb.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw')

# Area of Interest
AOI_COORDS = [
    [27.7, -12.6],
    [28.2, -12.6],
    [28.2, -12.4],
    [27.7, -12.4],
    [27.7, -12.6]
]

# Output directory
OUTPUT_DIR = Path(__file__).parent / 'temp_downloads'
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================
# INITIALIZE CLIENTS
# ============================================

def initialize():
    """Initialize Earth Engine and Supabase"""
    print("=" * 60)
    print("INITIALIZING CLIENTS")
    print("=" * 60)
    
    # Initialize Earth Engine
    try:
        ee.Initialize()
        print("✅ Earth Engine initialized")
    except Exception as e:
        print(f"❌ Earth Engine failed: {e}")
        print("   Trying to authenticate...")
        try:
            ee.Authenticate()
            ee.Initialize()
            print("✅ Earth Engine authenticated and initialized")
        except Exception as e2:
            print(f"❌ Authentication failed: {e2}")
            return None, None
    
    # Initialize Supabase
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase initialized")
    except Exception as e:
        print(f"❌ Supabase failed: {e}")
        return None, None
    
    return ee, supabase

# ============================================
# FETCH LATEST SATELLITE DATA
# ============================================

def fetch_latest_composite(days_back=30, cloud_threshold=20):
    """
    Fetch latest cloud-free Sentinel-2 composite
    
    Args:
        days_back: Number of days to look back
        cloud_threshold: Maximum cloud percentage
    
    Returns:
        Earth Engine image composite
    """
    print(f"\n📡 Fetching Sentinel-2 data (last {days_back} days)")
    
    # Define date range
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days_back)
    
    # Create geometry
    aoi = ee.Geometry.Polygon(AOI_COORDS)
    
    # Load Sentinel-2 collection
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(aoi) \
        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold))
    
    # Check count
    count = s2.size().getInfo()
    print(f"   Found {count} images")
    
    if count == 0:
        print("   ⚠️  No images found")
        return None, None
    
    # Create median composite
    composite = s2.median().clip(aoi)
    
    # Calculate NDVI
    ndvi = composite.normalizedDifference(['B8', 'B4']).rename('NDVI')
    
    return composite, ndvi

# ============================================
# EXPORT IMAGE AS URL
# ============================================

def get_download_url(image, name, scale=10):
    """
    Get download URL for an Earth Engine image
    
    Args:
        image: Earth Engine image
        name: Image name
        scale: Resolution in meters
    
    Returns:
        Download URL
    """
    aoi = ee.Geometry.Polygon(AOI_COORDS)
    
    url = image.getDownloadURL({
        'name': name,
        'scale': scale,
        'region': aoi,
        'filePerBand': False,
        'format': 'GEO_TIFF'
    })
    
    return url

# ============================================
# UPLOAD TO SUPABASE
# ============================================

def upload_metadata_to_db(supabase, metadata):
    """
    Upload satellite data metadata to Supabase database
    
    Args:
        supabase: Supabase client
        metadata: Dictionary with metadata
    """
    print("\n💾 Updating database...")
    
    try:
        # Insert into satellite_updates table (create if needed)
        response = supabase.table('satellite_updates').insert({
            'collection_date': metadata['date'],
            'satellite': 'Sentinel-2',
            'cloud_percentage': metadata.get('cloud_pct', 0),
            'image_count': metadata.get('image_count', 0),
            'download_url': metadata.get('download_url'),
            'ndvi_url': metadata.get('ndvi_url'),
            'status': 'completed'
        }).execute()
        
        if response.data:
            print(f"   ✅ Database updated (ID: {response.data[0]['id']})")
            return response.data[0]['id']
        else:
            print("   ⚠️  Database update returned no data")
            return None
            
    except Exception as e:
        print(f"   ❌ Database update failed: {e}")
        print(f"   Note: Make sure 'satellite_updates' table exists")
        return None

# ============================================
# MAIN AUTOMATION WORKFLOW
# ============================================

def main():
    """Main automation workflow"""
    print("\n" + "=" * 60)
    print("GEE TO SUPABASE AUTOMATION")
    print("=" * 60)
    print(f"⏰ Run time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize
    ee_module, supabase = initialize()
    if ee_module is None or supabase is None:
        print("\n❌ Initialization failed")
        return
    
    # Fetch latest data
    print("\n" + "=" * 60)
    print("FETCHING SATELLITE DATA")
    print("=" * 60)
    
    composite, ndvi = fetch_latest_composite(days_back=30)
    
    if composite is None:
        print("\n❌ No data available")
        return
    
    # Get download URLs
    print("\n" + "=" * 60)
    print("GENERATING DOWNLOAD URLs")
    print("=" * 60)
    
    try:
        # RGB composite URL
        rgb = composite.select(['B4', 'B3', 'B2'])
        rgb_url = get_download_url(rgb, 'chingola_latest_rgb')
        print(f"✅ RGB URL generated")
        print(f"   {rgb_url[:80]}...")
        
        # NDVI URL
        ndvi_url = get_download_url(ndvi, 'chingola_latest_ndvi')
        print(f"✅ NDVI URL generated")
        print(f"   {ndvi_url[:80]}...")
        
    except Exception as e:
        print(f"❌ URL generation failed: {e}")
        return
    
    # Upload metadata to database
    metadata = {
        'date': datetime.datetime.now().isoformat(),
        'download_url': rgb_url,
        'ndvi_url': ndvi_url,
        'cloud_pct': 10,  # Placeholder
        'image_count': 1
    }
    
    db_id = upload_metadata_to_db(supabase, metadata)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ AUTOMATION COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    print(f"   Database ID: {db_id}")
    print(f"   RGB URL: Available")
    print(f"   NDVI URL: Available")
    print(f"\n💡 Next Steps:")
    print(f"   1. Download files from URLs")
    print(f"   2. Run U-Net inference on new imagery")
    print(f"   3. Upload predictions to Supabase")
    print(f"   4. Mobile app will auto-fetch latest data")
    
    # Save URLs to file
    urls_file = OUTPUT_DIR / f'download_urls_{datetime.datetime.now().strftime("%Y%m%d")}.json'
    with open(urls_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n📄 URLs saved to: {urls_file}")

if __name__ == "__main__":
    main()
