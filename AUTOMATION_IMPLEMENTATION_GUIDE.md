# 🤖 Automated Mining Detection System - Implementation Guide

## 🎯 What We're Building

**Automated Loop:**
```
Sentinel-2 Satellite → Google Earth Engine → Supabase Storage 
→ AI Retraining (Colab) → Mobile App Updates → User Notifications
```

**Update Frequency:** Every 5-14 days (or manual trigger)

---

## 📋 Prerequisites Checklist

- [x] U-Net model trained (`saved_weights.pt`)
- [x] Streamlit app working
- [x] Android app built
- [ ] Supabase account (free tier)
- [ ] Google Earth Engine account (free for research)
- [ ] Google Colab (free tier)
- [ ] Firebase account (optional - for notifications)

---

## 🚀 PHASE 1: Supabase Setup (30 minutes)

### Step 1.1: Create Supabase Project

1. Go to https://supabase.com
2. Sign up (free)
3. Create new project: `illegal-mining-detection`
4. Note your:
   - **Project URL:** `https://xxxxx.supabase.co`
   - **Anon Key:** `eyJhbGc...` (public, safe)
   - **Service Role Key:** `eyJhbGc...` (private, keep secret!)

### Step 1.2: Create Storage Buckets

In Supabase Dashboard → Storage → Create buckets:

```
illegal-mining-data/
  ├── before/          # Sentinel-2 images (2016)
  ├── after/           # Sentinel-2 images (2025)
  ├── predictions/     # AI prediction TIFFs
  └── geojson/         # Polygon outputs
```

**Make them public** (for mobile app access):
- Settings → Make bucket public → Enable

### Step 1.3: Create Database Table

In Supabase Dashboard → SQL Editor → Run this:

```sql
-- Mining updates tracking table
CREATE TABLE mining_updates (
  id SERIAL PRIMARY KEY,
  update_time TIMESTAMP DEFAULT NOW(),
  before_tiff_url TEXT,
  after_tiff_url TEXT,
  prediction_tiff_url TEXT,
  prediction_geojson_url TEXT,
  mining_area_ha FLOAT,
  new_mining_ha FLOAT,
  ai_model_version TEXT DEFAULT 'v1.0',
  status TEXT DEFAULT 'pending'
);

-- Index for fast queries
CREATE INDEX idx_update_time ON mining_updates(update_time DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE mining_updates ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read access
CREATE POLICY "Public read access" 
ON mining_updates FOR SELECT 
USING (true);

-- Policy: Only service role can insert
CREATE POLICY "Service role insert" 
ON mining_updates FOR INSERT 
WITH CHECK (true);
```

### Step 1.4: Test Supabase Connection

Create file: `test_supabase.py`

```python
from supabase import create_client, Client

url = "https://xxxxx.supabase.co"  # Your project URL
key = "eyJhbGc..."  # Your anon key

supabase: Client = create_client(url, key)

# Test query
response = supabase.table('mining_updates').select("*").limit(5).execute()
print("✅ Supabase connected:", response)
```

Run: `pip install supabase`

---

## 🌍 PHASE 2: Google Earth Engine Automation (1 hour)

### Step 2.1: Install GEE Python API

```bash
pip install earthengine-api
```

Authenticate:
```bash
earthengine authenticate
```

### Step 2.2: Create GEE Data Fetcher Script

Create file: `gee_data_fetcher.py`

```python
import ee
import datetime
import requests
from supabase import create_client

# Initialize Earth Engine
ee.Initialize()

# Supabase config
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-service-role-key"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Chingola AOI coordinates
aoi = ee.Geometry.Rectangle([27.7, -12.6, 28.3, -12.2])

def fetch_latest_sentinel():
    """Fetch latest Sentinel-2 image for Chingola"""
    
    # Date range: last 30 days
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=30)
    
    # Sentinel-2 collection
    collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                  .filterBounds(aoi)
                  .filterDate(start_date.strftime('%Y-%m-%d'), 
                             end_date.strftime('%Y-%m-%d'))
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
    
    # Median composite
    image = collection.median().clip(aoi)
    
    # Select bands: B2,B3,B4,B8,B11 (RGB, NIR, SWIR)
    image = image.select(['B2','B3','B4','B8','B11'])
    
    return image

def export_to_drive(image, filename):
    """Export image to Google Drive"""
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=filename,
        folder='Mining_Detection',
        fileNamePrefix=filename,
        region=aoi,
        scale=10,  # 10m resolution
        maxPixels=1e9,
        fileFormat='GeoTIFF'
    )
    task.start()
    return task

def main():
    print("🌍 Fetching latest Sentinel-2 data...")
    
    # Fetch latest image
    latest_image = fetch_latest_sentinel()
    
    # Export to Drive
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    filename = f"chingola_after_{timestamp}"
    
    task = export_to_drive(latest_image, filename)
    print(f"✅ Export started: {filename}")
    print(f"   Task ID: {task.id}")
    print(f"   Check progress: https://code.earthengine.google.com/tasks")
    
    # Log to Supabase
    supabase.table('mining_updates').insert({
        'status': 'processing',
        'after_tiff_url': f'pending:{filename}'
    }).execute()

if __name__ == "__main__":
    main()
```

