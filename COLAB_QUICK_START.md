# 🚀 Quick Start - Google Colab Automated Training

## ⚡ 5-Minute Setup

### Step 1: Upload Model to Google Drive
```
1. Go to: https://drive.google.com
2. Click: New → Folder → Name it "Mining_Detection"
3. Open the folder
4. Click: Upload files
5. Select: models/saved_weights.pt (from your PC)
6. Wait for upload to complete (6.5 MB)
```

### Step 2: Open Your Existing Colab Notebook
```
1. Open your notebook: https://colab.research.google.com/drive/1o4jx8GC7aDniZ0f4_zUpeQfOdg9pZn-w
2. Notebook is already set up and ready to use!
```

### Step 3: Enable GPU
```
1. In Colab, click: Runtime → Change runtime type
2. Hardware accelerator: GPU
3. GPU type: T4 (default)
4. Click: Save
```

### Step 4: Mount Google Drive
```python
# Add this cell at the VERY TOP of the notebook (before Cell 1)
# Click "+ Code" button to add new cell

from google.colab import drive
drive.mount('/content/drive')

# Copy model weights
!cp /content/drive/MyDrive/Mining_Detection/saved_weights.pt ./

# Verify file exists
!ls -lh saved_weights.pt

print("✅ Model loaded from Google Drive")
```

### Step 5: Run All Cells
```
1. Click: Runtime → Run all
2. When prompted "Warning: This notebook was not authored by Google"
   → Click: Run anyway
3. When Drive mount asks for permission:
   → Click: Connect to Google Drive
   → Choose your Google account
   → Click: Allow
4. Wait 5-10 minutes for completion
```

---

## 📊 Expected Output

```
✅ All packages installed
📅 Run timestamp: 20251106_150000
🔑 Supabase URL: https://ntkzaobvbsppxbljamvb.supabase.co
🧠 Model: UNet-v1.0

✅ Found latest update:
   ID: 7
   Time: 2025-11-06
   Status: completed

🖥️  Using device: cuda
✅ Model loaded: saved_weights.pt

🔮 Running prediction...
✅ Prediction complete

📊 Prediction Statistics:
   Mining area: 45.23 hectares
   Number of sites: 8

☁️  Uploading to Supabase...
   ✅ Uploaded: prediction_20251106_150000.tif
   ✅ Uploaded: mining_polygons_20251106_150000.geojson
   ✅ Uploaded: prediction_20251106_150000.png

✅ Database updated (Record ID: 8)

🎉 PIPELINE COMPLETE!
```

---

## ✅ Success Indicators

Look for these messages:
- ✅ "All packages installed"
- ✅ "Model loaded: saved_weights.pt"
- ✅ "Using device: cuda" (GPU enabled)
- ✅ "Prediction complete"
- ✅ "Database updated"
- ✅ "PIPELINE COMPLETE!"

---

## ❌ Troubleshooting

### Problem: "Model weights not found"
**Solution:**
```python
# Run this to check file location
!ls -lh /content/drive/MyDrive/Mining_Detection/

# If not there, upload saved_weights.pt to correct folder
```

### Problem: "No GPU available"
**Solution:**
```
1. Runtime → Change runtime type
2. Hardware accelerator → T4 GPU
3. Save
4. Runtime → Restart runtime
```

### Problem: "Supabase upload failed"
**Solution:**
```python
# Test connection
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
response = supabase.table('mining_updates').select('*').limit(1).execute()
print(response)
# Should show data without errors
```

---

## 🔗 Direct Links

- **Google Drive:** https://drive.google.com
- **Google Colab:** https://colab.research.google.com
- **Supabase Dashboard:** https://ntkzaobvbsppxbljamvb.supabase.co
- **Your Storage Bucket:** https://ntkzaobvbsppxbljamvb.supabase.co/project/default/storage/buckets/illegal-mining-data

---

## 📱 After Completion

1. **Check Supabase Storage**
   - Go to Storage → illegal-mining-data
   - Look for new files with today's timestamp
   - Should see 3 new files (TIFF, GeoJSON, PNG)

2. **Check Database**
   - Go to Table Editor → mining_updates
   - Look for new record (latest ID)
   - Status should be "completed"

3. **Test Mobile App**
   - Open your Android app
   - App will auto-fetch latest predictions
   - View new mining sites on map

---

## 🔄 Run Weekly

To keep predictions updated:

**Option A - Manual (Recommended)**
- Open Colab notebook once a week
- Click "Runtime → Run all"
- Takes 5-10 minutes

**Option B - Scheduled (Colab Pro)**
- Upgrade to Colab Pro ($10/month)
- Set schedule: Every Sunday 2 AM
- Runs automatically

---

## 📚 Full Documentation

For detailed instructions, see:
- **COLAB_SETUP_GUIDE.md** - Complete setup guide
- **AUTOMATION_SETUP_COMPLETE.md** - Status summary
- **PHASE1_QUICKSTART.md** - Supabase setup

---

## 💡 Pro Tips

1. **Always use GPU** - 10x faster than CPU
2. **Check file sizes** - saved_weights.pt should be ~6.5 MB
3. **Monitor storage** - You have 500 MB free tier (currently using 5 MB)
4. **Keep notebook open** - Don't close browser during run
5. **Save output** - Download visualizations before closing notebook

---

**Ready to automate! Copy saved_weights.pt to Google Drive and run the notebook.** 🚀
