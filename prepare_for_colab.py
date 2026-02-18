"""
Prepare Files for Google Colab Upload

This script:
1. Checks if model weights exist
2. Creates a zip file with all necessary files for Colab
3. Provides upload instructions
"""

import os
import zipfile
from pathlib import Path

print("="*60)
print("PREPARING FILES FOR GOOGLE COLAB")
print("="*60)

# Check model weights
model_path = "models/saved_weights.pt"
if os.path.exists(model_path):
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"\n✅ Model weights found: {model_path}")
    print(f"   Size: {size_mb:.1f} MB")
else:
    print(f"\n❌ Model weights not found: {model_path}")
    print("   Please train the model first or place saved_weights.pt in models/")
    exit(1)

# Check test image
test_image = "data/after/chingola_After_2025.tif"
has_test_image = os.path.exists(test_image)

if has_test_image:
    size_mb = os.path.getsize(test_image) / (1024 * 1024)
    print(f"\n✅ Test image found: {test_image}")
    print(f"   Size: {size_mb:.1f} MB")
else:
    print(f"\n⚠️  Test image not found: {test_image}")
    print("   The notebook will download images from Supabase instead")

# Check notebook
notebook_path = "notebooks/automated_training.ipynb"
if os.path.exists(notebook_path):
    print(f"\n✅ Notebook found: {notebook_path}")
else:
    print(f"\n❌ Notebook not found: {notebook_path}")
    exit(1)

# Create zip file
print("\n" + "="*60)
print("CREATING COLAB PACKAGE")
print("="*60)

zip_filename = "colab_mining_detection.zip"
files_to_zip = [
    (model_path, "saved_weights.pt"),
    (notebook_path, "automated_training.ipynb"),
    ("COLAB_SETUP_GUIDE.md", "COLAB_SETUP_GUIDE.md"),
]

# Add test image if it exists
if has_test_image:
    files_to_zip.append((test_image, "chingola_After_2025.tif"))

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file_path, archive_name in files_to_zip:
        if os.path.exists(file_path):
            zipf.write(file_path, archive_name)
            print(f"   ✅ Added: {archive_name}")

zip_size = os.path.getsize(zip_filename) / (1024 * 1024)
print(f"\n✅ Package created: {zip_filename}")
print(f"   Total size: {zip_size:.1f} MB")

# Instructions
print("\n" + "="*60)
print("NEXT STEPS - GOOGLE COLAB SETUP")
print("="*60)

print("\n📋 Your Existing Colab Notebook:")
print("   https://colab.research.google.com/drive/1o4jx8GC7aDniZ0f4_zUpeQfOdg9pZn-w")

print("\n📋 Steps to Use Your Notebook:")
print("   1. Open the Colab link above")
print("   2. Upload saved_weights.pt to Google Drive/Mining_Detection/")
print("   3. Upload chingola_After_2025.tif to Colab or Drive")
print("   4. Update Supabase credentials in the notebook (if needed)")
print("   5. Runtime → Run all")

print("\n📚 Full Instructions:")
print("   Open COLAB_SETUP_GUIDE.md for detailed setup steps")

print("\n" + "="*60)
print("✅ PREPARATION COMPLETE")
print("="*60)

print("\n🎯 Quick Start:")
print("   1. Open: https://colab.research.google.com/drive/1o4jx8GC7aDniZ0f4_zUpeQfOdg9pZn-w")
print("   2. Upload saved_weights.pt → Google Drive/Mining_Detection/")
print("   3. Add Drive mount cell at top:")
print("      from google.colab import drive")
print("      drive.mount('/content/drive')")
print("      !cp /content/drive/MyDrive/Mining_Detection/saved_weights.pt ./")
print("   4. Upload satellite image (chingola_After_2025.tif)")
print("   5. Runtime → Run all")
print("\n📱 After completion, your mobile app will auto-load the latest predictions!")
