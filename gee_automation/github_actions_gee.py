"""
GitHub Actions Compatible GEE Script
Simplified version for automated runs with proper authentication
"""

import ee
import os
import sys
import json
from datetime import datetime, timedelta

def initialize_earth_engine():
    """Initialize Earth Engine with GitHub Actions authentication"""
    print("🔧 Initializing Earth Engine...")
    
    # Try environment variable authentication (GitHub Actions)
    ee_token = os.getenv('EARTHENGINE_TOKEN')
    
    if ee_token:
        print("   Using EARTHENGINE_TOKEN from environment")
        try:
            # Parse token if it's JSON and write to temp file
            credentials_dict = json.loads(ee_token)
            
            # Write credentials to temporary location
            creds_path = '/tmp/ee_credentials'
            os.makedirs(os.path.dirname(creds_path), exist_ok=True)
            with open(creds_path, 'w') as f:
                json.dump(credentials_dict, f)
            
            # Authenticate using the credentials file
            os.environ['EARTHENGINE_CREDENTIALS_PATH'] = creds_path
            ee.Authenticate(auth_mode='gcloud', quiet=True)
            ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
            print("✅ Earth Engine initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️  Token authentication failed: {e}")
            # Try direct initialization with credentials
            try:
                credentials_dict = json.loads(ee_token)
                from google.oauth2.credentials import Credentials
                from google.auth.transport.requests import AuthorizedSession
                
                creds = Credentials(
                    token=None,
                    refresh_token=credentials_dict.get('refresh_token'),
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id='517222506229-vsmmajv00ul0bs7p89v5m89qs8eb9359.apps.googleusercontent.com',
                    scopes=credentials_dict.get('scopes', [])
                )
                ee.Initialize(credentials=creds, opt_url='https://earthengine-highvolume.googleapis.com')
                print("✅ Earth Engine initialized with OAuth2 credentials")
                return True
            except Exception as e2:
                print(f"⚠️  OAuth2 initialization failed: {e2}")
    
    # Try service account (alternative method)
    service_account = os.getenv('GEE_SERVICE_ACCOUNT')
    private_key = os.getenv('GEE_PRIVATE_KEY')
    
    if service_account and private_key:
        print("   Using service account authentication")
        try:
            credentials = ee.ServiceAccountCredentials(service_account, key_data=private_key)
            ee.Initialize(credentials)
            print("✅ Earth Engine initialized with service account")
            return True
        except Exception as e:
            print(f"⚠️  Service account failed: {e}")
    
    # Fallback: Try default authentication
    try:
        ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
        print("✅ Earth Engine initialized with default credentials")
        return True
    except Exception as e:
        print(f"❌ All authentication methods failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Set EARTHENGINE_TOKEN secret in GitHub")
        print("   2. Or set GEE_SERVICE_ACCOUNT and GEE_PRIVATE_KEY")
        print("   3. Follow: https://developers.google.com/earth-engine/guides/service_account")
        return False

def fetch_latest_imagery(aoi_coords, days_back=30):
    """
    Fetch latest Sentinel-2 imagery
    
    Args:
        aoi_coords: List of [lon, lat] coordinates
        days_back: How many days to look back
    
    Returns:
        (composite_image, ndvi_image, metadata)
    """
    print(f"\n📡 Fetching Sentinel-2 imagery (last {days_back} days)...")
    
    # Create AOI geometry
    aoi = ee.Geometry.Polygon([aoi_coords])
    
    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"   Date range: {start_date.date()} to {end_date.date()}")
    
    # Load Sentinel-2 collection
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(aoi)
        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
    
    # Check image count
    count = collection.size().getInfo()
    print(f"   Found: {count} images")
    
    if count == 0:
        print("   ⚠️  No suitable images found (try increasing days_back or cloud threshold)")
        return None, None, None
    
    # Create median composite
    composite = collection.median().clip(aoi)
    
    # Calculate NDVI
    ndvi = composite.normalizedDifference(['B8', 'B4']).rename('NDVI')
    
    # Metadata
    metadata = {
        'image_count': count,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'satellite': 'Sentinel-2',
        'cloud_threshold': 20
    }
    
    print("✅ Imagery fetched successfully")
    return composite, ndvi, metadata

