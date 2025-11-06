# 🔧 Google Colab Troubleshooting Guide

## 🚨 Common Errors and Solutions

---

## Error 1: "after.tif not recognized as being in a supported file format"

### Problem
```
RasterioIOError: 'after.tif' not recognized as being in a supported file format.
```

### Cause
The satellite image file is either:
- Missing (not uploaded)
- Corrupt (incomplete upload)
- Wrong format (not a GeoTIFF)
- Empty file

### Solution

**Option A: Upload File Manually (Recommended)**

1. **In Google Colab, click the folder icon** (📁) in the left sidebar
2. **Click the upload button** at the top
3. **Select file from your PC:**
   - File: `data/after/chingola_After_2025.tif`
   - Location: `C:\Users\oseim\OneDrive\School\Final Year Project\Project\data\after\`
   - Size: Should be ~315 MB

4. **After upload completes, rename the file:**
   ```python
   # Run this in a new cell
   !mv chingola_After_2025.tif after.tif
   !ls -lh after.tif  # Verify file exists
   ```

5. **Re-run the prediction cell**

**Option B: Use Google Drive**

1. **Upload image to Google Drive:**
   - Create folder: `Mining_Detection`
   - Upload: `chingola_After_2025.tif`

2. **Copy to Colab workspace:**
   ```python
   # Run this in a new cell
   !cp /content/drive/MyDrive/Mining_Detection/chingola_After_2025.tif ./after.tif
   !ls -lh after.tif  # Should show ~315 MB
   ```

3. **Re-run the prediction cell**

**Option C: Download from Supabase**

If you've already uploaded satellite images to Supabase:

```python
# Run this in a new cell
from supabase import create_client
import requests

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get the latest TIFF URL from your database
response = supabase.table('mining_updates').select('after_tiff_url').order('update_time', desc=True).limit(1).execute()

if response.data and response.data[0]['after_tiff_url']:
    url = response.data[0]['after_tiff_url']
    print(f"Downloading from: {url}")
    
    # Download file
    r = requests.get(url)
    with open('after.tif', 'wb') as f:
        f.write(r.content)
    
    print(f"Downloaded: {len(r.content)/1024/1024:.1f} MB")
else:
    print("No TIFF URL found in database")