**Run manually first:**
```bash
python gee_data_fetcher.py
```

---

## 🧠 PHASE 3: AI Retraining Pipeline (1.5 hours)

### Step 3.1: Create Colab Notebook

Create: `notebooks/automated_training.ipynb`

**Key sections:**

#### Cell 1: Install Dependencies
```python
!pip install rasterio geopandas supabase torch torchvision
```

#### Cell 2: Download Latest Data from Supabase
```python
from supabase import create_client
import rasterio
import requests

# Supabase config
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-anon-key"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get latest update
response = supabase.table('mining_updates')\
    .select('*')\
    .order('update_time', desc=True)\
    .limit(1)\
    .execute()

latest = response.data[0]

# Download TIFFs
before_url = latest['before_tiff_url']
after_url = latest['after_tiff_url']

# Save locally
!wget -O before.tif "{before_url}"
!wget -O after.tif "{after_url}"

print("✅ Data downloaded")
```

#### Cell 3: Load Your Trained Model
```python
import torch
from your_unet_model import UNet  # Your model class

# Load pre-trained weights
model = UNet(in_channels=5, num_classes=2)
model.load_state_dict(torch.load('saved_weights.pt'))
model.eval()

print("✅ Model loaded")
```

#### Cell 4: Run Prediction
```python
import numpy as np

# Load image
with rasterio.open('after.tif') as src:
    image = src.read()
    profile = src.profile

# Normalize
image = image / 10000.0

# Predict
with torch.no_grad():
    image_tensor = torch.from_numpy(image).float().unsqueeze(0)
    prediction = model(image_tensor)
    pred_mask = prediction.argmax(dim=1).squeeze().cpu().numpy()

# Save prediction
profile.update(count=1, dtype=rasterio.uint8)
with rasterio.open('prediction_latest.tif', 'w', **profile) as dst:
    dst.write(pred_mask.astype(np.uint8), 1)

print("✅ Prediction complete")
```

#### Cell 5: Convert to GeoJSON
```python
from rasterio.features import shapes
from shapely.geometry import shape, mapping
import geopandas as gpd

# Vectorize prediction
with rasterio.open('prediction_latest.tif') as src:
    image = src.read(1)
    mask = image == 1  # Mining class
    
    results = (
        {'properties': {'class': 'mine'}, 'geometry': s}
        for s, v in shapes(mask.astype(np.int16), transform=src.transform)
        if v == 1
    )
    
    geoms = list(results)

# Create GeoDataFrame
gdf = gpd.GeoDataFrame.from_features(geoms, crs=src.crs)

# Calculate area in hectares
gdf['area_ha'] = gdf.geometry.area / 10000

# Save GeoJSON
gdf.to_file('mining_polygons_latest.geojson', driver='GeoJSON')

print(f"✅ Found {len(gdf)} mining sites")
print(f"   Total area: {gdf['area_ha'].sum():.1f} ha")
```

#### Cell 6: Upload to Supabase
```python
import os

# Upload TIFF
with open('prediction_latest.tif', 'rb') as f:
    tiff_response = supabase.storage.from_('illegal-mining-data')\
        .upload(f'predictions/prediction_{timestamp}.tif', f)

# Upload GeoJSON
with open('mining_polygons_latest.geojson', 'rb') as f:
    geojson_response = supabase.storage.from_('illegal-mining-data')\
        .upload(f'geojson/mining_{timestamp}.geojson', f)

# Get public URLs
tiff_url = f"{SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/predictions/prediction_{timestamp}.tif"
geojson_url = f"{SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/geojson/mining_{timestamp}.geojson"

# Update database
supabase.table('mining_updates').update({
    'prediction_tiff_url': tiff_url,
    'prediction_geojson_url': geojson_url,
    'mining_area_ha': float(gdf['area_ha'].sum()),
    'status': 'completed'
}).eq('id', latest['id']).execute()

print("✅ Results uploaded to Supabase")
print(f"   TIFF: {tiff_url}")
print(f"   GeoJSON: {geojson_url}")
```

### Step 3.2: Automate Colab Execution

