# Complete U-Net Mining Detection - Execution Checklist

## 📋 Pre-Training Checklist

Before you start training, ensure:

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] PyTorch installed with CUDA support (GPU recommended)
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```
- [ ] Required packages installed:
  ```bash
  pip install rasterio geopandas numpy matplotlib scipy scikit-learn tqdm
  ```
- [ ] GPU available (check with: `nvidia-smi` or `torch.cuda.is_available()`)

### Data Files Ready
- [ ] Satellite image: `data/before/chingola_Before_2016.tif` ✓
- [ ] Vector labels: `data/lable/chingola_mines.geojson` ✓
- [ ] Generated mask: `data/after/chingola_mask.tif` (from Cell 1)
- [ ] Directories exist:
  - [ ] `data/after/`
  - [ ] `models/`

### Notebook Preparation
- [ ] Open: `notebooks/train_unet.ipynb` ✓
- [ ] Cell 1 executed (creates mask) ✓
- [ ] Cell 2 executed (visualize mask) ✓
- [ ] Mask visualization looks correct
- [ ] No errors in console

---

## 🚀 Training Execution Checklist

### Phase 1: Model Initialization (Cell 5)
**Time: ~10 seconds | GPU Memory: ~100MB**

```
[ ] Cell 5: "U-Net Model Architecture"
    [ ] Expected output: Model summary with parameter count
    [ ] Check: "✓ Model works correctly!"
    [ ] Next: Proceed to Cell 6
```

**What to verify:**
- Model initialized on correct device (GPU or CPU)
- Forward pass test passes
- Output shape matches expected dimensions

### Phase 2: Data Preparation (Cell 6)
**Time: ~2-3 minutes | GPU Memory: ~1GB**

```
[ ] Cell 6: "Data Preparation for U-Net Training"
    [ ] Expected: Satellite image loaded
    [ ] Expected: Mask loaded and normalized
    [ ] Expected: Patches created (500+)
    [ ] Expected: Train/val split (80/20)
    [ ] Expected: Data loaders ready
    [ ] Check: "✓ Data loaders working correctly!"
    [ ] Next: Proceed to Cell 7
```

**What to verify:**
- Image shape: (5, 5567, 3230)
- Mask unique classes: [0, 1]
- Patch size: 256×256
- Train/val patch counts reasonable
- Class weights computed

### Phase 3: MODEL TRAINING (Cell 7) 🚨
**Time: 15-30 minutes on GPU | 2-4 hours on CPU | GPU Memory: ~2-4GB**

```
[ ] Cell 7: "U-Net Training Loop"
    
    TRAINING STARTS:
    [ ] Epoch 1/50 begins
    [ ] Training loss decreases
    [ ] Validation metrics displayed
    [ ] Best model saved after 1st epoch
    
    MONITORING (every 5 epochs):
    [ ] Train loss continues decreasing
    [ ] Val loss decreases or plateaus (not increasing)
    [ ] IoU increases over time (closer to 1.0)
    [ ] Dice increases over time (closer to 1.0)
    
    TRAINING ISSUES:
    [ ] If CUDA OOM:
        - Stop cell (Ctrl+C)
        - Reduce BATCH_SIZE to 8 in Cell 7
        - Re-run Cell 7
    
    [ ] If training stuck:
        - Reduce LEARNING_RATE to 5e-4
        - Reduce from 1e-3
    
    TRAINING ENDS:
    [ ] Completes all 50 epochs (or early stopping)
    [ ] Final model saved message
    [ ] Training history plot generated
    [ ] Message: "✓ Process completed successfully!"
    [ ] Next: Verify output files
```

**Expected Output Example:**
```
Epoch 1/50
Train Loss: 0.4521
Val Loss: 0.3854 | IoU: 0.6234 | Dice: 0.7123
✓ Best model saved (Val Loss: 0.3854)

...

Epoch 30/50
Train Loss: 0.1987
Val Loss: 0.1856 | IoU: 0.7654 | Dice: 0.8234
Early stopping triggered after 30 epochs

