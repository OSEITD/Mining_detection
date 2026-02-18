# Google Earth Engine Automation Setup Guide

Complete guide to automate satellite data collection from Google Earth Engine to Supabase.

## 📋 Overview

This automation will:
1. ✅ Fetch latest Sentinel-2 imagery from Google Earth Engine (every 5 days)
2. ✅ Calculate NDVI and detect vegetation loss
3. ✅ Upload data URLs to Supabase database
4. ✅ Trigger automatic U-Net inference (optional)
5. ✅ Update mobile app with latest predictions

---

## 🛠️ Prerequisites

### 1. Google Earth Engine Account
- Go to: https://earthengine.google.com/
- Sign up with your Google account
- Wait for approval (usually instant)

### 2. Install Required Packages
```powershell
pip install earthengine-api
pip install geemap
pip install geopandas
```

### 3. Authenticate Earth Engine
```powershell
earthengine authenticate
```
- This will open a browser
- Sign in and copy the authorization code
- Paste it in the terminal

---

## 🚀 Quick Start (Local Testing)

### Step 1: Test GEE Connection
```powershell
cd "c:\Users\oseim\OneDrive\School\Final Year Project\Project\gee_automation"
python fetch_satellite_data.py
```

**Expected Output:**
```
============================================================
GOOGLE EARTH ENGINE AUTOMATION
============================================================
✅ Earth Engine initialized successfully

📅 Date Ranges:
   Before: 2016-01-01 to 2016-12-31
   After:  2025-10-07 to 2025-11-06

============================================================
FETCHING SATELLITE IMAGERY
============================================================

📡 Fetching Sentinel-2 data from 2016-01-01 to 2016-12-31
   Found 45 images
📡 Fetching Sentinel-2 data from 2025-10-07 to 2025-11-06
   Found 12 images

============================================================
EXPORTING TO GOOGLE DRIVE
============================================================
   ✅ Export task started: chingola_before_2016
   ✅ Export task started: chingola_after_20251106
   ✅ Export task started: chingola_mining_mask_20251106
```

### Step 2: Check Export Tasks
1. Go to: https://code.earthengine.google.com/tasks
2. You'll see 3 tasks (READY status)
3. Click **RUN** for each task
4. Files will be saved to Google Drive folder: `Chingola_Mining`

### Step 3: Test Full Automation
```powershell
python gee_to_supabase.py
```

This will:
- Fetch latest Sentinel-2 data
- Generate download URLs
- Upload metadata to Supabase
- Save URLs to JSON file

---

## ⏰ Automated Scheduling Options

### Option 1: GitHub Actions (Recommended - Free)

#### Setup Steps:

1. **Create Supabase Secrets on GitHub**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Add these secrets:
     - `SUPABASE_URL`: `https://ntkzaobvbsppxbljamvb.supabase.co`
     - `SUPABASE_KEY`: `eyJhbGci...` (your anon key)
     - `GEE_SERVICE_ACCOUNT`: Your GEE service account email
     - `GEE_PRIVATE_KEY`: Service account JSON key

2. **Commit and Push**
   ```powershell
   git add .github/workflows/gee_automation.yml
   git add gee_automation/
   git commit -m "Add GEE automation workflow"
   git push
   ```

3. **Enable GitHub Actions**
   - Go to your repo → Actions tab
   - Enable workflows
   - The workflow will run automatically every 5 days at 2 AM UTC

4. **Manual Trigger**
   - Go to Actions → "Automated Satellite Data Collection"
   - Click "Run workflow"

---

### Option 2: Google Cloud Scheduler (Advanced)

#### Setup Steps:

1. **Create Google Cloud Function**
   ```bash
   gcloud functions deploy gee-automation \
     --runtime python310 \
     --trigger-http \
     --entry-point main \
     --set-env-vars SUPABASE_URL=your_url,SUPABASE_KEY=your_key
   ```

2. **Create Cloud Scheduler Job**
   ```bash
   gcloud scheduler jobs create http gee-every-5-days \
     --schedule="0 2 */5 * *" \
     --uri="https://REGION-PROJECT_ID.cloudfunctions.net/gee-automation" \
     --http-method=POST
   ```

**Cost:** ~$0.10/month (very cheap)

---

### Option 3: Windows Task Scheduler (Local)

#### Setup Steps:

1. **Create Batch Script** (`run_gee_automation.bat`):
   ```batch
   @echo off
   cd "c:\Users\oseim\OneDrive\School\Final Year Project\Project\gee_automation"
   python gee_to_supabase.py
   ```