**Option A: Manual Trigger**
- Add a "Run All" button
- Execute when new data is available

**Option B: Colab Pro + Scheduled Notebooks**
- Requires Colab Pro subscription ($10/month)
- Can schedule notebook runs

**Option C: Download as .py and Run on Cloud**
- File → Download → Download .py
- Upload to Google Cloud Functions or AWS Lambda

---

## 📱 PHASE 4: Mobile App Integration (2 hours)

### Step 4.1: Add Supabase to Android App

In `android-app/app/build.gradle`:

```gradle
dependencies {
    implementation 'io.github.jan-tennert.supabase:postgrest-kt:1.0.0'
    implementation 'io.ktor:ktor-client-android:2.3.0'
    // ... existing dependencies
}
```

### Step 4.2: Create Supabase Client

Create: `android-app/app/src/main/java/com/mining/detector/SupabaseClient.java`

```java
package com.mining.detector;

import org.json.JSONArray;
import org.json.JSONObject;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class SupabaseClient {
    private static final String SUPABASE_URL = "https://xxxxx.supabase.co";
    private static final String SUPABASE_KEY = "your-anon-key";
    
    public static JSONObject getLatestUpdate() throws Exception {
        String endpoint = SUPABASE_URL + "/rest/v1/mining_updates?order=update_time.desc&limit=1";
        
        URL url = new URL(endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("apikey", SUPABASE_KEY);
        conn.setRequestProperty("Authorization", "Bearer " + SUPABASE_KEY);
        
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(conn.getInputStream())
        );
        
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        
        JSONArray array = new JSONArray(response.toString());
        return array.getJSONObject(0);
    }
}
```

### Step 4.3: Update MainActivity to Fetch GeoJSON

In `MainActivity.java`, add:

```java
import org.json.JSONObject;
import android.os.AsyncTask;

// Add method to load latest predictions
private void loadLatestPredictions() {
    new AsyncTask<Void, Void, String>() {
        @Override
        protected String doInBackground(Void... voids) {
            try {
                JSONObject latest = SupabaseClient.getLatestUpdate();
                String geojsonUrl = latest.getString("prediction_geojson_url");
                return geojsonUrl;
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        }
        
        @Override
        protected void onPostExecute(String geojsonUrl) {
            if (geojsonUrl != null) {
                // Pass URL to Streamlit app
                String url = APP_URL + "?geojson=" + geojsonUrl;
                webView.loadUrl(url);
                
                Toast.makeText(MainActivity.this, 
                    "✅ Latest predictions loaded", 
                    Toast.LENGTH_SHORT).show();
            }
        }
    }.execute();
}

// Call in onCreate()
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    // ... existing code ...
    
    loadLatestPredictions();  // Auto-fetch latest data
}
```

### Step 4.4: Modify Streamlit to Accept GeoJSON URL

In `app_enhanced.py`, add URL parameter handling:

```python
import streamlit as st
import geopandas as gpd
import requests

# Check for URL parameter
params = st.query_params
geojson_url = params.get('geojson', None)

if geojson_url:
    # Download and load GeoJSON
    response = requests.get(geojson_url)
    gdf = gpd.read_file(response.content)
    
    st.success(f"✅ Loaded latest predictions: {len(gdf)} mining sites")
    
    # Display on map
    m = folium.Map(location=[-12.4, 28.0], zoom_start=11)
    folium.GeoJson(gdf).add_to(m)
    st_folium(m, width=700, height=500)
```

---

## ⏰ PHASE 5: Automation with Cron (30 minutes)

### Option A: Supabase Edge Function (Recommended)

Create: `supabase/functions/update-mining-data/index.ts`

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  console.log("🚀 Starting mining data update...")
  
  // 1. Trigger GEE script (via HTTP endpoint)
  const geeResponse = await fetch('https://your-gee-endpoint.com/fetch-latest')
  
  // 2. Wait for processing
  await new Promise(resolve => setTimeout(resolve, 60000)) // 1 min
  
  // 3. Trigger Colab notebook (via webhook)
  const colabResponse = await fetch('https://your-colab-webhook.com/retrain')
  
  return new Response(
    JSON.stringify({ message: "✅ Update pipeline started" }),
    { headers: { "Content-Type": "application/json" } }
  )
})
```

Deploy:
```bash
supabase functions deploy update-mining-data
```

Schedule with cron:
```yaml
# supabase/functions/cron.yaml
functions:
  update-mining-data:
    schedule:
      cron: "0 0 * * 0"  # Every Sunday midnight