TRAINING COMPLETED
✓ Model saved to: ../models/unet_mining_detector.pt
```

**What to verify:**
- Loss curves show decreasing trend
- IoU improves from ~0.3 to ~0.7-0.8
- Dice improves from ~0.4 to ~0.8-0.9
- No crashes or OOM errors
- Model saved successfully

### Phase 4: Inference (Cell 8)
**Time: 5-10 minutes | GPU Memory: ~2GB**

```
[ ] Cell 8: "Inference & Change Detection"
    [ ] Expected: Model loaded successfully
    [ ] Expected: 2016 predictions generated
    [ ] Expected: prediction_2016.tif created
    [ ] Expected: 2025 predictions generated (if file exists)
    [ ] Expected: Change map generated
    [ ] Expected: Visualizations created
    [ ] Check: "✓ Inference complete!"
    [ ] Check: All output files exist
```

**What to verify:**
- Model loads without errors
- Predictions have correct shape
- Change detection shows meaningful differences
- All output files created
- Visualizations display correctly

---

## 📊 Output Files Verification

After complete execution, check these files exist:

### Model & History (Cell 7 outputs)
```
✓ models/unet_mining_detector.pt      (100-150 MB)
✓ data/after/training_history.png     (learning curves)
```

### Predictions (Cell 8 outputs)
```
✓ data/after/prediction_2016.tif      (5-10 MB)
✓ data/after/prediction_2025.tif      (5-10 MB) [if 2025 image exists]
✓ data/after/change_map.tif           (5-10 MB) [if 2025 image exists]
✓ data/after/inference_results.png    (comparison visualization)
```

### File Size Check
```
If files are <1MB:          ❌ Something went wrong
If files are 5-100MB:       ✅ Correct size
If files are >1GB:          ⚠️ Check data type
```

---

## 🎯 Performance Validation

### Expected Metrics (After Training)

**Loss Values:**
```
Initial train loss:      0.6-1.0
Final train loss:        0.1-0.3
Final val loss:          0.15-0.3
✅ GOOD if: Val loss < Train loss
❌ BAD if: Val loss >> Train loss (overfitting)
```

**IoU (Intersection over Union):**
```
Initial:      0.2-0.3
Mid-training: 0.5-0.6
Final:        0.7-0.85
✅ GOOD if: IoU > 0.7
⚠️ OK if: IoU 0.6-0.7
❌ BAD if: IoU < 0.5 (check data/labels)
```

**Dice Coefficient:**
```
Initial:      0.3-0.4
Mid-training: 0.6-0.7
Final:        0.8-0.9
✅ GOOD if: Dice > 0.8
⚠️ OK if: Dice 0.7-0.8
❌ BAD if: Dice < 0.6 (check data/labels)
```

### Mining Detection Quality
```
2016 Predictions:
- Should detect ~90% of mine areas (high recall)
- May have some false positives (low precision is OK)
- Matches visual inspection of satellite image

2025 Predictions (if available):
- Should show similar mining patterns
- New mining areas highlighted in change map
- Reclaimed areas show as removed

Change Map:
- Red pixels: Reasonable number (mining expansion)
- Blue pixels: Some areas (mining reclamation)
- White pixels: Majority (unchanged areas)
```

---

## 🔧 Troubleshooting During Execution

### Problem: CUDA Out of Memory
```
Error: "CUDA out of memory"

Solution:
1. Stop execution (Ctrl+C)
2. In Cell 7, change:
   BATCH_SIZE = 8  (from 16)
   PATCH_SIZE = 128  (from 256)
3. Re-run Cell 6 to recreate dataloaders
4. Re-run Cell 7
```

### Problem: Training Not Starting
```
Error: "No module named torch"

Solution:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
Restart kernel
Re-run Cell 7
```

### Problem: Training is Very Slow
```
If training takes >1 minute per epoch:
- Likely using CPU instead of GPU
- Check: print(torch.cuda.is_available())
- If False, install CUDA version of PyTorch

Or:
- Reduce PATCH_SIZE to 128
- Reduce NUM_WORKERS to 0
```

### Problem: Model Not Improving
```
If IoU/Dice not changing:
1. Check Cell 2 visualization - is mask correct?
2. Verify image loading in Cell 6
3. Reduce LEARNING_RATE to 5e-4
4. Increase NUM_EPOCHS to 100
5. Check class weights are computed

If still not improving:
- Dataset might be too small
- Consider data augmentation
- Check for data normalization issues
```

### Problem: Training Crashes After 10-20 Epochs
```
Likely cause: Memory leak or GPU memory issues