def get_download_url(image, name, aoi_coords, scale=10):
    """
    Generate download URL for Earth Engine image
    
    Args:
        image: Earth Engine image
        name: Export name
        aoi_coords: AOI coordinates
        scale: Resolution in meters
    
    Returns:
        Download URL string
    """
    aoi = ee.Geometry.Polygon([aoi_coords])
    
    try:
        url = image.getDownloadURL({
            'name': name,
            'scale': scale,
            'region': aoi,
            'filePerBand': False,
            'format': 'GEO_TIFF'
        })
        return url
    except Exception as e:
        print(f"   ⚠️  URL generation failed: {e}")
        return None

def upload_to_supabase(metadata):
    """
    Upload metadata to Supabase database
    
    Args:
        metadata: Dictionary with satellite data info
    
    Returns:
        Database record ID or None
    """
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment")
        print("   Set SUPABASE_URL and SUPABASE_KEY secrets")
        return None
    
    print("\n💾 Uploading to Supabase...")
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        # Insert record
        response = supabase.table('satellite_updates').insert({
            'collection_date': metadata['end_date'],
            'satellite': metadata['satellite'],
            'cloud_percentage': metadata.get('cloud_pct', 0),
            'image_count': metadata['image_count'],
            'download_url': metadata.get('rgb_url'),
            'ndvi_url': metadata.get('ndvi_url'),
            'status': 'completed',
            'notes': f"Automated collection: {metadata['image_count']} images from {metadata['start_date'][:10]} to {metadata['end_date'][:10]}"
        }).execute()
        
        if response.data:
            record_id = response.data[0]['id']
            print(f"✅ Database updated (Record ID: {record_id})")
            return record_id
        else:
            print("⚠️  Database insert returned no data")
            return None
            
    except Exception as e:
        print(f"❌ Supabase upload failed: {e}")
        return None

def main():
    """Main workflow for GitHub Actions"""
    print("=" * 60)
    print("AUTOMATED SATELLITE DATA COLLECTION")
    print("=" * 60)
    print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Area of Interest (Chingola, Zambia)
    AOI_COORDS = [
        [27.7, -12.6],
        [28.2, -12.6],
        [28.2, -12.4],
        [27.7, -12.4],
        [27.7, -12.6]
    ]
    
    # Step 1: Initialize Earth Engine
    if not initialize_earth_engine():
        sys.exit(1)
    
    # Step 2: Fetch latest imagery
    composite, ndvi, metadata = fetch_latest_imagery(AOI_COORDS, days_back=30)
    
    if composite is None:
        print("\n❌ No imagery available")
        sys.exit(0)  # Exit gracefully (not an error)
    
    # Step 3: Generate download URLs
    print("\n🔗 Generating download URLs...")
    
    rgb = composite.select(['B4', 'B3', 'B2'])
    rgb_url = get_download_url(rgb, 'chingola_rgb', AOI_COORDS)
    ndvi_url = get_download_url(ndvi, 'chingola_ndvi', AOI_COORDS)
    
    if rgb_url:
        print(f"   ✓ RGB URL: {rgb_url[:80]}...")
        metadata['rgb_url'] = rgb_url
    
    if ndvi_url:
        print(f"   ✓ NDVI URL: {ndvi_url[:80]}...")
        metadata['ndvi_url'] = ndvi_url
    
    # Step 4: Upload to Supabase
    record_id = upload_to_supabase(metadata)
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Images processed: {metadata['image_count']}")
    print(f"   Date range: {metadata['start_date'][:10]} to {metadata['end_date'][:10]}")
    print(f"   Database record: {record_id}")
    print(f"   RGB URL: {'Available' if rgb_url else 'Failed'}")
    print(f"   NDVI URL: {'Available' if ndvi_url else 'Failed'}")
    
    if record_id:
        print("\n🎉 Success! Check Supabase dashboard for new data.")
        print(f"   Dashboard: {os.getenv('SUPABASE_URL', 'https://supabase.com')}")
    else:
        print("\n⚠️  Workflow completed but database update failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
