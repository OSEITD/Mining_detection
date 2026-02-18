"""
Google Earth Engine Automation Script
Automatically downloads latest Sentinel-2 imagery for Chingola mining area
"""

import ee
import geemap
import datetime
import os
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

# Area of Interest (Chingola, Zambia)
AOI = ee.Geometry.Polygon([
    [27.7, -12.6],
    [28.2, -12.6],
    [28.2, -12.4],
    [27.7, -12.4],
    [27.7, -12.6]
])

# Date ranges
END_DATE = datetime.datetime.now()
START_DATE = END_DATE - datetime.timedelta(days=30)  # Last 30 days

# Output directory
OUTPUT_DIR = Path(__file__).parent / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================
# INITIALIZE EARTH ENGINE
# ============================================

def initialize_ee():
    """Initialize Earth Engine with authentication"""
    try:
        ee.Initialize()
        print("✅ Earth Engine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Earth Engine: {e}")
        print("   Run: earthengine authenticate")
        return False

# ============================================
# FETCH SENTINEL-2 DATA
# ============================================

def get_sentinel2_composite(aoi, start_date, end_date):
    """
    Get cloud-free Sentinel-2 composite for the area
    
    Args:
        aoi: Earth Engine geometry
        start_date: Start date (datetime)
        end_date: End date (datetime)
    
    Returns:
        Earth Engine image composite
    """
    print(f"\n📡 Fetching Sentinel-2 data from {start_date.date()} to {end_date.date()}")
    
    # Load Sentinel-2 collection
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(aoi) \
        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    
    # Check if images are available
    count = s2.size().getInfo()
    print(f"   Found {count} images")
    
    if count == 0:
        print("   ⚠️  No images found for this period")
        return None
    
    # Create median composite (reduces clouds)
    composite = s2.median().clip(aoi)
    
    # Select RGB and NIR bands
    composite = composite.select(['B4', 'B3', 'B2', 'B8'])  # Red, Green, Blue, NIR
    
    return composite

# ============================================
# CALCULATE NDVI AND DETECT CHANGES
# ============================================

def calculate_ndvi(image):
    """Calculate Normalized Difference Vegetation Index"""
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

def detect_mining_areas(before_image, after_image, threshold=-0.2):
    """
    Detect areas where vegetation decreased (potential mining)
    
    Args:
        before_image: Baseline image
        after_image: Recent image
        threshold: NDVI change threshold (negative = vegetation loss)
    
    Returns:
        Binary mask of potential mining areas
    """
    print(f"\n🔍 Detecting mining areas (NDVI threshold: {threshold})")
    
    # Calculate NDVI for both images
    before_ndvi = before_image.normalizedDifference(['B8', 'B4'])
    after_ndvi = after_image.normalizedDifference(['B8', 'B4'])
    
    # Calculate change
    ndvi_change = after_ndvi.subtract(before_ndvi)
    
    # Identify areas with significant vegetation loss
    mining_mask = ndvi_change.lt(threshold).rename('mining_mask')
    
    return mining_mask

# ============================================
# EXPORT TO GOOGLE DRIVE
# ============================================

def export_to_drive(image, description, folder='GEE_Exports', scale=10):
    """
    Export image to Google Drive
    
    Args:
        image: Earth Engine image
        description: Export task description
        folder: Drive folder name
        scale: Export resolution in meters
    """
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description,
        folder=folder,
        scale=scale,
        region=AOI,
        maxPixels=1e13,
        fileFormat='GeoTIFF'
    )
    
    task.start()
    print(f"   ✅ Export task started: {description}")
    print(f"      Check status at: https://code.earthengine.google.com/tasks")
    
    return task

# ============================================
# DOWNLOAD DIRECTLY (Alternative)
# ============================================

def download_image(image, filename, scale=10):
    """
    Download image directly using geemap
    
    Args:
        image: Earth Engine image
        filename: Output filename
        scale: Resolution in meters
    """
    output_path = OUTPUT_DIR / filename
    
    print(f"   📥 Downloading: {filename}")
    
    try:
        geemap.ee_export_image(
            image,
            filename=str(output_path),
            scale=scale,
            region=AOI,
            file_per_band=False
        )
        print(f"   ✅ Downloaded: {output_path}")
        return output_path
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return None

# ============================================
# UPLOAD TO SUPABASE
# ============================================

def upload_to_supabase(file_path, supabase_client):
    """
    Upload downloaded file to Supabase storage
    
    Args:
        file_path: Local file path
        supabase_client: Initialized Supabase client
    """
    from datetime import datetime
    
    if not file_path.exists():
        print(f"   ⚠️  File not found: {file_path}")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    remote_path = f'satellite/{file_path.stem}_{timestamp}.tif'
    
    print(f"   ☁️  Uploading to Supabase: {remote_path}")
    
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        response = supabase_client.storage.from_('illegal-mining-data').upload(
            remote_path,
            file_content,
            {
                'content-type': 'image/tiff',
                'upsert': 'true'
            }
        )
        
        public_url = f"https://ntkzaobvbsppxbljamvb.supabase.co/storage/v1/object/public/illegal-mining-data/{remote_path}"
        
        print(f"   ✅ Uploaded: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        return None

# ============================================
# MAIN AUTOMATION FUNCTION
# ============================================

def main():
    """Main automation workflow"""
    print("=" * 60)
    print("GOOGLE EARTH ENGINE AUTOMATION")
    print("=" * 60)
    
    # Initialize Earth Engine
    if not initialize_ee():
        return
    
    # Define date ranges
    # Before: 2016 (baseline)
    before_start = datetime.datetime(2016, 1, 1)
    before_end = datetime.datetime(2016, 12, 31)
    
    # After: Last 30 days
    after_end = datetime.datetime.now()
    after_start = after_end - datetime.timedelta(days=30)
    
    print(f"\n📅 Date Ranges:")
    print(f"   Before: {before_start.date()} to {before_end.date()}")
    print(f"   After:  {after_start.date()} to {after_end.date()}")
    
    # Fetch imagery
    print("\n" + "=" * 60)
    print("FETCHING SATELLITE IMAGERY")
    print("=" * 60)
    
    before_composite = get_sentinel2_composite(AOI, before_start, before_end)
    after_composite = get_sentinel2_composite(AOI, after_start, after_end)
    
    if before_composite is None or after_composite is None:
        print("\n❌ Failed to fetch imagery")
        return
    
    # Detect mining areas
    mining_mask = detect_mining_areas(before_composite, after_composite)
    
    # Option 1: Export to Google Drive (recommended for large files)
    print("\n" + "=" * 60)
    print("EXPORTING TO GOOGLE DRIVE")
    print("=" * 60)
    
    export_to_drive(
        before_composite.select(['B4', 'B3', 'B2']),
        f'chingola_before_{before_start.year}',
        folder='Chingola_Mining'
    )
    
    export_to_drive(
        after_composite.select(['B4', 'B3', 'B2']),
        f'chingola_after_{after_end.strftime("%Y%m%d")}',
        folder='Chingola_Mining'
    )
    
    export_to_drive(
        mining_mask,
        f'chingola_mining_mask_{after_end.strftime("%Y%m%d")}',
        folder='Chingola_Mining'
    )
    
    print("\n" + "=" * 60)
    print("✅ EXPORT TASKS SUBMITTED")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Go to: https://code.earthengine.google.com/tasks")
    print("2. Click 'RUN' for each export task")
    print("3. Files will be saved to your Google Drive")
    print("4. Download from Drive and upload to Supabase")
    print("\nOr use the automated workflow in gee_to_supabase.py")

if __name__ == "__main__":
    main()
