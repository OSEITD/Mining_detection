# 🔗 Using Your Existing Colab Notebook with Supabase

**Your Notebook:** https://colab.research.google.com/drive/1o4jx8GC7aDniZ0f4_zUpeQfOdg9pZn-w

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Open Your Notebook
Click here: **[Open Colab Notebook](https://colab.research.google.com/drive/1o4jx8GC7aDniZ0f4_zUpeQfOdg9pZn-w)**

---

### Step 2: Upload Model Weights

**Upload to Google Drive:**
1. Go to https://drive.google.com
2. Create folder: `Mining_Detection`
3. Upload: `models/saved_weights.pt` (6.5 MB)

**Mount Drive in Colab:**
Add this cell at the top of your notebook:
```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Copy model weights
!cp /content/drive/MyDrive/Mining_Detection/saved_weights.pt ./
print("✅ Model loaded")
```

---

### Step 3: Upload Satellite Image

**Option A - Upload to Colab (Easier):**
1. Click 📁 folder icon (left sidebar)
2. Click upload button
3. Select: `data/after/chingola_After_2025.tif` (315 MB)
4. After upload:
   ```python
   !mv chingola_After_2025.tif after.tif
   ```

**Option B - Use Google Drive:**
1. Upload image to Drive/Mining_Detection/
2. Copy to Colab:
   ```python
   !cp /content/drive/MyDrive/Mining_Detection/chingola_After_2025.tif ./after.tif
   ```

---

### Step 4: Add Supabase Integration

Add these cells to your notebook for automatic upload to Supabase:

**Cell 1: Install Supabase**
```python
!pip install -q supabase
print("✅ Supabase installed")
```

**Cell 2: Configure Supabase**
```python
from supabase import create_client
from datetime import datetime

# Your Supabase credentials
SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhiamphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAwNzM5NzksImV4cCI6MjA0NTY0OTk3OX0.MBk4KJa7PGc0qU0i66tX8IrYCRfVCmP0xd03n4C6s9w"

# Initialize client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Timestamp for this run
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

print(f"✅ Supabase connected")
print(f"📅 Timestamp: {TIMESTAMP}")
```

**Cell 3: Upload Results to Supabase (Add after prediction)**
```python
import requests

print("☁️  Uploading to Supabase...")

# After you generate predictions, upload them

# 1. Upload prediction TIFF
tiff_filename = f'prediction_{TIMESTAMP}.tif'
with open(tiff_filename, 'rb') as f:
    response = supabase.storage.from_('illegal-mining-data').upload(
        f'predictions/{tiff_filename}', 
        f, 
        {'content-type': 'image/tiff'}
    )
print(f"✅ Uploaded: {tiff_filename}")

# 2. Upload GeoJSON (if you have it)
geojson_filename = f'mining_polygons_{TIMESTAMP}.geojson'
if os.path.exists(geojson_filename):
    with open(geojson_filename, 'rb') as f:
        response = supabase.storage.from_('illegal-mining-data').upload(
            f'geojson/{geojson_filename}', 
            f, 
            {'content-type': 'application/json'}
        )
    print(f"✅ Uploaded: {geojson_filename}")

# 3. Upload visualization PNG
viz_filename = f'prediction_{TIMESTAMP}.png'
if os.path.exists(viz_filename):
    with open(viz_filename, 'rb') as f:
        response = supabase.storage.from_('illegal-mining-data').upload(
            f'visualizations/{viz_filename}', 
            f, 
            {'content-type': 'image/png'}
        )
    print(f"✅ Uploaded: {viz_filename}")

# 4. Update database
tiff_url = f"{SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/predictions/{tiff_filename}"
geojson_url = f"{SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/geojson/{geojson_filename}"
viz_url = f"{SUPABASE_URL}/storage/v1/object/public/illegal-mining-data/visualizations/{viz_filename}"

# Calculate mining statistics (use your actual values)
mining_area_ha = 45.23  # Replace with actual calculation
num_sites = 8           # Replace with actual count

update_response = supabase.table('mining_updates').insert({
    'prediction_tiff_url': tiff_url,
    'prediction_geojson_url': geojson_url,
    'mining_area_ha': float(mining_area_ha),
    'num_sites': int(num_sites),
    'ai_model_version': 'UNet-v1.0',
    'status': 'completed',
    'notes': f'Automated prediction run at {TIMESTAMP}'
}).execute()

if update_response.data:
    print(f"\n✅ Database updated (Record ID: {update_response.data[0]['id']})")
    print(f"\n🎉 UPLOAD COMPLETE!")
    print(f"\n📱 Mobile app will auto-fetch this data on next launch")
else:
    print("\n⚠️  Database update failed")
```

---

### Step 5: Run All Cells

1. Click: **Runtime → Change runtime type** → GPU (T4)
2. Click: **Runtime → Run all**
3. Wait 5-10 minutes for completion
4. Check output for ✅ success messages

---

## 📊 Expected Output

After running successfully:

```
✅ Model loaded
✅ Image loaded successfully
   Shape: (5, 3230, 5567)
   Bands: 5

🔮 Running prediction...
✅ Prediction complete

📊 Statistics:
   Mining area: 45.23 hectares
   Number of sites: 8

☁️  Uploading to Supabase...
✅ Uploaded: prediction_20251106_150000.tif
✅ Uploaded: mining_polygons_20251106_150000.geojson
✅ Uploaded: prediction_20251106_150000.png

✅ Database updated (Record ID: 8)

🎉 UPLOAD COMPLETE!
```

---

## 🔍 Verify Results

### Check Supabase Storage
1. Go to: https://ntkzaobvbsppxbljamvb.supabase.co
2. Navigate: Storage → illegal-mining-data
3. Look for files with today's timestamp

### Check Database
1. Go to: Table Editor → mining_updates
2. Look for latest record (highest ID)
3. Status should be "completed"

### Test Mobile App
1. Open Android app
2. App will auto-fetch latest predictions
3. View new mining sites on map

---

## 💡 Tips for Your Notebook

### If Using Different Variable Names
Match these in your code:
- Prediction mask: `prediction_mask`
- Mining area: `mining_area_ha`
- Number of sites: `num_sites`

### If Generating GeoJSON
After vectorizing your prediction:
```python
# Save as GeoJSON
gdf.to_file(f'mining_polygons_{TIMESTAMP}.geojson', driver='GeoJSON')
```

### If Creating Visualizations
```python
# Save plot
plt.savefig(f'prediction_{TIMESTAMP}.png', dpi=150, bbox_inches='tight')
```

---

## 🐛 Common Issues

### "File not found: after.tif"
**Solution:** Upload satellite image first (Step 3)

### "Supabase upload failed"
**Solution:** Check credentials in Cell 2

### "GPU not available"
**Solution:** Runtime → Change runtime type → GPU

### "Out of memory"
**Solution:** 
```python
import torch
torch.cuda.empty_cache()
```

---

## 📚 Full Documentation

For more help:
- **COLAB_TROUBLESHOOTING.md** - Error solutions
- **COLAB_QUICK_START.md** - Quick reference
- **COLAB_SETUP_GUIDE.md** - Detailed guide

---

## ✅ Quick Checklist

Before running:
- [ ] Model weights in Google Drive/Mining_Detection/
- [ ] Drive mounted in Colab
- [ ] Satellite image uploaded (after.tif)
- [ ] GPU enabled (Runtime → Change runtime type)
- [ ] Supabase credentials added
- [ ] Upload cells added after prediction

After running:
- [ ] Check Colab output for ✅ messages
- [ ] Verify files in Supabase storage
- [ ] Check mining_updates table for new record
- [ ] Test mobile app to see updated data

---

**Your notebook link:** https://colab.research.google.com/drive/1o4jx8GC7aDniZ0f4_zUpeQfOdg9pZn-w

**Ready to automate! Follow steps 1-5 above.** 🚀
