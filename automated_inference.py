"""
🤖 Automated Mining Detection Pipeline
Runs U-Net inference on latest satellite imagery and sends notifications
"""

import os
import sys
import json
import ee
import torch
import torch.nn as nn
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import requests
from PIL import Image
import cv2
from supabase import create_client
import argparse

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntkzaobvbsppxbljamvb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw")

# Study area coordinates (Chingola, Zambia)
# Reduced area size for faster downloads (< 50MB limit)
STUDY_AREA = {
    'name': 'Chingola, Zambia',
    'latitude': -12.5,
    'longitude': 27.85,
    'bounds': [27.82, -12.52, 27.88, -12.48]  # [min_lon, min_lat, max_lon, max_lat] - reduced from 0.1 to 0.06 degrees
}

# Detection thresholds
CHANGE_THRESHOLD_HA = 0.5  # Alert if change > 0.5 hectares
CHANGE_THRESHOLD_PERCENT = 2.0  # Alert if change > 2%
PIXEL_SIZE_M = 9.8  # Sentinel-2 resolution (10m, but using 9.8 for accuracy)

# Model configuration
MODEL_PATH = "models/saved_weights.pt"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ========================================
# U-Net Model Architecture
# ========================================

class UNet(nn.Module):
    """U-Net model for mining detection"""
    
    def __init__(self, in_channels=3, out_channels=1):
        super(UNet, self).__init__()
        
        # Encoder
        self.enc1 = self.conv_block(in_channels, 64)
        self.enc2 = self.conv_block(64, 128)
        self.enc3 = self.conv_block(128, 256)
        self.enc4 = self.conv_block(256, 512)
        
        # Bottleneck
        self.bottleneck = self.conv_block(512, 1024)
        
        # Decoder
        self.upconv4 = nn.ConvTranspose2d(1024, 512, 2, stride=2)
        self.dec4 = self.conv_block(1024, 512)
        self.upconv3 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.dec3 = self.conv_block(512, 256)
        self.upconv2 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.dec2 = self.conv_block(256, 128)
        self.upconv1 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.dec1 = self.conv_block(128, 64)
        
        # Output
        self.out = nn.Conv2d(64, out_channels, 1)
        
        # Pooling
        self.pool = nn.MaxPool2d(2)
    
    def conv_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        enc4 = self.enc4(self.pool(enc3))
        
        # Bottleneck
        bottleneck = self.bottleneck(self.pool(enc4))
        
        # Decoder
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat([dec4, enc4], dim=1)
        dec4 = self.dec4(dec4)
        
        dec3 = self.upconv3(dec4)
        dec3 = torch.cat([dec3, enc3], dim=1)
        dec3 = self.dec3(dec3)
        
        dec2 = self.upconv2(dec3)
        dec2 = torch.cat([dec2, enc2], dim=1)
        dec2 = self.dec2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat([dec1, enc1], dim=1)
        dec1 = self.dec1(dec1)
        
        return torch.sigmoid(self.out(dec1))


# ========================================
# Mining Detection Pipeline
# ========================================

