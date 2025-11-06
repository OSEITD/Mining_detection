# 🚀 Phase 1 Quick Start Guide
## Automated Mining Detection - Minimal Viable System

**Time Required:** 2.5 hours  
**Cost:** $0 (100% free)

---

## ✅ What You'll Build

A system that:
1. Stores satellite imagery and AI predictions in the cloud (Supabase)
2. Automatically generates mining detection predictions (Google Colab)
3. Makes predictions accessible to your mobile app
4. Updates automatically when new data is available

---

## 📋 Step-by-Step Implementation

### **Step 1: Setup Supabase (30 minutes)**

#### 1.1 Create Account
1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub/Google (free)
4. Create new organization (your name)

#### 1.2 Create Project
1. Click "New Project"
2. **Name:** `illegal-mining-detection`
3. **Database Password:** (choose a strong password, save it!)
4. **Region:** Choose closest to you (e.g., Africa/Europe)
5. Wait 2-3 minutes for setup

#### 1.3 Get Your Credentials
1. Go to **Settings** → **API**
2. Copy these values:
   ```
   Project URL: https://xxxxx.supabase.co
   anon/public key: eyJhbGc...
   service_role key: eyJhbGc... (keep secret!)
   ```
3. Save them in a text file

#### 1.4 Create Database Tables
1. Go to **SQL Editor**
2. Click "New Query"
3. Open the file: `supabase_setup.sql`
4. Copy ALL the SQL code
5. Paste into SQL Editor
6. Click **Run** (bottom right)
7. Should see: "Setup complete! 1 row"

#### 1.5 Create Storage Bucket
1. Go to **Storage**
2. Click "New bucket"
3. **Name:** `illegal-mining-data`
4. **Public:** ✅ Enable (for mobile app access)
5. Click "Create bucket"
6. Inside the bucket, create folders:
   - `predictions/`
   - `geojson/`
   - `visualizations/`

#### 1.6 Test Connection
1. Open terminal in VS Code
2. Run:
   ```powershell
   pip install supabase
   ```
3. Edit `test_supabase.py`:
   - Replace `SUPABASE_URL` with your Project URL
   - Replace `SUPABASE_ANON_KEY` with your anon key
4. Run:
   ```powershell
   python test_supabase.py
   ```
5. Should see: ✅ All tests completed!

---

### **Step 2: Upload Your Model to Google Drive (10 minutes)**

#### 2.1 Prepare Files
You need:
- `saved_weights.pt` (your trained model)
- Current prediction TIFFs
- Mining GeoJSON

#### 2.2 Upload to Drive
1. Go to https://drive.google.com
2. Create folder: `Mining_Detection`
3. Upload:
   - `saved_weights.pt`
   - `chingola_After_2025.tif` (or latest)
4. Right-click → Share → Anyone with link

---

### **Step 3: Setup Google Colab Notebook (1 hour)**

#### 3.1 Open Notebook
1. Go to https://colab.research.google.com
2. File → Upload notebook
3. Upload: `notebooks/automated_training.ipynb`

#### 3.2 Mount Google Drive
Add cell at top:
```python
from google.colab import drive
drive.mount('/content/drive')

# Copy model to Colab
!cp /content/drive/MyDrive/Mining_Detection/saved_weights.pt ./
!cp /content/drive/MyDrive/Mining_Detection/chingola_After_2025.tif ./after.tif
```

#### 3.3 Configure Credentials
In Cell 2 (Configuration), update:
```python
SUPABASE_URL = "https://your-actual-url.supabase.co"
SUPABASE_KEY = "your-actual-key"
```

#### 3.4 Run Entire Notebook
1. Click **Runtime** → **Run all**
2. Wait 5-10 minutes
3. Should see: 🎉 PIPELINE COMPLETE!

#### 3.5 Verify Results
Check Supabase:
1. Go to **Storage** → `illegal-mining-data`
2. Should see new files:
   - `predictions/prediction_YYYYMMDD_HHMMSS.tif`
   - `geojson/mining_polygons_YYYYMMDD_HHMMSS.geojson`
   - `visualizations/prediction_YYYYMMDD_HHMMSS.png`

3. Go to **Table Editor** → `mining_updates`
4. Should see new record with URLs

---

### **Step 4: Update Streamlit App (1 hour)**

#### 4.1 Install Supabase Package
```powershell
pip install supabase
```

#### 4.2 Add Supabase Integration to app_enhanced.py

Add at the top:
```python
from supabase import create_client
import io

# Supabase config
SUPABASE_URL = "https://your-url.supabase.co"
SUPABASE_KEY = "your-anon-key"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
```

Add new function:
```python
def load_latest_predictions():
    """Fetch latest predictions from Supabase"""
    try:
        # Get latest update
        response = supabase.table('mining_updates') \
            .select('*') \
            .order('update_time', desc=True) \
            .limit(1) \
            .execute()
        
        if response.data:
            latest = response.data[0]
            geojson_url = latest['prediction_geojson_url']
            
            # Download GeoJSON
            import requests
            geojson_response = requests.get(geojson_url)
            
            if geojson_response.status_code == 200:
                return geojson_response.json(), latest
        
        return None, None
    except Exception as e:
        st.error(f"Failed to load predictions: {e}")
        return None, None
```

Add in sidebar:
```python
with st.sidebar:
    st.header("🔄 Auto-Update")
    
    if st.button("🔄 Fetch Latest Predictions"):
        with st.spinner("Loading from Supabase..."):
            geojson_data, metadata = load_latest_predictions()
            
            if geojson_data:
                st.success(f"✅ Loaded predictions from {metadata['update_time']}")
                st.metric("Mining Area", f"{metadata['mining_area_ha']:.1f} ha")
                st.metric("Sites Detected", metadata['num_sites'])
                
                # Store in session state
                st.session_state['latest_geojson'] = geojson_data
                st.session_state['latest_metadata'] = metadata
            else:
                st.warning("No predictions found")
```