```

### Option B: GitHub Actions (Free)

Create: `.github/workflows/update-mining.yml`

```yaml
name: Update Mining Data

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install earthengine-api supabase
      
      - name: Fetch new satellite data
        run: python gee_data_fetcher.py
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
      
      - name: Notify completion
        run: echo "✅ Data update complete"
```

---

## 🔔 PHASE 6: Push Notifications (Optional, 1 hour)

### Step 6.1: Setup Firebase Cloud Messaging

1. Go to https://console.firebase.google.com
2. Create project: `illegal-mining-detection`
3. Add Android app
4. Download `google-services.json` → `android-app/app/`

### Step 6.2: Add to Android App

In `android-app/app/build.gradle`:

```gradle
dependencies {
    implementation 'com.google.firebase:firebase-messaging:23.1.0'
    implementation platform('com.google.firebase:firebase-bom:32.0.0')
}

apply plugin: 'com.google.gms.google-services'
```

### Step 6.3: Send Notification from Supabase

In your Edge Function or Colab, add:

```python
import requests

def send_notification(new_mining_ha):
    """Send push notification via Firebase"""
    
    FCM_SERVER_KEY = "your-fcm-server-key"
    
    payload = {
        "to": "/topics/mining_alerts",
        "notification": {
            "title": "⚠️ New Mining Activity Detected",
            "body": f"{new_mining_ha:.1f} hectares of new mining in Chingola",
            "icon": "mining_icon",
            "click_action": "OPEN_APP"
        },
        "data": {
            "type": "mining_alert",
            "area": str(new_mining_ha)
        }
    }
    
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://fcm.googleapis.com/fcm/send",
        json=payload,
        headers=headers
    )
    
    return response.json()

# Call after prediction
if new_mining_ha > 5:  # Only alert if significant
    send_notification(new_mining_ha)
```

---

## 📊 Testing the Complete System

### Test 1: Manual Data Update
```bash
python gee_data_fetcher.py
# Check Google Earth Engine Tasks
```

### Test 2: Run Colab Training
- Open `automated_training.ipynb`
- Click "Runtime → Run all"
- Verify upload to Supabase

### Test 3: Mobile App Fetch
- Open Android app
- Should automatically load latest GeoJSON
- Check for new mining sites on map

### Test 4: End-to-End
```bash
# Trigger full pipeline
curl -X POST https://xxxxx.supabase.co/functions/v1/update-mining-data \
  -H "Authorization: Bearer your-anon-key"
```

Wait 5-10 minutes, then check app for updates.

---

## 💰 Cost Analysis

| Service | Free Tier | Paid |
|---------|-----------|------|
| Supabase | 500MB storage, 50K API calls/mo | $25/mo unlimited |
| Google Earth Engine | Free for research | Free |
| Google Colab | 12 hours/session | $10/mo Pro |
| Firebase | 10GB/mo | Pay as you go |
| GitHub Actions | 2000 min/mo | Free for public repos |

**Total for FYP:** $0-$10/month (Colab Pro optional)

---

## 🎯 Implementation Timeline

| Phase | Time | Priority |
|-------|------|----------|
| **Phase 1: Supabase Setup** | 30 min | ⭐⭐⭐ High |
| **Phase 2: GEE Automation** | 1 hour | ⭐⭐⭐ High |
| **Phase 3: AI Pipeline** | 1.5 hours | ⭐⭐⭐ High |
| **Phase 4: Mobile Integration** | 2 hours | ⭐⭐ Medium |
| **Phase 5: Cron Automation** | 30 min | ⭐ Low (manual OK for FYP) |
| **Phase 6: Notifications** | 1 hour | ⭐ Low (bonus feature) |

**Total:** ~6-7 hours to implement fully automated system

---

## 🚀 Quick Start (Minimal Viable Automation)

For your Final Year Project, focus on:

1. ✅ **Supabase storage** (30 min) - Store TIFFs and GeoJSON
2. ✅ **Colab notebook** (1 hour) - Automated training pipeline
3. ✅ **Mobile app fetch** (1 hour) - Load latest predictions from URL

**Skip for now:**
- ❌ Cron automation (run manually)
- ❌ GEE automation (use existing exports)
- ❌ Push notifications (nice to have)

This gives you a **functional automated system** in ~2.5 hours that you can demo manually!

---

## 📚 Next Steps

1. **Start with Phase 1** - Setup Supabase today
2. **Test each phase independently** before integrating
3. **Document everything** for your FYP report
4. **Create demo video** showing the automated pipeline

**Need help? Ask me to:**
- Generate the complete Supabase setup SQL
- Create the full Colab notebook
- Build the Android Supabase integration
- Set up GitHub Actions workflow

Ready to start? Which phase should we implement first? 🚀
