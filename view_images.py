#!/usr/bin/env python3
"""
Quick Image Viewer - Compare 2020 vs 2025 (AOI)
Shows actual satellite imagery side-by-side
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from glob import glob

print("="*70)
print("  SATELLITE IMAGE VIEWER (2020 vs 2025)")
print("="*70)

# Find images - check all folders
possible_dirs = ['data/yearly', 'data/before', 'data/after']

image_2020 = None
image_2025 = None

# Search in all directories
for data_dir in possible_dirs:
    if os.path.exists(data_dir):
        for file in glob(os.path.join(data_dir, '*.tif')):
            if '2020' in file and image_2020 is None:
                image_2020 = file
            elif '2025' in file and image_2025 is None:
                image_2025 = file

# If we don't have 2025, try the latest monitor image
if not image_2025:
    after_dir = 'data/after' 
    if os.path.exists(after_dir):
        after_files = sorted(glob(os.path.join(after_dir, '*.tif')))
        if after_files:
            image_2025 = after_files[-1]  # Use most recent

print(f"\n Looking for images in: {data_dir}")

if image_2020:
    print(f" Found 2020: {os.path.basename(image_2020)}")
else:
    print(f"⏳ 2020 image not yet downloaded")

if image_2025:
    print(f" Found 2025: {os.path.basename(image_2025)}")
else:
    print(f"⏳ 2025 image not yet downloaded")

if not image_2020 or not image_2025:
    print("\n  Images not ready yet. Data collection may still be in progress.")
    print("   Check terminal running the data collection script")
    print(f"\n Current status:")
    if os.path.exists(data_dir):
        files = glob(os.path.join(data_dir, '*.tif'))
        print(f"   {len(files)}/6 yearly images downloaded")
        for f in files:
            file_size = os.path.getsize(f) / (1024 * 1024)
            print(f"   - {os.path.basename(f)} ({file_size:.2f} MB)")
    exit(0)

def load_and_display(filepath):
    """Load GeoTIFF and prepare for display"""
    with rasterio.open(filepath) as src:
        # Read RGB bands (assumes bands are in order: R, G, B, NIR, SWIR, NDVI, NDWI)
        red = src.read(1).astype(float)
        green = src.read(2).astype(float)
        blue = src.read(3).astype(float)
        
        # Stack RGB
        rgb = np.stack([red, green, blue], axis=-1)
        
        # Normalize to 0-1 using percentile stretch for better contrast
        for i in range(3):
            p2 = np.percentile(rgb[:, :, i], 2)
            p98 = np.percentile(rgb[:, :, i], 98)
            rgb[:, :, i] = np.clip((rgb[:, :, i] - p2) / (p98 - p2 + 1e-8), 0, 1)
        
        # Also get NIR for NDVI calculation
        if src.count >= 4:
            nir = src.read(4).astype(float)
            
            # Calculate NDVI
            ndvi = (nir - red) / (nir + red + 1e-8)
            
            return rgb, ndvi, src.meta
        
        return rgb, None, src.meta

print("\n Loading images...")

# Load images
try:
    rgb_2020, ndvi_2020, meta_2020 = load_and_display(image_2020)
    print(" Loaded 2020 image")
    
    rgb_2025, ndvi_2025, meta_2025 = load_and_display(image_2025)
    print(" Loaded 2025 image")
    
except Exception as e:
    print(f" Error loading images: {e}")
    exit(1)

# Create visualization
print("\n Creating comparison view...")

# Figure 1: Side-by-side RGB
fig1, axes = plt.subplots(1, 2, figsize=(16, 8))

axes[0].imshow(rgb_2020)
axes[0].set_title('2020 - Baseline\nTrue Color Composite', fontsize=14, fontweight='bold')
axes[0].axis('off')

axes[1].imshow(rgb_2025)
axes[1].set_title('2025 - Current\nTrue Color Composite', fontsize=14, fontweight='bold')
axes[1].axis('off')

plt.suptitle('AOI - 5 Year Comparison\n-13.0291°S, 28.6323°E', 
             fontsize=16, fontweight='bold')
plt.tight_layout()

output_rgb = 'area_2020_vs_2025_rgb.png'
plt.savefig(output_rgb, dpi=200, bbox_inches='tight')
print(f" Saved RGB comparison: {output_rgb}")

# Figure 2: NDVI comparison
if ndvi_2020 is not None and ndvi_2025 is not None:
    fig2, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 2020 NDVI
    im1 = axes[0].imshow(ndvi_2020, cmap='RdYlGn', vmin=-0.5, vmax=0.8)
    axes[0].set_title('2020 - Vegetation Health\n(NDVI)', fontsize=12, fontweight='bold')
    axes[0].axis('off')
    plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)
    
    # 2025 NDVI
    im2 = axes[1].imshow(ndvi_2025, cmap='RdYlGn', vmin=-0.5, vmax=0.8)
    axes[1].set_title('2025 - Vegetation Health\n(NDVI)', fontsize=12, fontweight='bold')
    axes[1].axis('off')
    plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)
    
    # Change detection (difference)
    ndvi_change = ndvi_2025 - ndvi_2020
    im3 = axes[2].imshow(ndvi_change, cmap='RdBu_r', vmin=-0.5, vmax=0.5)
    axes[2].set_title('Change Detection\n(Red = Vegetation Loss)', fontsize=12, fontweight='bold')
    axes[2].axis('off')
    cbar = plt.colorbar(im3, ax=axes[2], fraction=0.046, pad=0.04)
    cbar.set_label('NDVI Change', fontsize=10)
    
    plt.suptitle('Vegetation Health Analysis (2020-2025)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_ndvi = 'area_2020_vs_2025_ndvi.png'
    plt.savefig(output_ndvi, dpi=200, bbox_inches='tight')
    print(f" Saved NDVI comparison: {output_ndvi}")

# Figure 3: Overlay with change highlighting
fig3, axes = plt.subplots(1, 2, figsize=(16, 8))

# 2020 base
axes[0].imshow(rgb_2020)
axes[0].set_title('2020 - Before', fontsize=14, fontweight='bold')
axes[0].axis('off')

# 2025 with change overlay
axes[1].imshow(rgb_2025)

# Overlay areas of significant change
if ndvi_2020 is not None and ndvi_2025 is not None:
    # Detect significant vegetation loss (mining expansion)
    mining_expansion = (ndvi_2025 < -0.1) & (ndvi_2020 > 0.1)
    
    # Create red overlay for mining areas
    overlay = np.zeros((*mining_expansion.shape, 4))
    overlay[mining_expansion] = [1, 0, 0, 0.5]  # Red with 50% transparency
    
    axes[1].imshow(overlay)
    
    mining_pixels = np.sum(mining_expansion)
    mining_area_ha = mining_pixels * 100 / 10000  # 10m pixels = 100 m²
    
    axes[1].set_title(f'2025 - After\n(Red = New Mining: {mining_area_ha:.1f} ha)', 
                     fontsize=14, fontweight='bold')
else:
    axes[1].set_title('2025 - After', fontsize=14, fontweight='bold')

axes[1].axis('off')

plt.suptitle('Mining Expansion Detection - AOI', 
             fontsize=16, fontweight='bold')
plt.tight_layout()

output_overlay = 'area_2020_vs_2025_overlay.png'
plt.savefig(output_overlay, dpi=200, bbox_inches='tight')
print(f" Saved overlay comparison: {output_overlay}")

# Calculate and display statistics
print("\n" + "="*70)
print(" COMPARISON STATISTICS")
print("="*70)

if ndvi_2020 is not None and ndvi_2025 is not None:
    # 2020 stats
    mean_ndvi_2020 = np.mean(ndvi_2020)
    veg_2020 = np.sum(ndvi_2020 > 0.3) / ndvi_2020.size * 100
    mining_2020 = np.sum(ndvi_2020 < -0.1) / ndvi_2020.size * 100
    
    # 2025 stats
    mean_ndvi_2025 = np.mean(ndvi_2025)
    veg_2025 = np.sum(ndvi_2025 > 0.3) / ndvi_2025.size * 100
    mining_2025 = np.sum(ndvi_2025 < -0.1) / ndvi_2025.size * 100
    
    print(f"\n2020 BASELINE:")
    print(f"  Mean NDVI: {mean_ndvi_2020:.3f}")
    print(f"  Vegetation Cover: {veg_2020:.1f}%")
    print(f"  Mining Areas: {mining_2020:.1f}%")
    
    print(f"\n2025 CURRENT:")
    print(f"  Mean NDVI: {mean_ndvi_2025:.3f}")
    print(f"  Vegetation Cover: {veg_2025:.1f}%")
    print(f"  Mining Areas: {mining_2025:.1f}%")
    
    print(f"\nCHANGES (2020 → 2025):")
    print(f"  NDVI Change: {mean_ndvi_2025 - mean_ndvi_2020:+.3f}")
    print(f"  Vegetation Loss: {veg_2025 - veg_2020:+.1f}%")
    print(f"  Mining Expansion: {mining_2025 - mining_2020:+.1f}%")
    
    if mining_2025 > mining_2020 + 5:
        print(f"\n    SIGNIFICANT MINING EXPANSION DETECTED!")
    elif mining_2025 > mining_2020 + 2:
        print(f"\n    Moderate mining expansion detected")
    else:
        print(f"\n  ℹ  Minimal change in mining activity")

print("\n" + "="*70)
print(" VISUALIZATION COMPLETE!")
print("="*70)
print(f"\n Generated files:")
print(f"  1. {output_rgb}")
print(f"  2. {output_ndvi}")
print(f"  3. {output_overlay}")
print(f"\n Open these PNG files to view the actual satellite images!")
print(f"\n To zoom in and explore details:")
print(f"  - Open files in Windows Photos, Paint, or any image viewer")
print(f"  - Use zoom controls to see changes in detail")
print(f"  - Look for:")
print(f"    • Brown/grey areas = Mining/bare soil")
print(f"    • Green areas = Vegetation")
print(f"    • Red overlay = New mining since 2020")
print("="*70)

# Try to open the images automatically
try:
    import subprocess
    print("\n  Attempting to open images...")
    subprocess.run(['start', output_rgb], shell=True, check=False)
    subprocess.run(['start', output_ndvi], shell=True, check=False)
    subprocess.run(['start', output_overlay], shell=True, check=False)
    print(" Images should open in your default viewer")
except:
    print("\n Manually open the PNG files to view images")