2. **Open Task Scheduler**
   - Press Win+R, type `taskschd.msc`
   - Create Basic Task
   - Name: "GEE Satellite Data Collection"
   - Trigger: Daily, repeat every 5 days
   - Action: Start a program
   - Program: `run_gee_automation.bat`

**Note:** Computer must be on for this to work

---

## 📊 Database Setup

### Create `satellite_updates` Table in Supabase

Go to Supabase SQL Editor and run:

```sql
CREATE TABLE satellite_updates (
  id BIGSERIAL PRIMARY KEY,
  collection_date TIMESTAMPTZ DEFAULT NOW(),
  satellite TEXT DEFAULT 'Sentinel-2',
  cloud_percentage DECIMAL(5,2),
  image_count INTEGER,
  download_url TEXT,
  ndvi_url TEXT,
  status TEXT DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE satellite_updates ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Allow public read access" 
ON satellite_updates FOR SELECT 
USING (true);

-- Allow authenticated inserts
CREATE POLICY "Allow authenticated inserts" 
ON satellite_updates FOR INSERT 
WITH CHECK (true);
```

---

## 🔄 Complete Workflow

### Automated Pipeline:

```
Every 5 Days:
┌─────────────────────────────────────────────────────────┐
│ 1. GitHub Actions triggers                              │
│ 2. Fetch latest Sentinel-2 from GEE                     │
│ 3. Calculate NDVI & detect mining areas                 │
│ 4. Upload download URLs to Supabase                     │
│ 5. (Optional) Trigger Colab notebook via webhook        │
│ 6. Colab runs U-Net inference on new imagery            │
│ 7. Predictions uploaded to Supabase                     │
│ 8. Mobile app auto-fetches latest predictions           │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

### Test 1: Manual Run
```powershell
python gee_to_supabase.py
```

### Test 2: Check Database
```powershell
python -c "from supabase import create_client; supabase = create_client('YOUR_URL', 'YOUR_KEY'); print(supabase.table('satellite_updates').select('*').execute().data)"
```

### Test 3: Verify URLs Work
- Copy `download_url` from database
- Paste in browser
- Should download GeoTIFF file

---

## 📱 Integration with Mobile App

### Update Mobile App to Fetch Latest Satellite Data:

Add this to your Android `MainActivity.java`:

```java
private void fetchLatestSatelliteData() {
    new Thread(() -> {
        try {
            // Fetch latest satellite update
            String url = SUPABASE_URL + "/rest/v1/satellite_updates?order=collection_date.desc&limit=1";
            
            OkHttpClient client = new OkHttpClient();
            Request request = new Request.Builder()
                .url(url)
                .addHeader("apikey", SUPABASE_KEY)
                .build();
            
            Response response = client.newCall(request).execute();
            String jsonData = response.body().string();
            
            // Parse and display
            runOnUiThread(() -> {
                displaySatelliteData(jsonData);
            });
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }).start();
}
```

---

## 🐛 Troubleshooting

### Error: "Earth Engine not authenticated"
**Solution:**
```powershell
earthengine authenticate
```

### Error: "No images found"
**Solution:**
- Check date range (may need to expand `days_back`)
- Increase `cloud_threshold` parameter
- Verify AOI coordinates are correct

### Error: "Task submission failed"
**Solution:**
- Check GEE quotas: https://code.earthengine.google.com/
- Wait a few minutes and try again
- Reduce image size/resolution

### Error: "Database table doesn't exist"
**Solution:**
- Run the SQL script above to create `satellite_updates` table

---

## 📚 Resources

- **Earth Engine Docs**: https://developers.google.com/earth-engine
- **Sentinel-2 Info**: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
- **GitHub Actions**: https://docs.github.com/en/actions
- **Supabase Storage**: https://supabase.com/docs/guides/storage

---

## ✅ Success Checklist

- [ ] Earth Engine authenticated
- [ ] Local test script works
- [ ] Export tasks appear in GEE console
- [ ] Files download to Google Drive
- [ ] Supabase `satellite_updates` table created
- [ ] Database receives metadata
- [ ] GitHub Actions workflow configured (optional)
- [ ] Mobile app fetches latest data

---

## 🎯 Next Steps

1. **Run manual test**: `python gee_to_supabase.py`
2. **Verify database**: Check Supabase dashboard
3. **Set up automation**: Choose GitHub Actions or Cloud Scheduler
4. **Integrate with U-Net**: Connect GEE → Colab → Supabase pipeline
5. **Update mobile app**: Fetch and display latest satellite data

Your complete automation pipeline is ready! 🚀
