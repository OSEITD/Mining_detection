# U-Net Quick Start - 5 Minutes to Training

## 🚀 Quick Steps

### 1. Install Dependencies (One-time)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install scikit-learn tqdm
```

### 2. Open Your Notebook
```
notebooks/train_unet.ipynb
```

### 3. Run These Cells in Order

| # | Cell Name | Action | Time |
|---|-----------|--------|------|
| 1 | Raster Conversion | Run | 30s |
| 2 | Visualization | Run | 10s |
| 5 | U-Net Model | Run | 10s |
| 6 | Data Preparation | Run | 2min |
| 7 | **Training Loop** | **Run** | **15-30min** |
| 8 | Inference | Run | 5min |

---

## 📊 What Happens When You Train

### Training Output:
```
Epoch 1/50
Train Loss: 0.4521
Val Loss: 0.3854 | IoU: 0.6234 | Dice: 0.7123
✓ Best model saved (Val Loss: 0.3854)

Epoch 2/50
Train Loss: 0.3987
Val Loss: 0.3456 | IoU: 0.6567 | Dice: 0.7456
✓ Best model saved (Val Loss: 0.3456)

...
[continues for ~30-50 epochs]

TRAINING COMPLETED
✓ Model saved to: ../models/unet_mining_detector.pt
```

### After Training:
```
Files created:
✓ ../models/unet_mining_detector.pt       (trained model)
✓ ../data/after/training_history.png      (performance curves)
✓ ../data/after/prediction_2016.tif       (predictions on 2016)
✓ ../data/after/prediction_2025.tif       (predictions on 2025)
✓ ../data/after/change_map.tif            (mining changes)
✓ ../data/after/inference_results.png     (visual comparison)
```

---

## 🎯 Expected Performance

**After ~30 epochs:**
- Validation Loss: ~0.20-0.30
- Validation IoU: ~70-80%
- Validation Dice: ~80-90%
- Accuracy: >95% (mostly background)

**Mining Detection:**
- Correctly identifies most mining areas
- Some false positives/negatives possible
- Change detection shows mining expansion

---

## ⚙️ Tweaking Performance

### If Training is Slow
```python
# In Cell 7, change:
BATCH_SIZE = 8              # Reduce from 16
PATCH_SIZE = 128            # Reduce from 256
```

### If Training is Not Converging
```python
# In Cell 7, change:
LEARNING_RATE = 5e-4        # Reduce from 1e-3
NUM_EPOCHS = 100            # Increase from 50
```

### If Training Stops Too Early
```python
# In Cell 7, change:
patience = 25               # Increase from 15
```

---

## 🔍 Monitoring Training

### Watch for Good Signs:
- ✅ Train loss decreases each epoch
- ✅ Validation loss decreases initially
- ✅ IoU increases over time
- ✅ Dice coefficient increases over time

### Watch for Problems:
- ❌ Train loss stuck or increasing → Learning rate too high
- ❌ Validation loss worse than train loss → Overfitting
- ❌ IoU/Dice not improving → Model capacity too small
- ❌ Training stops early → Increase patience parameter

---

## 📈 Interpreting Results

### Training History Graph:
```
Loss curves:
- Should show decreasing trend
- Validation loss should be similar to train loss
- Gap indicates overfitting (increase dropout/augmentation)

IoU & Dice curves:
- Should show increasing trend
- Higher is better (closer to 1.0)
- Plateau indicates convergence
```

### Prediction Maps:
```
Red areas = Predicted mines
Blue areas = Predicted background
Darker/brighter = Higher confidence

Compare with:
- Ground truth mask (Cell 2)
- Visual inspection of satellite image
- Detected changes between 2016 and 2025
```

### Change Detection:
```
Red pixels = NEW mining areas (expansion)
Blue pixels = Mining REMOVED (reclamation)
White pixels = UNCHANGED

Useful for:
- Monitoring mining expansion
- Environmental impact assessment
- Change analysis between years
```

---

## 💾 Save & Load Model

### Save After Training:
```python
# Automatic during training!
# Location: ../models/unet_mining_detector.pt
```

### Load Model Later:
```python
model = UNet(in_channels=5, num_classes=2)
model.load_state_dict(torch.load('../models/unet_mining_detector.pt'))
model.eval()

# Use for predictions on new images
```

---

## 🎓 Understanding the Model

### Input
- 5-band satellite image patches (256×256 pixels)
- Each pixel = [B1, B2, B3, B4, B5] values in range [0, 1]

### Processing
- Encoder: Downsamples 5 → 64 → 128 → 256 → 512 → 1024 channels
- Bottleneck: Learns high-level features at 1024 channels
- Decoder: Upsamples back to spatial resolution
- Skip connections: Preserve fine spatial details

### Output
- 2-class probability map (256×256 pixels)
- Class 0: Background (vegetation, water, non-mining)
- Class 1: Mining areas
- Final prediction: Argmax of the two classes

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| CUDA out of memory | Reduce BATCH_SIZE to 8 or 4 |
| Training very slow | Check GPU usage with `nvidia-smi` |
| Poor predictions | Increase NUM_EPOCHS, reduce LEARNING_RATE |
| Model not improving | Check if mask is correct (Cell 2 visualization) |
| ImportError (torch) | `pip install torch --index-url https://download.pytorch.org/whl/cu118` |

---

## 🏁 Final Checklist

Before running training:
- [ ] Mask created (`chingola_mask.tif` exists)
- [ ] Mask visualization looks correct (Cell 2)
- [ ] PyTorch installed (`import torch` works)
- [ ] GPU available (optional but recommended)
- [ ] `models/` directory exists or will be created

---

## ✅ Success Criteria

Your training was **successful** if:
1. ✅ Model trained for all 50 epochs (or stopped early with good val loss)
2. ✅ Training history PNG shows decreasing loss curves
3. ✅ Model weights saved to `../models/unet_mining_detector.pt`
4. ✅ Predictions generated for 2016 and 2025 images
5. ✅ Change map shows meaningful differences

---

**Ready? Start with Cell 1 and run through Cell 8!** 🚀

For detailed explanations, see `UNET_GUIDE.md`
