# U-Net Mining Detection Model - Complete Guide

## 📊 Project Overview

You now have a **complete end-to-end U-Net pipeline** for mining area detection and change analysis in satellite imagery.

**Your Dataset:**
- 🛰️ Satellite image: 2016 (5567×3230 pixels, 5 bands)
- 🏷️ Ground truth mask: Mining polygons rasterized to binary (mine/background)
- 📅 Future image: 2025 (for change detection)

---

## 🏗️ Model Architecture

### U-Net Design
```
Input (B, 5, H, W)
    ↓
Encoder (Downsampling)
  Conv 64  → Conv 128 → Conv 256 → Conv 512 → Conv 1024
  (skip connections preserved)
    ↓
Decoder (Upsampling)
  ConvT 512 → ConvT 256 → ConvT 128 → ConvT 64
  (concatenate with skip connections)
    ↓
Output Conv (2 classes)
    ↓
Output (B, 2, H, W)  [Background, Mine]
```

### Why U-Net?
✅ **Encoder-Decoder with Skip Connections**
- Preserves fine spatial details
- Good for small datasets

✅ **Parameter Efficient**
- ~31M parameters (suitable for GPU memory)
- Faster training than ResNet/DenseNet

✅ **Perfect for Binary Segmentation**
- Mining vs. Non-mining classification
- Pixel-level predictions

---

## 📈 Complete Training Pipeline

### Step 1: Data Preparation
```python
# Load satellite image and ground truth mask
image: (5, 5567, 3230) - 5 bands normalized to [0,1]
mask: (5567, 3230) - Binary (0=background, 1=mine)

# Create non-overlapping patches (50% overlap)
Patch size: 256×256
Stride: 128 pixels
Total patches: 500+

# Filter patches with sufficient labels
Min positive pixels: 100
Useful patches: ~300-400

# Train/Validation split (spatial)
Train: 80% (3200+ patches with augmentation)
Val: 20% (800+ patches)
```

### Step 2: Data Augmentation
```python
Random augmentations applied during training:
- Horizontal flip (50% probability)
- Vertical flip (50% probability)
- 90/180/270° rotation (50% probability)
→ Increases effective training data 4-8x
```

### Step 3: Training Loop

**Configuration:**
```
Epochs: 50
Batch Size: 16
Learning Rate: 1e-3 (with decay)
Optimizer: Adam (weight_decay=1e-4)
Loss: Weighted CrossEntropyLoss
  - Class 0 (background): weight ≈ 0.5
  - Class 1 (mine): weight ≈ 10.0
Scheduler: ReduceLROnPlateau (reduce LR if no improvement)
Early stopping: 15 epochs patience
```

**Metrics:**
- **Loss:** Validates improvement during training
- **IoU (Intersection over Union):** Measures overlap accuracy
- **Dice Coefficient:** F1-score for segmentation
- **Accuracy:** Percentage of correct pixels

### Step 4: Model Checkpointing
```
✓ Best model saved when validation loss improves
✓ Early stopping prevents overfitting
✓ Checkpoint path: ../models/unet_mining_detector.pt
```

---

## 🎯 Training Output Files

After training, check these files:

| File | Purpose | Location |
|------|---------|----------|
| `training_history.png` | Loss, IoU, Dice curves | `data/after/` |
| `unet_mining_detector.pt` | Trained model weights | `models/` |

---

## 🔮 Inference and Predictions

### Prediction Method: Sliding Window
```
1. Divide full image into overlapping patches (256×256)
2. Pass each patch through U-Net
3. Average overlapping regions
4. Output: Full image segmentation mask
→ Preserves consistency at patch boundaries
```

### Generated Predictions

**On 2016 Image:**
- `prediction_2016.tif` - Model's segmentation of training image
- Validate accuracy by comparing with ground truth mask

**On 2025 Image:**
- `prediction_2025.tif` - Model's segmentation of new image
- Use for change detection analysis

**Change Detection:**
- `change_map.tif` - Pixel-level changes
  - -1: Mining removed (reclaimed/deactivated)
  - 0: Unchanged
  - 1: New mining areas

### Visualization
```
inference_results.png shows:
- 2016 satellite image
- 2016 ground truth mask
- 2016 model prediction
- 2025 satellite image (if available)
- 2025 model prediction
- Change map (2016 vs 2025)
```

---

## 📊 Expected Results

### Model Performance (Typical)
```
Validation Metrics (after ~30-50 epochs):
- Loss: 0.15-0.25
- IoU: 0.70-0.85 (70-85% overlap)
- Dice: 0.80-0.90 (80-90% similarity)
- Accuracy: 95%+ (mostly background class)
```

### Mining Detection
```
2016 Predictions:
- Background pixels: ~98%
- Mine pixels: ~2%
- Roughly matches ground truth distribution

2025 Predictions (Change):
- Shows mining expansion/reduction
- Can calculate area changes in hectares
```

---

## 🚀 Running the Notebook

### Execution Order:
1. **Cell 0 (Markdown):** Read introduction
2. **Cell 1:** Main raster/vector conversion → Creates `chingola_mask.tif`
3. **Cell 2:** Visualization → Creates `mask_visualization.png`
4. **Cell 3 (Markdown):** Read U-Net documentation
5. **Cell 4 (Markdown):** U-Net info
6. **Cell 5:** U-Net architecture → Test forward pass
7. **Cell 6:** Data preparation → Creates train/val dataloaders
8. **Cell 7:** Training loop → **MAIN TRAINING (~10-30 min on GPU)**
9. **Cell 8:** Inference → Predictions and change detection