```

---

## Error 2: "Model weights not found: saved_weights.pt"

### Problem
```
❌ Model weights not found: saved_weights.pt
```

### Solution

1. **Check if model is in Drive:**
   ```python
   !ls -lh /content/drive/MyDrive/Mining_Detection/saved_weights.pt
   ```

2. **If not found, upload to Drive:**
   - Go to https://drive.google.com
   - Navigate to `Mining_Detection` folder
   - Upload `models/saved_weights.pt` from your PC

3. **Copy to Colab:**
   ```python
   !cp /content/drive/MyDrive/Mining_Detection/saved_weights.pt ./
   !ls -lh saved_weights.pt  # Should show ~6.5 MB
   ```

4. **Re-run the model loading cell**

---

## Error 3: "No GPU available" or "Using device: cpu"

### Problem
Predictions are very slow (15+ minutes)

### Solution

1. **Enable GPU in Colab:**
   - Click: `Runtime` → `Change runtime type`
   - Hardware accelerator: **GPU**
   - GPU type: **T4** (default)
   - Click: **Save**

2. **Restart runtime:**
   - Click: `Runtime` → `Restart runtime`

3. **Re-run all cells**

4. **Verify GPU is enabled:**
   ```python
   import torch
   print(f"CUDA available: {torch.cuda.is_available()}")
   print(f"Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
   
   # Check GPU info
   !nvidia-smi
   ```

---

## Error 4: "Out of memory" during prediction

### Problem
```
RuntimeError: CUDA out of memory
```

### Solution

**Option A: Clear GPU memory**
```python
# Run this before prediction cell
import torch
torch.cuda.empty_cache()
```

**Option B: Use smaller image or patches**
```python
# If image is very large, downsample it
from skimage.transform import resize

# Reduce image size by 50%
image_small = resize(image, (image.shape[0], image.shape[1]//2, image.shape[2]//2))
```

**Option C: Process in patches**
```python
# For very large images, use tiled/sliding window prediction
# This is already implemented in the notebook's predict_full_image function
```

---

## Error 5: "Supabase upload failed"

### Problem
```
❌ Upload failed: HTTP 403
```

### Solution

1. **Check credentials:**
   ```python
   print(f"URL: {SUPABASE_URL}")
   print(f"Key length: {len(SUPABASE_KEY)}")
   ```

2. **Test connection:**
   ```python
   from supabase import create_client
   
   supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
   response = supabase.table('mining_updates').select('id').limit(1).execute()
   
   if response.data:
       print("✅ Connection successful")
   else:
       print("❌ Connection failed")
   ```

3. **Check storage bucket:**
   - Go to: https://ntkzaobvbsppxbljamvb.supabase.co
   - Navigate to: Storage → illegal-mining-data
   - Verify bucket exists and is public

4. **Verify storage policies:**
   - Bucket should have upload permissions enabled
   - Check that `supabase_storage_policies.sql` was run

---

## Error 6: "Drive mount permission denied"

### Problem
Can't access Google Drive files

### Solution

1. **Re-mount Drive:**
   ```python
   from google.colab import drive
   drive.mount('/content/drive', force_remount=True)
   ```

2. **When prompted:**
   - Click: "Connect to Google Drive"
   - Choose your account
   - Click: "Allow"

3. **Verify mount:**
   ```python
   !ls /content/drive/MyDrive/
   # Should list your Drive folders
   ```

---

## Error 7: "Package installation failed"

### Problem
```
ERROR: Could not find a version that satisfies the requirement...
```

### Solution

1. **Update pip:**
   ```python
   !pip install --upgrade pip
   ```

2. **Install packages individually:**
   ```python
   !pip install supabase
   !pip install rasterio
   !pip install geopandas
   !pip install torch torchvision
   ```

3. **Check Python version:**
   ```python
   !python --version  # Should be 3.8+
   ```

---

## General Debugging Commands

### Check File System
```python
# List all files in current directory
!ls -lh

# Check file size
!du -h after.tif

# Check file type
!file after.tif

# Check disk space
!df -h
```

### Check Memory Usage
```python
# RAM usage
!free -h

# GPU memory
!nvidia-smi
```

### Check Installed Packages
```python
!pip list | grep -E "supabase|rasterio|torch|geopandas"
```

### Test Model Loading
```python
import torch

# Load model
model = UNet(in_channels=5, num_classes=2).to(device)
model.load_state_dict(torch.load('saved_weights.pt', map_location=device))

print(f"✅ Model loaded: {sum(p.numel() for p in model.parameters())} parameters")
```

---

## Quick Fixes Checklist

Before asking for help, try these:

- [ ] **GPU enabled?** Runtime → Change runtime type → GPU
- [ ] **Drive mounted?** Run drive mount cell
- [ ] **Files uploaded?** Check folder icon (📁) for after.tif and saved_weights.pt
- [ ] **Credentials correct?** SUPABASE_URL and SUPABASE_KEY in Cell 2
- [ ] **All cells run?** Runtime → Run all (in order)
- [ ] **Packages installed?** First cell should show "✅ All packages installed"

---

## Still Having Issues?

### Check Notebook Output

Look for these success indicators:
- ✅ All packages installed
- ✅ Model loaded: saved_weights.pt
- ✅ Using device: cuda
- ✅ Image loaded successfully
- ✅ Prediction complete
- ✅ Database updated

### Common Workflow Issues

**Problem:** Cells run out of order
**Solution:** Click Runtime → Restart runtime → Run all

**Problem:** Variables undefined
**Solution:** Re-run configuration cells (Cells 1-2)

**Problem:** File paths wrong
**Solution:** All files should be in /content/ (Colab root)

---

## Test Environment Setup

Run this cell to verify your environment:

```python
import sys
import os
import torch
import rasterio
import geopandas as gpd
from supabase import create_client

print("=" * 60)
print("ENVIRONMENT CHECK")
print("=" * 60)

# Python version
print(f"\n✓ Python: {sys.version.split()[0]}")

# GPU availability
print(f"✓ CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")

# Files
print(f"\n✓ Model weights: {'✅' if os.path.exists('saved_weights.pt') else '❌'}")
print(f"✓ Satellite image: {'✅' if os.path.exists('after.tif') else '❌'}")

# Packages
try:
    import supabase
    print(f"✓ Supabase: {supabase.__version__}")
except:
    print("✗ Supabase: Not installed")

try:
    import rasterio
    print(f"✓ Rasterio: {rasterio.__version__}")
except:
    print("✗ Rasterio: Not installed")

# Connection
try:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase_client.table('mining_updates').select('id').limit(1).execute()
    print(f"✓ Supabase connection: {'✅' if response.data else '❌'}")
except Exception as e:
    print(f"✗ Supabase connection: ❌ {str(e)}")

print("\n" + "=" * 60)
```

---

## Contact & Resources

- **Documentation:** See `COLAB_SETUP_GUIDE.md` for detailed setup
- **Supabase Dashboard:** https://ntkzaobvbsppxbljamvb.supabase.co
- **Google Colab Docs:** https://colab.research.google.com/notebooks/intro.ipynb

---

**Most issues are solved by uploading the satellite image file manually!** 📁
