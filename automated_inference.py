"""
Automated Mining Detection Pipeline
====================================
Runs ensemble ML/DL inference on latest satellite imagery and sends notifications.
Uses the mining_hotspot_detection module for model loading and prediction.
Integrates with Google Earth Engine for imagery and Supabase for persistence.
"""

import os
import sys
import json
import ee
import torch
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import requests
import rasterio
from supabase import create_client
import argparse

# Import from the new hotspot detection pipeline
from mining_hotspot_detection import (
    Config, SimpleCNN, UNet, FeaturePreprocessor, DeepLearningPipeline
)

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntkzaobvbsppxbljamvb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw")

# Study area coordinates (Chingola, Zambia)
STUDY_AREA = {
    'name': 'Chingola, Zambia',
    'latitude': -12.5,
    'longitude': 27.85,
    'bounds': [27.82, -12.52, 27.88, -12.48]
}

# Detection thresholds
CHANGE_THRESHOLD_HA = 0.5
CHANGE_THRESHOLD_PERCENT = 2.0
PIXEL_SIZE_M = 9.8

# Model configuration - new ensemble model
MODEL_PATH = "outputs/best_model.pth"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ========================================
# Mining Detection Pipeline
# ========================================

class MiningDetector:
    """Automated mining detection system using ensemble ML/DL models"""
    
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.model = None
        self.ee_initialized = False
        self.config = Config()
        
        print("Mining Detector Initialized")
        print(f"Study Area: {STUDY_AREA['name']}")
        print(f"Device: {DEVICE}")
    
    def initialize_earth_engine(self):
        """Initialize Google Earth Engine"""
        try:
            project_id = os.getenv('GEE_PROJECT_ID', 'ornate-justice-463107-j5')
            
            credentials_path = os.getenv('GEE_SERVICE_ACCOUNT_KEY')
            if credentials_path and os.path.exists(credentials_path):
                credentials = ee.ServiceAccountCredentials(
                    email=os.getenv('GEE_SERVICE_ACCOUNT_EMAIL'),
                    key_file=credentials_path
                )
                ee.Initialize(credentials, project=project_id)
            else:
                ee.Initialize(project=project_id)
            
            self.ee_initialized = True
            print(f"Earth Engine initialized (Project: {project_id})")
            return True
        except Exception as e:
            print(f"Earth Engine initialization failed: {e}")
            return False
    
    def load_model(self):
        """Load trained model from the mining_hotspot_detection pipeline"""
        try:
            if not os.path.exists(MODEL_PATH):
                print(f"Model not found at {MODEL_PATH}")
                # Fall back to old model path
                fallback_path = "models/saved_weights.pt"
                if os.path.exists(fallback_path):
                    print(f"Using fallback model: {fallback_path}")
                    # Load old-style model (3-channel U-Net)
                    from mining_hotspot_detection import UNet as NewUNet
                    self.model = NewUNet(in_channels=3, num_classes=2)
                    checkpoint = torch.load(fallback_path, map_location=DEVICE)
                    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                        self.model.load_state_dict(checkpoint['model_state_dict'])
                    else:
                        self.model.load_state_dict(checkpoint)
                    self.model.to(DEVICE)
                    self.model.eval()
                    print(f"Fallback model loaded from {fallback_path}")
                    return True
                return False
            
            # Load new-style ensemble model checkpoint
            checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
            
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                model_type = checkpoint.get('model_type', 'cnn')
                in_channels = checkpoint.get('in_channels', 19)
                
                if model_type == 'unet':
                    self.model = UNet(in_channels=in_channels, num_classes=2)
                else:
                    self.model = SimpleCNN(in_channels=in_channels, num_classes=2)
                
                self.model.load_state_dict(checkpoint['model_state_dict'])
                print(f"Loaded {model_type} model with {in_channels} input channels")
            else:
                # State dict only
                self.model = SimpleCNN(in_channels=19, num_classes=2)
                self.model.load_state_dict(checkpoint)
            
            self.model.to(DEVICE)
            self.model.eval()
            
            print(f"Model loaded from {MODEL_PATH}")
            return True
        except Exception as e:
            print(f"Model loading failed: {e}")
            return False
    
    def fetch_latest_imagery(self, days_back=30):
        """Fetch latest Sentinel-2 imagery from Google Earth Engine"""
        if not self.ee_initialized:
            print("[ERROR] Earth Engine not initialized")
            return None
        
        try:
            geometry = ee.Geometry.Rectangle(STUDY_AREA['bounds'])
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(geometry) \
                .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .sort('system:time_start', False)
            
            latest = collection.first()
            
            if latest is None:
                print("[WARNING] No recent imagery found")
                return None
            
            img_info = latest.getInfo()
            img_date = datetime.fromtimestamp(img_info['properties']['system:time_start'] / 1000)
            
            print(f"[OK] Found imagery from {img_date.strftime('%Y-%m-%d')}")
            
            # Select bands for multi-spectral analysis
            bands = latest.select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12']).clip(geometry)
            
            url = bands.getDownloadURL({
                'scale': 10,
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
            print(f"[ERROR] Error fetching imagery: {e}")
            return None
    
    def download_image(self, url, output_path):
        """Download image from URL"""
        try:
            print("Downloading image...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"[OK] Image saved to {output_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
            return False
    
    def preprocess_image(self, image_path):
        """Preprocess GeoTIFF for model input using rasterio"""
        try:
            import torch.nn.functional as F
            
            with rasterio.open(image_path) as src:
                features = src.read().astype(np.float32)
                
                # Percentile-based normalization per band
                for i in range(features.shape[0]):
                    band = features[i].flatten()
                    valid = band[~np.isnan(band)]
                    if len(valid) > 0:
                        p2, p98 = np.percentile(valid, [2, 98])
                        if p98 > p2:
                            features[i] = np.clip(features[i], p2, p98)
                            features[i] = (features[i] - p2) / (p98 - p2)
                
                features = np.nan_to_num(features, nan=0.0)
                
                return features, features.shape[1:]
        except Exception as e:
            print(f"[ERROR] Image preprocessing failed: {e}")
            return None, None
    
    def run_inference(self, features):
        """Run inference using the loaded model with patch-based sliding window"""
        try:
            import torch.nn.functional as F
            
            if isinstance(features, np.ndarray):
                n_bands, height, width = features.shape
            else:
                return None
            
            patch_size = 32
            stride = patch_size // 4
            
            prob_accumulator = np.zeros((height, width), dtype=np.float32)
            count_accumulator = np.zeros((height, width), dtype=np.float32)
            
            self.model.eval()
            with torch.no_grad():
                for i in range(0, height - patch_size + 1, stride):
                    for j in range(0, width - patch_size + 1, stride):
                        patch = features[:, i:i+patch_size, j:j+patch_size]
                        patch_tensor = torch.FloatTensor(patch).unsqueeze(0).to(DEVICE)
                        output = self.model(patch_tensor)
                        
                        # Handle both old (sigmoid) and new (softmax) model outputs
                        if output.shape[1] == 1:
                            prob = output[0, 0].cpu().numpy()
                        else:
                            prob = F.softmax(output, dim=1)[0, 1].cpu().numpy()
                        
                        prob_accumulator[i:i+patch_size, j:j+patch_size] += prob
                        count_accumulator[i:i+patch_size, j:j+patch_size] += 1
            
            prob_map = np.divide(prob_accumulator, count_accumulator,
                                out=np.zeros_like(prob_accumulator),
                                where=count_accumulator > 0)
            
            # Binary mask at threshold
            mask = (prob_map > 0.426).astype(np.uint8)
            
            return mask
        except Exception as e:
            print(f"[ERROR] Inference failed: {e}")
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
            response = self.supabase.table('mining_predictions') \
                .select('*') \
                .order('prediction_date', desc=True) \
                .limit(1) \
                .execute()
            
            if not response.data or len(response.data) == 0:
                print("[INFO] No previous predictions found - this is the first run")
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
            
            print(f"Previous area: {prev_area:.2f} ha")
            print(f"Current area: {current_area:.2f} ha")
            print(f"Change: {change_ha:+.2f} ha ({change_percent:+.1f}%)")
            
            return {
                'is_first_run': False,
                'change_ha': change_ha,
                'change_percent': change_percent,
                'previous_area': prev_area,
                'previous_date': prev_prediction['prediction_date']
            }
            
        except Exception as e:
            print(f"[ERROR] Comparison failed: {e}")
            return None
    
    def save_prediction(self, area_ha, image_date, notes=""):
        """Save prediction to database"""
        try:
            data = {
                'prediction_date': image_date.strftime('%Y-%m-%d'),
                'mining_area_ha': float(area_ha),
                'model_version': '2.0',
                'confidence': 0.95,
                'status': 'completed',
                'notes': notes
            }
            
            response = self.supabase.table('mining_predictions').insert(data).execute()
            
            if response.data:
                print("[OK] Prediction saved to database")
                return response.data[0]['id']
            else:
                print("[ERROR] Failed to save prediction")
                return None
                
        except Exception as e:
            print(f"[ERROR] Error saving prediction: {e}")
            return None
    
    def send_alert(self, change_ha, change_percent, current_area, image_date, comparison):
        """Send notification alert"""
        try:
            if abs(change_ha) > 10:
                severity = 'critical'
                title = "CRITICAL: Major Mining Activity Detected"
            elif abs(change_ha) > 5:
                severity = 'high'
                title = "HIGH PRIORITY: Significant Mining Expansion"
            elif abs(change_ha) > 1:
                severity = 'medium'
                title = "ALERT: New Mining Activity Detected"
            else:
                severity = 'low'
                title = "NOTICE: Minor Change Detected"
            
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
                print(f"[ALERT] Alert sent. ID: {alert_id} | Severity: {severity.upper()}")
                return alert_id
            else:
                print("[ERROR] Failed to send alert")
                return None
                
        except Exception as e:
            print(f"[ERROR] Error sending alert: {e}")
            return None
    
    def run_detection_pipeline(self, days_back=30, force_alert=False):
        """Run complete detection pipeline"""
        print("\n" + "="*60)
        print("STARTING AUTOMATED MINING DETECTION PIPELINE")
        print("="*60)
        
        # Step 1: Initialize Earth Engine
        if not self.initialize_earth_engine():
            return False
        
        # Step 2: Load model
        if not self.load_model():
            print("\n⚠️  WARNING: No trained model found. Skipping detection pipeline.")
            print("   To enable inference, upload model to Supabase Storage bucket 'mining-models':")
            print("   • outputs/best_model.pth  OR  models/saved_weights.pt")
            print("   Detection pipeline cannot run without a trained model.")
            return None  # None = skipped (not failed)
        
        # Step 3: Fetch latest imagery
        print("\nFetching latest satellite imagery...")
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
        print("\nPreprocessing image...")
        features, img_shape = self.preprocess_image(image_path)
        if features is None:
            return False
        
        # Step 6: Run inference
        print("\nRunning model inference...")
        mask = self.run_inference(features)
        if mask is None:
            return False
        
        # Step 7: Calculate area
        current_area = self.calculate_area(mask)
        print(f"[OK] Detected mining area: {current_area:.2f} hectares")
        
        # Step 8: Compare with previous
        print("\nComparing with previous predictions...")
        comparison = self.compare_with_previous(mask, current_area)
        if comparison is None:
            return False
        
        # Step 9: Save prediction
        print("\nSaving prediction...")
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
            print("\nSending notification alert...")
            alert_id = self.send_alert(
                comparison['change_ha'],
                comparison['change_percent'],
                current_area,
                imagery['date'],
                comparison
            )
        else:
            print(f"\n[INFO] No significant change detected (change: {change_ha:.2f} ha, {change_percent:.1f}%)")
            print(f"   Threshold: {CHANGE_THRESHOLD_HA} ha or {CHANGE_THRESHOLD_PERCENT}%")
        
        # Cleanup
        if image_path.exists():
            image_path.unlink()
        
        print("\n" + "="*60)
        print("DETECTION PIPELINE COMPLETED SUCCESSFULLY")
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
    result = detector.run_detection_pipeline(
        days_back=args.days_back,
        force_alert=args.force_alert
    )
    
    # None = skipped (no model), True = success, False = error
    sys.exit(0 if result is not False else 1)


if __name__ == "__main__":
    main()
