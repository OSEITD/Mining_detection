# Vector to Raster Mask Conversion - Project Documentation

## 📊 Project Analysis Summary

### Your Data Structure
```
Project/
├── data/
│   ├── before/
│   │   └── chingola_Before_2016.tif      # Satellite image (2016)
│   ├── after/
│   │   └── chingola_After_2025.tif       # Satellite image (2025)
│   └── lable/
│       └── chingola_mines.geojson        # Mining area polygons
├── models/
│   └── saved_weights.pt
└── notebooks/
    └── train_unet.ipynb                   # YOUR UPDATED NOTEBOOK
```

### Data Specifications

#### Satellite Image (chingola_Before_2016.tif)
- **Dimensions:** 5567 × 3230 pixels
- **Bands:** 5 (likely multispectral)
- **CRS:** EPSG:4326 (WGS84 Geographic)
- **Resolution:** ~0.00009° per pixel (~10m at this latitude)
- **Coverage:** ~32km × 50km area in Chingola, Zambia
- **Data Type:** float32

#### Vector Labels (chingola_mines.geojson)
- **Features:** 7-8 mining polygons
- **Properties:**
  - `id`: Feature identifier (1-7)
  - `name`: Mine names (e.g., "Nchanga Mi", "chingolaOP", etc.)
  - `status`: Activity status ("Active", "active", "acttive", None)
  - `area_ha`: Area in hectares (48.9 - 1744.0 ha)
  - `geometry`: MULTIPOLYGON geometries
- **CRS:** EPSG:4326 (matches raster)
- **Total Mining Area:** ~3,840 hectares

#### Key Observations
1. ⚠️ **Inconsistent status values:** "Active", "active", "acttive", None
2. ✅ **CRS already matches** between raster and vector
3. ⚠️ **Only one class** (mines) - no vegetation/water labels
4. ✅ **Good spatial coverage** of mining areas

---

## 🎯 Solution Provided

### Updated Notebook Structure

Your `train_unet.ipynb` now contains:

#### **Cell 1: Main Conversion Pipeline** ⭐
**What it does:**
- Reads satellite imagery and vector polygons
- Handles CRS reprojection (if needed)
- Normalizes inconsistent status values
- Rasterizes polygons using `rasterio.features.rasterize()`
- Preserves spatial alignment with original raster
- Optional resampling to 10m resolution
- Saves mask as GeoTIFF

**Key Features:**
- ✅ Comprehensive error checking
- ✅ Detailed progress reporting
- ✅ Memory-efficient processing
- ✅ Handles CRS mismatches automatically
- ✅ Configurable class mapping
- ✅ Optional resolution resampling

**Output:**
- `../data/after/chingola_mask.tif` - Original resolution mask
- `../data/after/chingola_mask_10m.tif` - 10m resampled mask (optional)

#### **Cell 2: Visualization** 📊
**What it does:**
- Loads satellite image and generated mask
- Creates 3-panel visualization:
  1. Original satellite image
  2. Generated mask with color-coded classes
  3. Mask overlay on satellite image
- Calculates and displays statistics
- Estimates area coverage in hectares and km²

**Output:**
- `../data/after/mask_visualization.png`
- Detailed statistics in console

#### **Cell 3: Multi-Class Mask Generation** 🔄
**What it does:**
- Combines multiple vector files (mine, vegetation, water)
- Handles class priority for overlapping polygons
- Creates unified multi-class mask

**When to use:**
- When you have multiple vector files for different classes
- Currently configured for mines only (others commented out)

#### **Cell 4: Quality Control & Validation** ✅
**What it does:**
- Verifies spatial alignment (CRS, transform, dimensions, bounds)
- Analyzes class balance (checks for imbalanced datasets)
- Edge quality assessment (detects fragmentation)
- Provides training recommendations

**Checks performed:**
1. ✅ CRS Match
2. ✅ Transform Match
3. ✅ Dimensions Match
4. ✅ Bounds Match
5. ✅ Class Balance
6. ✅ Edge Quality

**Output:**
- `../data/after/mask_edge_analysis.png`
- Detailed validation report
- Training recommendations (class weights, augmentation, patch size)

---

## 🚀 How to Use

### Step 1: Install Dependencies
```bash
pip install rasterio geopandas numpy matplotlib scipy
```

### Step 2: Run the Notebook
1. Open `notebooks/train_unet.ipynb`
2. Run Cell 1 (Main Pipeline) - Creates the mask
3. Run Cell 2 (Visualization) - Verify results
4. Run Cell 4 (Quality Control) - Validate alignment

### Step 3: Review Outputs
Check the following files in `data/after/`:
- ✅ `chingola_mask.tif` - Your training mask
- ✅ `mask_visualization.png` - Visual verification
- ✅ `mask_edge_analysis.png` - Quality assessment

---

## ⚙️ Configuration

### Customize Class Mapping
Edit in Cell 1:
```python
CLASS_MAP = {
    "mine": 1,        # Active mining areas
    "vegetation": 2,  # Vegetation cover
    "water": 3        # Water bodies
}
```

### Enable 10m Resampling
Edit in Cell 1:
```python
RESAMPLE_TO_10M = True
TARGET_RESOLUTION = 10  # meters
```

### Change Input/Output Paths
```python
raster_path = "../data/before/chingola_Before_2016.tif"
vector_path = "../data/lable/chingola_mines.geojson"
output_mask_path = "../data/after/chingola_mask.tif"
```

---

## 📋 Expected Results