Solutions:
1. Reduce BATCH_SIZE
2. Use torch.cuda.empty_cache() before training
3. Restart kernel between runs
4. Check GPU memory with nvidia-smi
```

---

## ✅ Success Criteria

### Your training was SUCCESSFUL if:

#### ✅ Training Completed
- [x] All 50 epochs completed OR early stopped with good val_loss
- [x] No crashes or errors during training
- [x] Model saved to `../models/unet_mining_detector.pt`

#### ✅ Metrics Improved
- [x] Train loss decreased over epochs
- [x] Val loss decreased (or plateaued)
- [x] IoU improved from 0.3 to >0.7
- [x] Dice improved from 0.4 to >0.8

#### ✅ Files Generated
- [x] `training_history.png` shows curves
- [x] `prediction_2016.tif` created
- [x] `prediction_2025.tif` created (if 2025 image exists)
- [x] `change_map.tif` created (if 2025 image exists)
- [x] `inference_results.png` shows visualizations

#### ✅ Predictions Look Good
- [x] Predictions match visual features in satellite image
- [x] Most mines detected (few false negatives)
- [x] Change map shows reasonable mining changes

---

## 📈 Next Steps After Training

### 1. Analyze Results
```
[ ] Open training_history.png
    - Verify loss curves show convergence
    - Check IoU/Dice improvements
    
[ ] Open inference_results.png
    - Compare predictions with ground truth
    - Verify mining areas are detected
    
[ ] Open change_map.tif in GIS software (QGIS)
    - Visualize mining changes
    - Calculate area changes
```

### 2. Performance Evaluation
```
[ ] Calculate additional metrics:
    - Precision (True Positives / (TP + FP))
    - Recall (True Positives / (TP + FN))
    - F1-Score (2 * (Precision * Recall) / (Precision + Recall))
    
[ ] Compare with ground truth mask:
    - Visual inspection
    - Quantitative metrics
```

### 3. Use Model for Applications
```
[ ] Apply model to new satellite images
[ ] Track mining expansion over time
[ ] Monitor environmental impact
[ ] Generate reports with change maps
```

### 4. Improve Model (Optional)
```
[ ] Add more training data
[ ] Fine-tune hyperparameters
[ ] Try different architectures
[ ] Ensemble multiple models
[ ] Apply transfer learning
```

---

## 🐛 Emergency Debugging

If everything fails, follow this:

```python
# Cell 0: Diagnostic
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

import rasterio
with rasterio.open('../data/before/chingola_Before_2016.tif') as src:
    print(f"Image shape: {src.shape}")
    print(f"Image CRS: {src.crs}")

with rasterio.open('../data/after/chingola_mask.tif') as src:
    print(f"Mask shape: {src.shape}")
    print(f"Mask range: {src.read(1).min()}-{src.read(1).max()}")

# If all above works, issue is in training code
# Clear GPU memory and try again
torch.cuda.empty_cache()
```

---

## 🎓 Learning Resources

If you want to understand the code better:
- `UNET_GUIDE.md` - Detailed explanations
- `UNET_QUICK_START.md` - Quick reference
- Inline code comments in notebook

---

## 📞 Common Questions

**Q: Why is training slow?**
A: Likely using CPU. Install GPU version of PyTorch.

**Q: Can I stop training early?**
A: Yes, press Ctrl+C. Model will save best weights so far.

**Q: What if I want to use only CPU?**
A: It will work, but very slow (~2-4 hours). Consider reducing image/patch size.

**Q: Can I train longer for better results?**
A: Yes, increase NUM_EPOCHS to 100. Early stopping will prevent overfitting.

**Q: How do I use the trained model on new images?**
A: See Cell 8. Load model and use `predict_full_image()` function.

---

## 🏁 Final Checklist

```
BEFORE TRAINING:
[ ] All files present and verified
[ ] Dependencies installed
[ ] GPU available (optional but recommended)
[ ] Cells 1-2 completed successfully

TRAINING:
[ ] Cell 5 executed (model initialized)
[ ] Cell 6 executed (data prepared)
[ ] Cell 7 executed (training complete)
[ ] Training history plot generated

INFERENCE:
[ ] Cell 8 executed (predictions generated)
[ ] All output files created
[ ] Visualizations look reasonable

POST-TRAINING:
[ ] Metrics analyzed and documented
[ ] Results compared with ground truth
[ ] Next steps planned
```

---

**You're all set! Execute the cells and watch your model train! 🚀**

Questions? Check the documentation files or review the inline comments in the notebook.