Add in main area:
```python
# Check for auto-loaded predictions
if 'latest_geojson' in st.session_state:
    st.info("📡 Using latest predictions from Supabase")
    
    geojson_data = st.session_state['latest_geojson']
    metadata = st.session_state['latest_metadata']
    
    # Display on map
    import folium
    from streamlit_folium import st_folium
    
    m = folium.Map(location=[-12.4, 28.0], zoom_start=11)
    folium.GeoJson(
        geojson_data,
        style_function=lambda x: {
            'fillColor': 'red',
            'color': 'darkred',
            'weight': 2,
            'fillOpacity': 0.5
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=['area_ha'],
            aliases=['Area (ha):'],
            localize=True
        )
    ).add_to(m)
    
    st_folium(m, width=700, height=500)
```

#### 4.3 Test in Browser
```powershell
streamlit run app_enhanced.py --server.address=0.0.0.0
```

Click "🔄 Fetch Latest Predictions" in sidebar.

---

### **Step 5: Update Android App (Optional - 30 minutes)**

#### 5.1 Add Internet Permission
Already added in `AndroidManifest.xml`

#### 5.2 Create Supabase Utility Class

Create file: `android-app/app/src/main/java/com/mining/detector/SupabaseHelper.java`

```java
package com.mining.detector;

import org.json.JSONArray;
import org.json.JSONObject;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class SupabaseHelper {
    private static final String SUPABASE_URL = "https://your-url.supabase.co";
    private static final String SUPABASE_KEY = "your-anon-key";
    
    public static String getLatestGeoJsonUrl() {
        try {
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
            if (array.length() > 0) {
                JSONObject latest = array.getJSONObject(0);
                return latest.getString("prediction_geojson_url");
            }
            
            return null;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
```

#### 5.3 Update MainActivity.java

Add method:
```java
private void loadLatestPredictions() {
    new Thread(() -> {
        String geojsonUrl = SupabaseHelper.getLatestGeoJsonUrl();
        
        runOnUiThread(() -> {
            if (geojsonUrl != null) {
                // Pass URL to Streamlit app
                String url = APP_URL + "?geojson=" + Uri.encode(geojsonUrl);
                webView.loadUrl(url);
            } else {
                webView.loadUrl(APP_URL);
            }
        });
    }).start();
}
```

Call in `onCreate()`:
```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    // ... existing code ...
    
    loadLatestPredictions();  // Auto-fetch latest
}
```

#### 5.4 Rebuild APK
```powershell
cd "C:\Users\oseim\OneDrive\School\Final Year Project\Project\android-app"
.\gradlew assembleDebug
```

---

## 🎉 You're Done! Test the System

### Test 1: Colab → Supabase
1. Run Colab notebook
2. Check Supabase storage for new files
3. Check `mining_updates` table for new record

### Test 2: Streamlit → Supabase
1. Open Streamlit app
2. Click "🔄 Fetch Latest Predictions"
3. Should see map update with new data

### Test 3: Android → Supabase
1. Install APK on phone
2. Open app
3. Should auto-load latest predictions

### Test 4: End-to-End
1. Upload new satellite image to Supabase storage
2. Run Colab notebook
3. Open mobile app → Should see updated predictions

---

## 📊 Success Metrics

You've successfully implemented automation if:
- ✅ Supabase stores your predictions
- ✅ Colab notebook runs without errors
- ✅ Streamlit app fetches latest data
- ✅ Android app displays predictions
- ✅ System works without manual file transfers

---

## 🔄 Running Updates

**Manual Trigger (Recommended for FYP):**
1. Get new satellite imagery (every 2-4 weeks)
2. Upload to Supabase storage
3. Run Colab notebook (5-10 minutes)
4. Users open app → Auto-updates!

**Frequency:**
- **For demo:** Run once before presentation
- **For testing:** Run 2-3 times with different dates
- **For production:** Weekly/monthly via cron (Phase 5)

---

## 💡 Tips for Your FYP Report

**What to document:**
1. ✅ Architecture diagram (Sentinel-2 → GEE → Supabase → Colab → App)
2. ✅ Screenshots of Supabase dashboard
3. ✅ Colab notebook output
4. ✅ Mobile app fetching latest data
5. ✅ Cost analysis ($0!)

**Innovation points:**
- ✅ Cloud-based automated pipeline
- ✅ Serverless architecture (no servers to maintain)
- ✅ Real-time updates to mobile app
- ✅ Scalable to other regions
- ✅ Version control for predictions

---

## 🆘 Troubleshooting

### Problem: Supabase connection fails
**Solution:** Check URL and API key are correct, test with `test_supabase.py`

### Problem: Colab can't find model weights
**Solution:** Mount Google Drive, check file path

### Problem: Streamlit doesn't show predictions
**Solution:** Check console for errors, verify Supabase URL

### Problem: Android app shows blank
**Solution:** Check IP address, verify Streamlit is running

---

## 🚀 Next Steps (Optional)

After completing Phase 1, you can add:
- **Phase 2:** Google Earth Engine automation (auto-fetch satellite data)
- **Phase 5:** GitHub Actions cron (auto-run weekly)
- **Phase 6:** Push notifications (alert users of new mining)

But **Phase 1 alone is sufficient** for an excellent FYP demo! 🎓

---

## 📞 Need Help?

If stuck, check:
1. ✅ All credentials are correct (URL, keys)
2. ✅ Supabase bucket is public
3. ✅ Files uploaded successfully
4. ✅ Internet connection stable

**You've got this!** 💪

Ready to start? Begin with **Step 1: Setup Supabase** 🚀