### Computing Requirements:
| Component | GPU | CPU |
|-----------|-----|-----|
| Model size | 100MB | 100MB |
| Training time | 10-30 min | 2-4 hours |
| Inference time | 1-2 min | 5-10 min |
| Memory | 4GB | 8-16GB |

**Recommended:** NVIDIA GPU (CUDA available) for faster training

---

## 🔧 Customization Guide

### Change Model Capacity
```python
# In Cell 5 (U-Net Model)
class UNet(in_channels=5, num_classes=2, bilinear=True):
    # Reduce channels for smaller GPU memory:
    self.inc = DoubleConv(in_channels, 32)  # Instead of 64
    # This reduces parameters ~4x, but may reduce accuracy
```

### Change Training Parameters
```python
# In Cell 7 (Training Loop)
NUM_EPOCHS = 50              # Increase for better performance
BATCH_SIZE = 16              # Decrease if OOM, increase if GPU available
LEARNING_RATE = 1e-3         # Lower for finer training
PATCH_SIZE = 256             # Smaller if GPU memory limited
```

### Change Data Split
```python
VALIDATION_SPLIT = 0.2       # 20% validation, 80% training
# Adjust based on available labeled data
```

### Enable Multi-Class
```python
# If you have vegetation/water labels:
num_classes = 3  # mine, vegetation, water
CLASS_MAP = {"mine": 1, "vegetation": 2, "water": 3}
# Adjust class weights accordingly
```

---

## 📈 Performance Tips

### To Improve Accuracy:
1. **Add more labeled data** (vegetation, water classes)
2. **Use stronger augmentation** (elastic deformations, color jittering)
3. **Increase training time** (more epochs, lower learning rate)
4. **Use focal loss** (better for imbalanced classes)
5. **Ensemble multiple models** (train 3-5 models, average predictions)

### To Speed Up Training:
1. **Reduce image resolution** (256×256 → 128×128 patches)
2. **Reduce batch size** (but may hurt convergence)
3. **Use mixed precision training** (torch.cuda.amp)
4. **Reduce number of epochs** (stop early if validation plateaus)

### To Handle Overfitting:
1. **Increase dropout** in DoubleConv blocks
2. **Reduce learning rate** (0.5e-3 instead of 1e-3)
3. **Increase L2 regularization** (weight_decay=5e-4)
4. **More aggressive augmentation**

---

## 🎓 Advanced Usage

### Export Model for Deployment
```python
# Save as ONNX for deployment
import torch.onnx
torch.onnx.export(
    model, torch.randn(1, 5, 256, 256),
    "unet_model.onnx",
    input_names=['input'],
    output_names=['output']
)
```

### Use Pre-trained Backbone
```python
# Instead of training from scratch:
from torchvision.models.segmentation import deeplabv3_resnet50
model = deeplabv3_resnet50(pretrained=True, num_classes=2)
# Fine-tune with transfer learning
```

### Real-Time Inference
```python
# Optimize for inference:
model.eval()
with torch.jit.optimized_execution(False):
    predictions = model(input_tensor)
# Or use ONNX Runtime for faster inference
```

---

## 🐛 Troubleshooting

### Out of Memory (OOM)
```
Solution: Reduce BATCH_SIZE or PATCH_SIZE in Cell 7
Example: BATCH_SIZE = 8 (instead of 16)
```

### Training is very slow
```
Solution: Use GPU (check torch.cuda.is_available())
Or: Reduce PATCH_SIZE from 256 to 128
```

### Poor predictions
```
Solution:
1. Check if ground truth mask is correct (Cell 2 visualization)
2. Increase NUM_EPOCHS to 100+
3. Reduce LEARNING_RATE to 5e-4
4. Add more augmentation
```

### Model not converging
```
Solution:
1. Check class weights are computed correctly (Cell 6)
2. Visualize a few patches (Cell 6) to verify data
3. Reduce learning rate (try 5e-4 instead of 1e-3)
4. Increase batch size if possible
```

---

## 📚 References & Further Learning

### Papers:
- **U-Net Original:** [U-Net: Convolutional Networks for Biomedical Image Segmentation](https://arxiv.org/abs/1505.04597)
- **Transfer Learning:** [Torchvision Models](https://pytorch.org/vision/stable/models.html)

### Tutorials:
- [PyTorch Semantic Segmentation](https://pytorch.org/tutorials/intermediate/semantic_segmentation_tutorial.html)
- [Rasterio Documentation](https://rasterio.readthedocs.io/)
- [Change Detection with Satellite Imagery](https://www.mdpi.com/journal/remotesensing)

### Next Steps:
1. Train the model and evaluate performance
2. Compare 2016 vs 2025 predictions
3. Calculate mining area changes
4. Consider multi-class extension (vegetation, water)
5. Prepare results for publication/presentation

---

## 🎉 Summary

You now have:
✅ Complete dataset preparation pipeline
✅ State-of-the-art U-Net model implementation
✅ Full training pipeline with validation
✅ Inference and change detection capabilities
✅ Comprehensive visualizations
✅ All output files for analysis

**Ready to train your mining detection model!** 🚀

---

**Questions?** Check the inline code comments or review the notebook cells for detailed explanations.