### Mask Properties
- **Shape:** 5567 × 3230 pixels (same as input raster)
- **CRS:** EPSG:4326
- **Transform:** Identical to input raster
- **Data Type:** uint8
- **Values:**
  - `0` = Background (~98% of pixels)
  - `1` = Mine (~2% of pixels)

### Statistics
```
Total pixels: 17,981,510
Non-background pixels: ~350,000 (2%)

Class distribution:
  Background: ~17,630,000 pixels (98%)
  Mine:       ~350,000 pixels (2%)

Approximate area:
  Mine: ~3,840 ha (~38 km²)
```

---

## 🔍 Quality Assurance

### What to Check
1. ✅ **Visual Alignment:** Mask overlays correctly on satellite image
2. ✅ **Spatial Properties:** CRS, transform, and bounds match exactly
3. ✅ **Class Balance:** Background vs. mine ratio is reasonable
4. ✅ **Edge Quality:** Clean polygon boundaries without artifacts

### Common Issues & Solutions

#### Issue: Mask appears empty
**Solution:** 
- Check if vector and raster CRS match (code handles this automatically)
- Verify polygons are within raster bounds
- Ensure `status` field exists and is properly mapped

#### Issue: Mask misaligned with image
**Solution:**
- Run Cell 4 (Quality Control) to identify alignment issues
- Check if reprojection is needed (code does this automatically)
- Verify transform and bounds match exactly

#### Issue: Sparse labels warning
**Solution:**
- This is expected (mines cover ~2% of image)
- Use weighted loss function during training (weights provided in Cell 4)
- Consider data augmentation to increase effective training data

---

## 🎓 For U-Net Training

### Recommended Next Steps

#### 1. Use the Generated Mask
```python
# Load mask for training
with rasterio.open('data/after/chingola_mask.tif') as src:
    mask = src.read(1)  # Shape: (5567, 3230)
```

#### 2. Extract Patches
For efficient training, extract 256×256 or 512×512 patches:
```python
# Example: Extract 256x256 patches
patch_size = 256
for i in range(0, height - patch_size, patch_size):
    for j in range(0, width - patch_size, patch_size):
        img_patch = img[i:i+patch_size, j:j+patch_size]
        mask_patch = mask[i:i+patch_size, j:j+patch_size]
        # Save or use for training
```

#### 3. Apply Class Weights
Use the weights calculated in Cell 4:
```python
# Example weights (will vary based on your data)
class_weights = {
    0: 0.5,   # Background
    1: 10.0   # Mine (higher weight for minority class)
}
```

#### 4. Data Augmentation
Recommended augmentations:
- Random horizontal/vertical flips
- Random 90° rotations
- Color jittering (brightness, contrast)
- Elastic deformations

#### 5. Train U-Net
```python
# Pseudo-code
model = UNet(in_channels=5, num_classes=2)  # 5 bands, 2 classes
loss_fn = weighted_cross_entropy(weights=class_weights)
# Train model...
```

#### 6. Predict on After Image
```python
# Apply trained model to 2025 image
with rasterio.open('data/after/chingola_After_2025.tif') as src:
    img_2025 = src.read()
    
predictions = model.predict(img_2025)
# Compare with 2016 to detect mining expansion
```

---

## 📝 Technical Details

### Libraries Used
- **rasterio:** Raster I/O, CRS handling, rasterization
- **geopandas:** Vector data reading and manipulation
- **numpy:** Array operations and masking
- **matplotlib:** Visualization
- **scipy:** Edge detection (ndimage)

### Key Functions
```python
# Rasterization
rasterio.features.rasterize(shapes, out_shape, transform)

# Reprojection
rasterio.warp.reproject(source, destination, src_transform, dst_transform)

# CRS conversion
geopandas.GeoDataFrame.to_crs(target_crs)
```

### Memory Considerations
- Original image: ~362 MB (5567×3230×5 bands, float32)
- Mask: ~18 MB (5567×3230×1 band, uint8)
- 10m resampled mask: ~250 MB (larger dimensions due to higher resolution)

---

## 🐛 Troubleshooting

### Error: "No such file or directory"
**Cause:** File path is incorrect  
**Solution:** Use absolute paths or verify relative paths are correct

### Error: "CRS mismatch"
**Cause:** Vector and raster have different coordinate systems  
**Solution:** Code handles this automatically via `gdf.to_crs(raster_crs)`

### Warning: "Several features with id = X"
**Cause:** Duplicate feature IDs in GeoJSON  
**Solution:** This is handled automatically by pyogrio, doesn't affect results

### Issue: "Very sparse labels (<1%)"
**Cause:** Mining areas cover small portion of image  
**Solution:** Use class weights during training (provided in Cell 4)

---

## 📚 Additional Resources

### Tutorials
- [Rasterio Documentation](https://rasterio.readthedocs.io/)
- [GeoPandas User Guide](https://geopandas.org/en/stable/docs/user_guide.html)
- [U-Net Paper (Ronneberger et al., 2015)](https://arxiv.org/abs/1505.04597)

### Related Tasks
- Change detection (compare 2016 vs 2025)
- Time series analysis
- Multi-temporal classification
- Mining expansion monitoring

---

## 👤 Author Information

**Name:** Owen Mupeta  
**Project:** Final Year Project - Land Cover Classification  
**Institution:** [Your University]  
**Location:** Chingola, Zambia Study Area  
**Date:** October 2025

---

## 📄 License & Citation

If you use this code in your research, please cite:
```
Mupeta, O. (2025). Vector to Raster Mask Conversion for Satellite Image 
Segmentation. Final Year Project, [Your University].
```

---

**Questions or Issues?** Review the Quality Control cell output or check the generated visualizations.

Good luck with your U-Net training! 🚀
