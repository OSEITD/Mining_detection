# 🚀 Google Colab Setup Guide - Automated Mining Detection

This guide will help you set up the automated training pipeline in Google Colab.

---

## 📋 Prerequisites

✅ Supabase account with data uploaded  
✅ Trained U-Net model (`saved_weights.pt`)  
✅ Google account (for Google Drive and Colab)

---

## 🎯 Quick Start (5 Steps)

### **Step 1: Upload Model Weights to Google Drive**

1. Open [Google Drive](https://drive.google.com)
2. Create a folder: **`Mining_Detection`**
3. Upload your model file: **`saved_weights.pt`** (from `models/` folder)
4. Your Drive structure should look like:
   ```
   My Drive/
   └── Mining_Detection/
       └── saved_weights.pt  (6.5 MB)
   ```

---

### **Step 2: Open Your Existing Colab Notebook**

1. Open your notebook directly: **[https://colab.research.google.com/drive/1o4jx8GC7aDniZ0f4_zUpeQfOdg9pZn-w](https://colab.research.google.com/drive/1o4jx8GC7aDniZ0f4_zUpeQfOdg9pZn-w)**
2. The notebook is already configured with your project setup
3. No need to upload a new notebook - use the existing one!

---

### **Step 3: Connect Google Drive**

Add this cell at the **TOP** of the notebook (before Step 1):

```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Copy model weights to Colab workspace
!cp /content/drive/MyDrive/Mining_Detection/saved_weights.pt ./
print("✅ Model weights copied to Colab")
```

**Run this cell first** - it will ask permission to access your Drive.

---

### **Step 4: Update Satellite Image Path**

The notebook is already configured with your Supabase credentials. If you need to use a local test image:

1. Upload test image to Colab:
   - Click folder icon (📁) on left sidebar
   - Click upload button
   - Select `chingola_After_2025.tif`

2. Or download from Supabase:
   ```python
   # Cell already exists in notebook - no changes needed!
   # It will download from your latest Supabase upload
   ```

---

### **Step 5: Run All Cells**

1. Click **Runtime → Run all** in Colab menu
2. Wait for completion (2-5 minutes depending on GPU)
3. Check output for:
   - ✅ Model loaded successfully
   - ✅ Prediction complete
   - ✅ Files uploaded to Supabase
   - ✅ Database updated

---

## 🔧 Configuration (Already Done!)

Your notebook is **pre-configured** with:

```python
SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJ..."  # Your anon key
MODEL_VERSION = "UNet-v1.0"
```

✅ No changes needed!

---

## 📊 Expected Output

After running all cells, you should see:

```
✅ All packages installed
📅 Run timestamp: 20251106_143025
🔑 Supabase URL: https://ntkzaobvbsppxbljamvb.supabase.co
🧠 Model: UNet-v1.0

✅ Found latest update:
   ID: 7
   Time: 2025-11-06T14:30:25
   Status: completed

📥 Downloading satellite imagery...
✅ Downloaded: after.tif (0.4 MB)

🖥️  Using device: cuda
✅ Model loaded: saved_weights.pt

📖 Loading satellite image...
   Shape: (5, 3230, 5567)
   Bands: 5
   Size: 3230 x 5567 pixels

🔮 Running prediction...
✅ Prediction complete

📊 Prediction Statistics:
   Mining pixels: 45,230
   Mining area: 45.23 hectares
   Coverage: 0.25%

💾 Saved: prediction_20251106_143025.png
💾 Saved: prediction_20251106_143025.tif

🗺️  Converting to GeoJSON...
   Found 12 polygons
   After filtering: 8 sites
   Total area: 45.23 ha
   Largest site: 12.45 ha
   Average size: 5.65 ha

✅ Saved: mining_polygons_20251106_143025.geojson

☁️  Uploading to Supabase...
   ✅ Uploaded: prediction_20251106_143025.tif
   ✅ Uploaded: mining_polygons_20251106_143025.geojson
   ✅ Uploaded: prediction_20251106_143025.png

✅ Database updated (Record ID: 8)

============================================================
🎉 PIPELINE COMPLETE!
============================================================

📊 Summary:
   Mining area detected: 45.23 hectares
   Number of sites: 8
   Files uploaded: 3 (TIFF, GeoJSON, PNG)

📱 Mobile app will auto-fetch latest data on next launch

🔗 Share GeoJSON URL: https://ntkzaobvbsppxbljamvb.supabase.co/storage/v1/object/public/illegal-mining-data/geojson/mining_polygons_20251106_143025.geojson
```

---

## 📱 Verify in Mobile App

After Colab completes:

1. Open your Android app
2. App will auto-load the latest predictions from Supabase
3. View new mining sites on the map
4. Check analytics dashboard for updated statistics

---

## 🔄 Schedule Automated Runs

### Option A: Manual (Easiest)
- Run notebook manually once a week
- Takes 2-5 minutes each time

### Option B: Google Colab Scheduled Notebooks (Colab Pro)
1. Upgrade to Colab Pro ($10/month)
2. Use scheduled notebook execution
3. Set cron schedule: Every Sunday at 2 AM

### Option C: GitHub Actions (Free)
1. Convert notebook to Python script:
   ```bash
   jupyter nbconvert --to python automated_training.ipynb
   ```
2. Create `.github/workflows/mining-detection.yml`:
   ```yaml
   name: Weekly Mining Detection
   on:
     schedule:
       - cron: '0 2 * * 0'  # Every Sunday at 2 AM
   
   jobs:
     run-detection:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
           with:
             python-version: '3.9'
         - run: pip install -r requirements.txt
         - run: python automated_training.py
   ```
3. Add secrets to GitHub:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

---

## 🐛 Troubleshooting

### Issue: "Model weights not found"
**Solution:** Make sure you ran the Drive mount cell and copied `saved_weights.pt`

```python
!ls -lh saved_weights.pt  # Check if file exists
# Should show: -rw-r--r-- 1 root root 6.5M saved_weights.pt
```

---

### Issue: "No GPU available"
**Solution:** Enable GPU in Colab

1. Click **Runtime → Change runtime type**
2. Hardware accelerator: **GPU** (T4)
3. Save
4. Restart runtime

---

### Issue: "Supabase upload failed"
**Solution:** Check storage bucket exists

```python
# Test bucket access
response = supabase.storage.list_buckets()
print(response)  # Should show 'illegal-mining-data'
```

---

### Issue: "Out of memory"
**Solution:** Reduce image size or use patches

```python
# Add this before prediction
if image.shape[1] > 5000 or image.shape[2] > 5000:
    print("⚠️  Large image detected, using tiled prediction...")
    # Use sliding window prediction (already in notebook)
```

---

## 📊 Monitoring Performance

### Check Colab Runtime
```python
# Add this cell to monitor resources
!nvidia-smi  # GPU usage
!free -h     # RAM usage
!df -h       # Disk space
```

### Expected Performance
- **GPU (T4):** 2-3 minutes for 5567×3230 image
- **CPU only:** 15-20 minutes (not recommended)
- **Memory:** ~4 GB RAM, ~2 GB GPU VRAM

---

## 📚 Next Steps

1. ✅ **Test the notebook** - Run all cells manually
2. ✅ **Verify uploads** - Check Supabase storage for new files
3. ✅ **Update mobile app** - Fetch latest data
4. ⏳ **Set up scheduling** - Choose automation method (manual, Colab Pro, or GitHub Actions)

---

## 🆘 Need Help?

Common issues:
- **Model not loading:** Check file path and Drive mount
- **Prediction failed:** Verify image format (5-band GeoTIFF)
- **Upload error:** Check Supabase credentials and bucket permissions

---

## 🎓 Understanding the Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                   AUTOMATED PIPELINE                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Download Latest Data from Supabase                  │
│     ↓                                                    │
│  2. Load U-Net Model (saved_weights.pt)                 │
│     ↓                                                    │
│  3. Run Prediction on Satellite Image                   │
│     ↓                                                    │
│  4. Convert Binary Mask → GeoJSON Polygons              │
│     ↓                                                    │
│  5. Upload Results to Supabase Storage                  │
│     ↓                                                    │
│  6. Update Database Record                              │
│     ↓                                                    │
│  7. Mobile App Auto-Fetches Latest Data                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Result:** New predictions are automatically available in your mobile app without any manual updates!

---

## ✅ Checklist

Before running the notebook:

- [ ] Uploaded `saved_weights.pt` to Google Drive
- [ ] Opened notebook in Google Colab
- [ ] Added Drive mount cell at top
- [ ] Enabled GPU runtime
- [ ] Verified Supabase credentials
- [ ] Have test satellite image ready

After successful run:

- [ ] Check Colab output for ✅ success messages
- [ ] Verify files in Supabase storage (`predictions/`, `geojson/`, `visualizations/`)
- [ ] Check database for new record in `mining_updates` table
- [ ] Open mobile app to see updated predictions
- [ ] Share GeoJSON URL if needed

---

**🎉 Ready to automate your mining detection!**

For questions or issues, refer to `PHASE1_QUICKSTART.md` or the main `AUTOMATION_IMPLEMENTATION_GUIDE.md`.