class MiningDetector:
    """Automated mining detection system"""
    
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.model = None
        self.ee_initialized = False
        
        print("🤖 Mining Detector Initialized")
        print(f"📍 Study Area: {STUDY_AREA['name']}")
        print(f"🎯 Device: {DEVICE}")
    
    def initialize_earth_engine(self):
        """Initialize Google Earth Engine"""
        try:
            # Try to authenticate using service account
            credentials_path = os.getenv('GEE_SERVICE_ACCOUNT_KEY')
            if credentials_path and os.path.exists(credentials_path):
                credentials = ee.ServiceAccountCredentials(
                    email=os.getenv('GEE_SERVICE_ACCOUNT_EMAIL'),
                    key_file=credentials_path
                )
                ee.Initialize(credentials)
            else:
                # Fall back to regular authentication
                ee.Initialize()
            
            self.ee_initialized = True
            print("✅ Earth Engine initialized")
            return True
        except Exception as e:
            print(f"❌ Earth Engine initialization failed: {e}")
            return False
    
    def load_model(self):
        """Load trained U-Net model"""
        try:
            if not os.path.exists(MODEL_PATH):
                print(f"❌ Model not found at {MODEL_PATH}")
                return False
            
            self.model = UNet(in_channels=3, out_channels=1)
            
            # Load weights
            checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
            self.model.load_state_dict(checkpoint)
            self.model.to(DEVICE)
            self.model.eval()
            
            print(f"✅ Model loaded from {MODEL_PATH}")
            return True
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            return False
    
    def fetch_latest_imagery(self, days_back=30):
        """Fetch latest Sentinel-2 imagery"""
        if not self.ee_initialized:
            print("❌ Earth Engine not initialized")
            return None
        
        try:
            # Define study area
            geometry = ee.Geometry.Rectangle(STUDY_AREA['bounds'])
            
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Fetch Sentinel-2 imagery
            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(geometry) \
                .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .sort('system:time_start', False)
            
            # Get most recent image
            latest = collection.first()
            
            if latest is None:
                print("❌ No recent imagery found")
                return None
            
            # Get image info
            img_info = latest.getInfo()
            img_date = datetime.fromtimestamp(img_info['properties']['system:time_start'] / 1000)
            
            print(f"✅ Found imagery from {img_date.strftime('%Y-%m-%d')}")
            
            # Select RGB bands and clip to area
            rgb = latest.select(['B4', 'B3', 'B2']).clip(geometry)
            
            # Reduce image size to avoid download size limit (50MB max)
            # Using scale=30 instead of 10 reduces size by 9x
            url = rgb.getDownloadURL({
                'scale': 30,  # Changed from 10 to reduce file size
                'region': geometry,
                'format': 'GEO_TIFF',
                'crs': 'EPSG:4326'
            })
            
            return {
                'url': url,
                'date': img_date,
                'cloud_cover': img_info['properties'].get('CLOUDY_PIXEL_PERCENTAGE', 0)
            }
            
        except Exception as e:
            print(f"❌ Error fetching imagery: {e}")
            return None
    
    def download_image(self, url, output_path):
        """Download image from URL"""
        try:
            print(f"📥 Downloading image...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Image saved to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        try:
            # Load image
            img = Image.open(image_path).convert('RGB')
            img = np.array(img)
            
            # Normalize to [0, 1]
            img = img.astype(np.float32) / 255.0
            
            # Convert to tensor [1, 3, H, W]
            img_tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)
            
            return img_tensor.to(DEVICE), img.shape[:2]
        except Exception as e:
            print(f"❌ Image preprocessing failed: {e}")
            return None, None
    
    def run_inference(self, image_tensor):
        """Run U-Net inference"""
        try:
            with torch.no_grad():
                prediction = self.model(image_tensor)
            
            # Convert to binary mask (threshold at 0.5)
            mask = (prediction > 0.5).cpu().numpy()[0, 0]
            
            return mask.astype(np.uint8)
        except Exception as e:
            print(f"❌ Inference failed: {e}")
            return None
    
    def calculate_area(self, mask):
        """Calculate mining area in hectares"""
        mining_pixels = np.sum(mask == 1)
        area_m2 = mining_pixels * (PIXEL_SIZE_M ** 2)
        area_ha = area_m2 / 10000
        return area_ha
    
    def compare_with_previous(self, current_mask, current_area):
        """Compare with previous prediction"""
        try:
            # Get latest prediction from database
            response = self.supabase.table('mining_predictions') \
                .select('*') \
                .order('prediction_date', desc=True) \
                .limit(1) \
                .execute()
            
            if not response.data or len(response.data) == 0:
                print("ℹ️ No previous predictions found - this is the first run")
                return {
                    'is_first_run': True,
                    'change_ha': 0,
                    'change_percent': 0,
                    'previous_area': 0
                }
            
            prev_prediction = response.data[0]
            prev_area = float(prev_prediction['mining_area_ha'])
            
            change_ha = current_area - prev_area
            change_percent = (change_ha / prev_area * 100) if prev_area > 0 else 0
            
            print(f"📊 Previous area: {prev_area:.2f} ha")
            print(f"📊 Current area: {current_area:.2f} ha")
            print(f"📊 Change: {change_ha:+.2f} ha ({change_percent:+.1f}%)")
            
            return {
                'is_first_run': False,
                'change_ha': change_ha,
                'change_percent': change_percent,
                'previous_area': prev_area,
                'previous_date': prev_prediction['prediction_date']
            }
            
        except Exception as e:
            print(f"❌ Comparison failed: {e}")
            return None
    
    def save_prediction(self, area_ha, image_date, notes=""):
        """Save prediction to database"""
        try:
            data = {
                'prediction_date': image_date.strftime('%Y-%m-%d'),
                'mining_area_ha': float(area_ha),
                'model_version': '1.0',
                'confidence': 0.95,
                'status': 'completed',
                'notes': notes
            }
            
            response = self.supabase.table('mining_predictions').insert(data).execute()
            
            if response.data:
                print(f"✅ Prediction saved to database")
                return response.data[0]['id']
            else:
                print("❌ Failed to save prediction")
                return None
                
        except Exception as e:
            print(f"❌ Error saving prediction: {e}")
            return None
    
    def send_alert(self, change_ha, change_percent, current_area, image_date, comparison):
        """Send notification alert"""
        try:
            # Determine severity
            if abs(change_ha) > 10:
                severity = 'critical'
                title = "🚨🚨 CRITICAL: Major Mining Activity Detected"
            elif abs(change_ha) > 5:
                severity = 'high'
                title = "🚨 High Priority: Significant Mining Expansion"
            elif abs(change_ha) > 1:
                severity = 'medium'
                title = "⚠️ New Mining Activity Detected"
            else:
                severity = 'low'
                title = "ℹ️ Minor Change Detected"
            
            # Create message
            if change_ha > 0:
                message = f"Mining area INCREASED by {change_ha:.2f} hectares (+{change_percent:.1f}%). "
            else:
                message = f"Mining area DECREASED by {abs(change_ha):.2f} hectares ({change_percent:.1f}%). "
            
            message += f"Current total: {current_area:.2f} ha. "
            
            if not comparison['is_first_run']:
                prev_date = comparison['previous_date']
                message += f"Previous measurement from {prev_date}. "
            
            message += "Field inspection recommended."
            
            # Create alert
            alert_data = {
                'alert_type': 'mining_detected',
                'severity': severity,
                'title': title,
                'message': message,
                'location': STUDY_AREA['name'],
                'latitude': STUDY_AREA['latitude'],
                'longitude': STUDY_AREA['longitude'],
                'area_change_ha': float(change_ha),
                'change_percent': float(change_percent),
                'image_date': image_date.strftime('%Y-%m-%d'),
                'status': 'unread',
                'requires_action': severity in ['high', 'critical']
            }
            
            response = self.supabase.table('mining_alerts').insert(alert_data).execute()
            
            if response.data:
                alert_id = response.data[0]['id']
                print(f"🔔 Alert sent! ID: {alert_id} | Severity: {severity.upper()}")
                return alert_id
            else:
                print("❌ Failed to send alert")
                return None
                
        except Exception as e:
            print(f"❌ Error sending alert: {e}")
            return None
    
    def run_detection_pipeline(self, days_back=30, force_alert=False):
        """Run complete detection pipeline"""
        print("\n" + "="*60)
        print("🚀 STARTING AUTOMATED MINING DETECTION PIPELINE")
        print("="*60)
        
        # Step 1: Initialize Earth Engine
        if not self.initialize_earth_engine():
            return False
        
        # Step 2: Load model
        if not self.load_model():
            return False
        
        # Step 3: Fetch latest imagery
        print("\n📡 Fetching latest satellite imagery...")
        imagery = self.fetch_latest_imagery(days_back)
        if not imagery:
            return False
        
        # Step 4: Download image
        output_dir = Path("temp_inference")
        output_dir.mkdir(exist_ok=True)
        image_path = output_dir / f"satellite_{imagery['date'].strftime('%Y%m%d')}.tif"
        
        if not self.download_image(imagery['url'], image_path):
            return False
        
        # Step 5: Preprocess image
        print("\n🔧 Preprocessing image...")
        image_tensor, img_shape = self.preprocess_image(image_path)
        if image_tensor is None:
            return False
        
        # Step 6: Run inference
        print("\n🤖 Running U-Net inference...")
        mask = self.run_inference(image_tensor)
        if mask is None:
            return False
        
        # Step 7: Calculate area
        current_area = self.calculate_area(mask)
        print(f"✅ Detected mining area: {current_area:.2f} hectares")
        
        # Step 8: Compare with previous
        print("\n📊 Comparing with previous predictions...")
        comparison = self.compare_with_previous(mask, current_area)
        if comparison is None:
            return False
        
        # Step 9: Save prediction
        print("\n💾 Saving prediction...")
        notes = f"Automated detection from satellite imagery. Cloud cover: {imagery['cloud_cover']:.1f}%"
        prediction_id = self.save_prediction(current_area, imagery['date'], notes)
        
        # Step 10: Send alert if significant change
        change_ha = abs(comparison['change_ha'])
        change_percent = abs(comparison['change_percent'])
        
        should_alert = (
            force_alert or
            comparison['is_first_run'] or
            change_ha >= CHANGE_THRESHOLD_HA or
            change_percent >= CHANGE_THRESHOLD_PERCENT
        )
        
        if should_alert:
            print("\n🔔 Sending notification alert...")
            alert_id = self.send_alert(
                comparison['change_ha'],
                comparison['change_percent'],
                current_area,
                imagery['date'],
                comparison
            )
        else:
            print(f"\nℹ️ No significant change detected (change: {change_ha:.2f} ha, {change_percent:.1f}%)")
            print(f"   Threshold: {CHANGE_THRESHOLD_HA} ha or {CHANGE_THRESHOLD_PERCENT}%")
        
        # Cleanup
        if image_path.exists():
            image_path.unlink()
        
        print("\n" + "="*60)
        print("✅ DETECTION PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True


# ========================================
# Main Entry Point
# ========================================

def main():
    parser = argparse.ArgumentParser(description='Automated Mining Detection')
    parser.add_argument('--days-back', type=int, default=30, 
                       help='Number of days back to search for imagery')
    parser.add_argument('--force-alert', action='store_true',
                       help='Send alert even if change is below threshold')
    
    args = parser.parse_args()
    
    detector = MiningDetector()
    success = detector.run_detection_pipeline(
        days_back=args.days_back,
        force_alert=args.force_alert
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
