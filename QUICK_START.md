# Quick Start Guide - Vector to Raster Conversion

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (One-time)
```bash
pip install rasterio geopandas numpy matplotlib scipy
```

### Step 2: Run the Notebook
Open `notebooks/train_unet.ipynb` and run these cells:

1. **Cell 1** - Convert vectors to mask (takes ~30 seconds)
2. **Cell 2** - Visualize results (takes ~10 seconds)
3. **Cell 5** - Quality control checks (takes ~5 seconds)

### Step 3: Check Outputs
Look in `data/after/` folder for:
- ✅ `chingola_mask.tif` - Your training mask
- ✅ `mask_visualization.png` - Verify alignment
- ✅ `mask_edge_analysis.png` - Quality report

---

## ⚙️ Quick Configuration

### Want to resample to 10m resolution?
In **Cell 1**, change:
```python
RESAMPLE_TO_10M = True  # Change from False to True
```

### Have multiple vector files (vegetation, water)?
In **Cell 3**, uncomment and add paths:
```python
VECTOR_FILES = {
    "mine": "../data/lable/chingola_mines.geojson",
    "vegetation": "../data/lable/chingola_vegetation.geojson",  # Add your file
    "water": "../data/lable/chingola_water.geojson",  # Add your file
}
```

---

## 📊 What You Should See

### Console Output (Cell 1)
```
============================================================
STEP 1: Reading Raster Properties
============================================================
Raster CRS: EPSG:4326
Raster Shape (H x W): (5567, 3230)
...

============================================================
STEP 5: Rasterizing Polygons
============================================================
✓ Rasterization complete!
  Mask shape: (5567, 3230)
  Unique values in mask: [0 1]
  Non-zero pixels: ~350,000 / 17,981,510 (2%)
```

### Visualization (Cell 2)
![Expected Output](../data/after/mask_visualization.png)

Should show:
- Left: Original satellite image
- Middle: Color-coded mask (red = mines)
- Right: Mask overlay on image

### Quality Control (Cell 5)
```
============================================================
QUALITY CONTROL: SPATIAL ALIGNMENT
============================================================

1. CRS Match: ✓ PASS
2. Transform Match: ✓ PASS
3. Dimensions Match: ✓ PASS
4. Bounds Match: ✓ PASS

============================================================
✓ ALL CHECKS PASSED - MASK IS CORRECTLY ALIGNED
============================================================
```

---

## ⚠️ Common Issues

### "ModuleNotFoundError: No module named 'rasterio'"
**Fix:** Install dependencies
```bash
pip install rasterio geopandas numpy matplotlib scipy
```

### "FileNotFoundError: [Errno 2] No such file or directory"
**Fix:** Check your file paths in Cell 1:
```python
raster_path = "../data/before/chingola_Before_2016.tif"  # Verify this exists
vector_path = "../data/lable/chingola_mines.geojson"     # Verify this exists
```

### Mask appears empty or incorrect
**Fix:** Run Cell 5 (Quality Control) to diagnose issues

---

## 🎯 Next Steps for U-Net Training

### 1. Load Your Mask
```python
import rasterio
with rasterio.open('../data/after/chingola_mask.tif') as src:
    mask = src.read(1)
```

### 2. Load Satellite Image
```python
with rasterio.open('../data/before/chingola_Before_2016.tif') as src:
    image = src.read()  # Shape: (5, 5567, 3230) - 5 bands
```

### 3. Extract Training Patches
```python
# Example: 256x256 patches
patches = []
for i in range(0, height-256, 128):  # 50% overlap
    for j in range(0, width-256, 128):
        img_patch = image[:, i:i+256, j:j+256]
        mask_patch = mask[i:i+256, j:j+256]
        
        # Skip patches with no labels
        if mask_patch.sum() > 0:
            patches.append((img_patch, mask_patch))
```

### 4. Train U-Net
```python
from torch.utils.data import Dataset, DataLoader
# Create dataset from patches
# Define U-Net model
# Train with your patches
```

### 5. Apply to 2025 Image
```python
# Predict on after image to detect changes
with rasterio.open('../data/after/chingola_After_2025.tif') as src:
    image_2025 = src.read()
    
# predictions = model.predict(image_2025)
# Compare 2016 vs 2025 predictions
```

---

## 📚 Need More Details?

- **Full Documentation:** See `README.md`
- **Code Comments:** Each cell has detailed inline comments
- **Troubleshooting:** Run Cell 5 for diagnostics

---

## ✅ Checklist

Before training your U-Net, ensure:

- [ ] Mask file created: `data/after/chingola_mask.tif`
- [ ] Visualization looks correct (Cell 2)
- [ ] All quality checks pass (Cell 5)
- [ ] Mask and image have same CRS and dimensions
- [ ] Class distribution is reasonable (~2% mines, ~98% background)

---

**Ready to train? Your mask is now ready for U-Net training!** 🎉

For questions, review the detailed documentation in `README.md`.
