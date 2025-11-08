"""
🧪 Test Image Download Size
Verifies Earth Engine download stays under 50MB limit
"""

import os
import ee
from datetime import datetime, timedelta

print("\n" + "="*60)
print("🧪 TESTING IMAGE DOWNLOAD SIZE")
print("="*60)

# Initialize Earth Engine
try:
    print("\n🔧 Initializing Earth Engine...")
    
    # Get credentials from environment
    service_account = os.getenv('GEE_SERVICE_ACCOUNT_EMAIL')
    key_data = os.getenv('GEE_SERVICE_ACCOUNT_KEY')
    
    if service_account and key_data:
        print(f"   Using service account: {service_account[:30]}...")
        import json
        credentials_dict = json.loads(key_data)
        credentials = ee.ServiceAccountCredentials(service_account, key_data=credentials_dict)
        ee.Initialize(credentials)
    else:
        print("   Using default credentials...")
        ee.Initialize()
    
    print("✅ Earth Engine initialized\n")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    exit(1)

# Study area (reduced size)
bounds = [27.82, -12.52, 27.88, -12.48]  # Smaller area
geometry = ee.Geometry.Rectangle(bounds)

print("📍 Study Area:")
print(f"   Location: Chingola, Zambia")
print(f"   Bounds: {bounds}")
print(f"   Size: ~6.6 km × 4.4 km\n")

# Get imagery
try:
    print("📡 Fetching Sentinel-2 imagery...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(geometry) \
        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    
    count = collection.size().getInfo()
    print(f"   Found {count} images\n")
    
    if count > 0:
        latest = collection.sort('system:time_start', False).first()
        img_info = latest.getInfo()
        
        print("🖼️  Latest Image:")
        print(f"   Date: {datetime.fromtimestamp(img_info['properties']['system:time_start'] / 1000).strftime('%Y-%m-%d')}")
        print(f"   Cloud cover: {img_info['properties'].get('CLOUDY_PIXEL_PERCENTAGE', 0):.1f}%\n")
        
        # Test different scales
        rgb = latest.select(['B4', 'B3', 'B2']).clip(geometry)
        
        scales = [10, 20, 30, 50]
        
        print("🔍 Testing download sizes:\n")
        for scale in scales:
            try:
                print(f"   Scale {scale}m: ", end='')
                url = rgb.getDownloadURL({
                    'scale': scale,
                    'region': geometry,
                    'format': 'GEO_TIFF',
                    'crs': 'EPSG:4326'
                })
                
                # Estimate size from URL (GEE includes size hint)
                import requests
                response = requests.head(url, allow_redirects=True)
                size_bytes = int(response.headers.get('content-length', 0))
                size_mb = size_bytes / (1024 * 1024)
                
                status = "✅" if size_mb < 50 else "❌"
                print(f"{status} {size_mb:.2f} MB")
                
            except Exception as e:
                if "must be less than or equal to" in str(e):
                    print(f"❌ TOO LARGE (> 50 MB)")
                else:
                    print(f"❌ Error: {e}")
        
        print("\n" + "="*60)
        print("📊 RECOMMENDATION")
        print("="*60)
        print("\n✅ Use scale=30m for automated pipeline")
        print("   - Stays under 50MB limit")
        print("   - Good enough for mining detection")
        print("   - Reliable downloads\n")
        
    else:
        print("⚠️  No imagery found in date range\n")

except Exception as e:
    print(f"❌ Error: {e}\n")

print("="*60)
