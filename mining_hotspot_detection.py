
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Importing geospatial libraries
import rasterio
from rasterio.features import rasterize
import geopandas as gpd
from shapely.geometry import mapping

# Importing machine learning libraries
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, roc_curve,
    confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline

# Importing deep learning libraries
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F

# Importing XGBoost
try:
    import xgboost as xgb  # type: ignore
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not available. Install with: pip install xgboost")


class FocalLoss(nn.Module):
    """Focal Loss for addressing class imbalance in segmentation"""
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss

        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


class DiceLoss(nn.Module):
    """Dice Loss for better boundary detection in imbalanced data"""
    def __init__(self, smooth=1e-5):
        super(DiceLoss, self).__init__()
        self.smooth = smooth

    def forward(self, pred, target):
        # pred: (batch_size, 2, H, W) - model output
        # target: (batch_size, H, W) - ground truth
        
        # Converting target to one-hot: (batch_size, 2, H, W)
        target_onehot = torch.zeros_like(pred)
        target_onehot[:, 0] = (target == 0).float()  # Background
        target_onehot[:, 1] = (target == 1).float()  # Mining
        
        # softmax to pred for probabilities
        pred = F.softmax(pred, dim=1)
        
        # Calculate Dice for each class and average
        dice_loss = 0
        for class_idx in range(pred.shape[1]):
            pred_class = pred[:, class_idx]
            target_class = target_onehot[:, class_idx]
            
            intersection = (pred_class * target_class).sum()
            dice_class = (2 * intersection + self.smooth) / (pred_class.sum() + target_class.sum() + self.smooth)
            dice_loss += (1 - dice_class)
        
        return dice_loss / pred.shape[1]  



# Configuring pipeline parameters


class Config:
    """Configuration parameters for the pipeline"""
    
    FEATURE_STACK_PATH = "chingola_FeatureStack_PERFECT.tif"  
    LABELS_GEOJSON_PATH = "chingola_TrainingData_PERFECT.geojson"  
    METADATA_PATH = "chingola_Metadata_PERFECT.geojson" 
    OUTPUT_DIR = "outputs"
    
    #  models :random_forest', 'xgboost', 'cnn', 'unet', 'ensemble'
    MODEL_TYPE = 'ensemble' 
    TRAIN_BOTH_ML_DL = True 
    ML_MODEL_TYPE = 'random_forest' 
    ENSEMBLE_METHOD = 'average'  
    
    # Loss function options
    LOSS_TYPE = 'dice_focal'  

    # Setting training parameters
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    HANDLE_IMBALANCE = True
    IMBALANCE_METHOD = 'focal_loss' 
    
    # Configuring Random Forest parameters
    RF_N_ESTIMATORS = 25  
    RF_MAX_DEPTH = 10    
    RF_MIN_SAMPLES_SPLIT = 50  
    RF_N_JOBS = -1
    
    # Configuring XGBoost parameters
    XGB_N_ESTIMATORS = 200
    XGB_MAX_DEPTH = 10
    XGB_LEARNING_RATE = 0.1
    
    # Configuring deep learning parameters
    DL_BATCH_SIZE = 8  
    DL_EPOCHS = 150      
    DL_LEARNING_RATE = 0.0003  
    DL_PATCH_SIZE = 32  
    DL_DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Ensuring reproducibility
    SET_SEED = True
    SEED = 42
    
    # Applying SAR terrain correction
    APPLY_SAR_TERRAIN_CORRECTION = False
    DEM_PATH = None 
    SAR_BAND_INDICES = [0, 1] 
    
    HOTSPOT_BUFFER = 5 
    
    # Setting visualization parameters
    PLOT_DPI = 300



# Preparing data loading and preprocessing


class GeospatialDataLoader:
    """Handles loading and alignment of raster and vector data"""
    
    def __init__(self, config):
        self.config = config
        
    def load_feature_stack(self):
        """Load the feature stack GeoTIFF"""
        print(f"Loading feature stack from: {self.config.FEATURE_STACK_PATH}")
        
        with rasterio.open(self.config.FEATURE_STACK_PATH) as src:
           
            features = src.read()  # Shape: (bands, height, width)
            transform = src.transform
            crs = src.crs
            profile = src.profile
            
            
            nodata = src.nodata
            if nodata is not None:
                features = np.where(features == nodata, np.nan, features)
        
        # Applying SAR terrain correction if enabled
        if self.config.APPLY_SAR_TERRAIN_CORRECTION:
            print("\nApplying SAR terrain correction...")
            features = self._apply_sar_terrain_correction(
                features, transform, crs, profile
            )
            
        print(f"Feature stack shape: {features.shape}")
        print(f"Bands: {features.shape[0]}, Height: {features.shape[1]}, Width: {features.shape[2]}")
        print(f"CRS: {crs}")
        
        return features, transform, crs, profile
    
    def load_labels(self, crs):
        """Load GeoJSON labels (now balanced training data with class attribute)"""
        print(f"Loading labels from: {self.config.LABELS_GEOJSON_PATH}")
        
        gdf = gpd.read_file(self.config.LABELS_GEOJSON_PATH)
        print(f"Loaded {len(gdf)} training samples")
        
        # Checking the class distribution
        if 'class' in gdf.columns:
            class_dist = gdf['class'].value_counts()
            print(f"Class distribution: {dict(class_dist)}")
            if 'label' in gdf.columns:
                label_dist = gdf['label'].value_counts()
                print(f"Label distribution: {dict(label_dist)}")

        if gdf.crs != crs:
            print(f"Reprojecting labels from {gdf.crs} to {crs}")
            gdf = gdf.to_crs(crs)
        
        return gdf
    
    def _apply_sar_terrain_correction(self, features, transform, crs, profile):
        """Apply radiometric terrain correction to SAR bands"""
        from scipy.ndimage import gaussian_filter
        
        n_bands, height, width = features.shape
        corrected_features = features.copy()
        
        # Loading or generating DEM
        if self.config.DEM_PATH and os.path.exists(self.config.DEM_PATH):
            print(f"  Loading DEM from: {self.config.DEM_PATH}")
            with rasterio.open(self.config.DEM_PATH) as dem_src:
                # Reproject DEM to match feature stack if needed
                if dem_src.crs != crs:
                    from rasterio.warp import reproject, Resampling
                    dem = np.zeros((height, width), dtype=np.float32)
                    reproject(
                        source=rasterio.band(dem_src, 1),
                        destination=dem,
                        src_transform=dem_src.transform,
                        src_crs=dem_src.crs,
                        dst_transform=transform,
                        dst_crs=crs,
                        resampling=Resampling.bilinear
                    )
                else:
                    dem = dem_src.read(1)
                    if dem.shape != (height, width):
                        from rasterio.warp import reproject, Resampling
                        dem_resampled = np.zeros((height, width), dtype=np.float32)
                        reproject(
                            source=dem,
                            destination=dem_resampled,
                            src_transform=dem_src.transform,
                            src_crs=dem_src.crs,
                            dst_transform=transform,
                            dst_crs=crs,
                            resampling=Resampling.bilinear
                        )
                        dem = dem_resampled
        else:
            print("  Using flat terrain assumption (DEM=0)")
            dem = np.zeros((height, width), dtype=np.float32)
        
        # Calculating slope and aspect from DEM for terrain correction
        print("  Computing terrain geometry...")
        dy, dx = np.gradient(dem, transform.a, abs(transform.e))  # Pixel spacing
        slope = np.arctan(np.sqrt(dx**2 + dy**2))  # Slope in radians
        aspect = np.arctan2(dy, dx)  # Aspect in radians
        
        # SAR imaging geometry (typical Sentinel-1 parameters)

        center_incidence = np.deg2rad(35.0)  
       
        local_incidence = np.arccos(
            np.cos(center_incidence) * np.cos(slope) + 
            np.sin(center_incidence) * np.sin(slope) * np.cos(aspect)
        )
        
        
        local_incidence = np.clip(local_incidence, np.deg2rad(10), np.deg2rad(80))
        
        # Applying terrain flattening correction to SAR bands
        for band_idx in self.config.SAR_BAND_INDICES:
            if band_idx >= n_bands:
                continue
                
            print(f"  Correcting SAR band {band_idx}...")
            sar_band = features[band_idx].copy()
            
           
            is_db = np.nanmax(sar_band) < 10 and np.nanmin(sar_band) > -50
            if is_db:
                sar_linear = 10 ** (sar_band / 10.0)
            else:
                sar_linear = sar_band
            
            correction_factor = np.cos(local_incidence) / np.cos(center_incidence)
            correction_factor = np.clip(correction_factor, 0.1, 10.0)  
            
            sar_corrected = sar_linear * correction_factor
            
            if is_db:
                sar_corrected = 10 * np.log10(np.maximum(sar_corrected, 1e-10))
            
            
            sar_corrected = gaussian_filter(sar_corrected, sigma=1.0)
          
            sar_corrected = np.where(np.isnan(sar_band), np.nan, sar_corrected)
            
            corrected_features[band_idx] = sar_corrected
            
            # Report statistics
            valid_orig = sar_band[~np.isnan(sar_band)]
            valid_corr = sar_corrected[~np.isnan(sar_corrected)]
            if len(valid_orig) > 0 and len(valid_corr) > 0:
                print(f"    Original range: [{np.min(valid_orig):.2f}, {np.max(valid_orig):.2f}]")
                print(f"    Corrected range: [{np.min(valid_corr):.2f}, {np.max(valid_corr):.2f}]")
        
        print("  SAR terrain correction completed")
        return corrected_features
    
    def create_label_mask(self, gdf, shape, transform):
        """Rasterize vector labels to create a binary mask"""
        print("Creating label mask from vector data...")
        
        if 'class' in gdf.columns:
            mining_gdf = gdf[gdf['class'] == 1].copy()
            print(f"Using {len(mining_gdf)} mining samples for mask creation")
        else:
            mining_gdf = gdf
        
        # Creating shapes for rasterization
        shapes = [(geom, 1) for geom in mining_gdf.geometry]
       
        mask = rasterize(
            shapes,
            out_shape=shape,
            transform=transform,
            fill=0,
            dtype=np.uint8
        )
        if self.config.HOTSPOT_BUFFER > 0:
            from scipy.ndimage import binary_dilation
            struct = np.ones((self.config.HOTSPOT_BUFFER*2+1, self.config.HOTSPOT_BUFFER*2+1))
            mask = binary_dilation(mask, structure=struct).astype(np.uint8)
        
        positive_pixels = np.sum(mask)
        total_pixels = mask.size
        print(f"Positive pixels: {positive_pixels} ({100*positive_pixels/total_pixels:.2f}%)")
        print(f"Negative pixels: {total_pixels - positive_pixels} ({100*(1-positive_pixels/total_pixels):.2f}%)")
        
        return mask


# Engineering features


class FeaturePreprocessor:
    """Handles feature normalization and preprocessing"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.fitted = False
        
    def prepare_features_ml(self, features, mask):
        """Prepare features for classical ML (flatten to 2D) with better NaN handling"""
        print("Preparing features for classical ML...")
        
        n_bands, height, width = features.shape
        
        # Flattening spatial dimensions
        X = features.reshape(n_bands, -1).T
        y = mask.flatten()
        
        #  removing pixels where ALL bands are NaN
        all_nan_mask = np.isnan(X).all(axis=1)
        X = X[~all_nan_mask]
        y = y[~all_nan_mask]
        
        # For remaining NaN values in individual bands, impute with mean of that band
        for i in range(X.shape[1]):
            band_data = X[:, i]
            nan_mask = np.isnan(band_data)
            if nan_mask.any():
                band_mean = np.nanmean(band_data)
                band_data[nan_mask] = band_mean
                X[:, i] = band_data
        
        print(f"Features shape: {X.shape}")
        print(f"Labels shape: {y.shape}")
        
        return X, y, ~all_nan_mask
    
    def normalize_features(self, X_train, X_test=None):
        """Normalize features using StandardScaler"""
        print("Normalizing features...")
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.fitted = True
        
        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            return X_train_scaled, X_test_scaled
        
        return X_train_scaled
    
    def normalize_raster(self, features):
        """Normalize entire raster stack with better NaN handling"""
        n_bands, height, width = features.shape
        features_norm = np.zeros_like(features, dtype=np.float32)
        
        for i in range(n_bands):
            band = features[i].flatten()
            valid_mask = ~np.isnan(band)
            valid_values = band[valid_mask]
            
            if len(valid_values) > 0:
                mean = np.mean(valid_values)
                std = np.std(valid_values)
                
                if std > 1e-6: 
                    features_norm[i] = np.where(valid_mask.reshape(height, width), 
                                              (features[i] - mean) / std, 
                                              0.0)  
                else:
                    features_norm[i] = np.where(valid_mask.reshape(height, width), 
                                              features[i] - mean, 
                                              0.0)
            else:
    
                features_norm[i] = np.zeros((height, width), dtype=np.float32)
        if np.any(np.isnan(features_norm)):
            print("Warning: NaN values still present after normalization, filling with 0")
            features_norm = np.nan_to_num(features_norm, nan=0.0)
        
        return features_norm


# Defining classical machine learning models

class ClassicalMLPipeline:
    """Pipeline for Random Forest and XGBoost models"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.preprocessor = FeaturePreprocessor()
        
    def create_model(self):
        """Create model based on configuration"""
    
        model_type = self.config.ML_MODEL_TYPE if (hasattr(self.config, 'TRAIN_BOTH_ML_DL') and 
                                                     self.config.TRAIN_BOTH_ML_DL) else self.config.MODEL_TYPE
        
        if model_type == 'random_forest':
            print("Creating Random Forest model...")
            self.model = RandomForestClassifier(
                n_estimators=self.config.RF_N_ESTIMATORS,
                max_depth=self.config.RF_MAX_DEPTH,
                min_samples_split=self.config.RF_MIN_SAMPLES_SPLIT,
                n_jobs=self.config.RF_N_JOBS,
                random_state=self.config.RANDOM_STATE,
                class_weight='balanced' if self.config.HANDLE_IMBALANCE and 
                             self.config.IMBALANCE_METHOD == 'class_weight' else None,
                verbose=1
            )
        elif model_type == 'xgboost':
            if not XGBOOST_AVAILABLE:
                raise ImportError("XGBoost is not installed")
            print("Creating XGBoost model...")
            self.model = xgb.XGBClassifier(
                n_estimators=self.config.XGB_N_ESTIMATORS,
                max_depth=self.config.XGB_MAX_DEPTH,
                learning_rate=self.config.XGB_LEARNING_RATE,
                random_state=self.config.RANDOM_STATE,
                use_label_encoder=False,
                eval_metric='logloss',
                tree_method='hist',
                verbosity=1
            )
        else:
            print(f"Warning: Unknown model type '{model_type}' for classical ML")
        
        return self.model
    
    def handle_imbalance(self, X_train, y_train):
        """Handle class imbalance using SMOTE or undersampling"""
        if not self.config.HANDLE_IMBALANCE:
            return X_train, y_train
        
        if self.config.IMBALANCE_METHOD in ['class_weight', 'focal_loss']:
           
            return X_train, y_train
        
        print(f"Handling class imbalance using {self.config.IMBALANCE_METHOD}...")
        print(f"Original class distribution: {np.bincount(y_train)}")
        
        if self.config.IMBALANCE_METHOD == 'smote':
         
            sampler = SMOTE(random_state=self.config.RANDOM_STATE)
        elif self.config.IMBALANCE_METHOD == 'undersample':
        
            sampler = RandomUnderSampler(random_state=self.config.RANDOM_STATE)
        else:
    
            print(f"Warning: Unknown imbalance method '{self.config.IMBALANCE_METHOD}', skipping resampling")
            return X_train, y_train
        
        X_resampled, y_resampled = sampler.fit_resample(X_train, y_train)
        print(f"Resampled class distribution: {np.bincount(y_resampled)}")
        
        return X_resampled, y_resampled
    
    def train(self, X_train, y_train, X_val, y_val):
        """Train the classical ML model"""
        print("\n" + "="*70)
        print(f"Training {self.config.MODEL_TYPE.upper()} model...")
        print("="*70)

        X_train_scaled, X_val_scaled = self.preprocessor.normalize_features(X_train, X_val)
       
        X_train_balanced, y_train_balanced = self.handle_imbalance(X_train_scaled, y_train)
        
        # Training model
        self.model.fit(X_train_balanced, y_train_balanced)
        
        # Evaluating on training and validation sets
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_val = self.model.predict(X_val_scaled)
        
        print("\nTraining Results:")
        print(f"Train Accuracy: {accuracy_score(y_train, y_pred_train):.4f}")
        print(f"Val Accuracy: {accuracy_score(y_val, y_pred_val):.4f}")
        print(f"Val F1-Score: {f1_score(y_val, y_pred_val, zero_division=0):.4f}")
        
        # Probability predictions for ROC AUC
        y_pred_proba_val = self.model.predict_proba(X_val_scaled)
        if y_pred_proba_val.shape[1] > 1:
            y_pred_proba_val = y_pred_proba_val[:, 1]  
        else:
            y_pred_proba_val = y_pred_proba_val[:, 0] 
        
        if len(np.unique(y_val)) > 1:
            print(f"Val ROC AUC: {roc_auc_score(y_val, y_pred_proba_val):.4f}")
        else:
            print(f"Val ROC AUC: N/A (only one class in validation set)")
        
        return {
            'y_val': y_val,
            'y_pred_val': y_pred_val,
            'y_pred_proba_val': y_pred_proba_val
        }
    
    def predict_full_raster(self, features, valid_mask):
        """Generate prediction map for full raster"""
        print("\nGenerating probability map...")
        
        n_bands, height, width = features.shape
        X_full = features.reshape(n_bands, -1).T
        
        # Initializing output
        prob_map = np.zeros(height * width)
        
        X_valid = X_full[valid_mask]
        X_valid_scaled = self.preprocessor.scaler.transform(X_valid)
        prob_valid = self.model.predict_proba(X_valid_scaled)
        
        if prob_valid.shape[1] > 1:
            prob_valid = prob_valid[:, 1] 
        else:
            prob_valid = prob_valid[:, 0]  
        
        prob_map[valid_mask] = prob_valid
        prob_map = prob_map.reshape(height, width)
        
        return prob_map


# ============================================================================
# Defining deep learning models
# ============================================================================

class MiningDataset(Dataset):
    """PyTorch Dataset for patch-based training with mining-aware sampling"""
    
    def __init__(self, features, labels, patch_size=64, stride=32, oversample_mining=True):
        self.features = features  
        self.labels = labels      
        self.patch_size = patch_size
        self.stride = stride
        self.oversample_mining = oversample_mining
        self.patches = self._generate_patches()
        
    def _generate_patches(self):
        """Generate all valid patch coordinates with mining-aware sampling"""
        _, h, w = self.features.shape
        patches = []
        mining_patches = []
        
        for i in range(0, h - self.patch_size + 1, self.stride):
            for j in range(0, w - self.patch_size + 1, self.stride):
                patch_coords = (i, j)
             
                label_patch = self.labels[i:i+self.patch_size, j:j+self.patch_size]
                has_mining = np.any(label_patch == 1)
                
                if has_mining:
                    mining_patches.append(patch_coords)
                patches.append(patch_coords)
     
        if self.oversample_mining and len(mining_patches) > 0:
            patches.extend(mining_patches * 24)  
            print(f"  Mining patches: {len(mining_patches)} -> oversampled to {len(mining_patches) * 25} (25x)")
        
        return patches
    
    def __len__(self):
        return len(self.patches)
    
    def __getitem__(self, idx):
        i, j = self.patches[idx]
        
        feature_patch = self.features[:, i:i+self.patch_size, j:j+self.patch_size]
        label_patch = self.labels[i:i+self.patch_size, j:j+self.patch_size]
        
        # data augmentation for mining patches 
        if np.random.rand() < 0.8 and np.any(label_patch == 1):  
            # Random horizontal flip
            if np.random.rand() < 0.5:
                feature_patch = np.flip(feature_patch, axis=2).copy()
                label_patch = np.flip(label_patch, axis=1).copy()
            # Random vertical flip
            if np.random.rand() < 0.5:
                feature_patch = np.flip(feature_patch, axis=1).copy()
                label_patch = np.flip(label_patch, axis=0).copy()
            # Random 90-degree rotation
            if np.random.rand() < 0.5:
                k = np.random.randint(1, 4)  # 1, 2, or 3 rotations
                feature_patch = np.rot90(feature_patch, k=k, axes=(1, 2)).copy()
                label_patch = np.rot90(label_patch, k=k, axes=(0, 1)).copy()
            # Random brightness/contrast adjustment 
            if np.random.rand() < 0.3:
                brightness_factor = np.random.uniform(0.8, 1.2)
                contrast_factor = np.random.uniform(0.8, 1.2)
                feature_patch = feature_patch * brightness_factor
                feature_patch = (feature_patch - feature_patch.mean()) * contrast_factor + feature_patch.mean()
            # Random noise addition 
            if np.random.rand() < 0.2:
                noise = np.random.normal(0, 0.01, feature_patch.shape)
                feature_patch = feature_patch + noise
        
        feature_patch = torch.FloatTensor(feature_patch)
        label_patch = torch.LongTensor(label_patch)
        
        return feature_patch, label_patch


class SimpleCNN(nn.Module):
    """Simple CNN for pixel-level classification with dropout"""
    
    def __init__(self, in_channels, num_classes=2):
        super(SimpleCNN, self).__init__()
        
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout2d(0.2), 
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.2),  
            
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Dropout2d(0.3), 
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.3), 
            
            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Dropout2d(0.4), 
            nn.Conv2d(256, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Dropout2d(0.4), 
        )
        
        self.classifier = nn.Sequential(
            nn.Conv2d(256, 128, 1),
            nn.ReLU(),
            nn.Dropout(0.5), 
            nn.Conv2d(128, num_classes, 1)
        )
        
    def forward(self, x):
        features = self.encoder(x)
        out = self.classifier(features)

        out = F.interpolate(out, size=x.shape[2:], mode='bilinear', align_corners=False)
        return out


class UNet(nn.Module):
    """U-Net architecture for semantic segmentation"""
    
    def __init__(self, in_channels, num_classes=2):
        super(UNet, self).__init__()
        
        # Encoder
        self.enc1 = self._conv_block(in_channels, 64)
        self.enc2 = self._conv_block(64, 128)
        self.enc3 = self._conv_block(128, 256)
        self.enc4 = self._conv_block(256, 512)
        
        # Bottleneck
        self.bottleneck = self._conv_block(512, 1024)
        
        # Decoder
        self.upconv4 = nn.ConvTranspose2d(1024, 512, 2, stride=2)
        self.dec4 = self._conv_block(1024, 512)
        
        self.upconv3 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.dec3 = self._conv_block(512, 256)
        
        self.upconv2 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.dec2 = self._conv_block(256, 128)
        
        self.upconv1 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.dec1 = self._conv_block(128, 64)
        
        # Output
        self.out = nn.Conv2d(64, num_classes, 1)
        
        self.pool = nn.MaxPool2d(2)
        
    def _conv_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Dropout2d(0.1),  
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Dropout2d(0.1)
        )
    
    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))
        
        # Bottleneck
        b = self.bottleneck(self.pool(e4))
        
        # Decoder
        d4 = self.upconv4(b)
        d4 = torch.cat([d4, e4], dim=1)
        d4 = self.dec4(d4)
        
        d3 = self.upconv3(d4)
        d3 = torch.cat([d3, e3], dim=1)
        d3 = self.dec3(d3)
        
        d2 = self.upconv2(d3)
        d2 = torch.cat([d2, e2], dim=1)
        d2 = self.dec2(d2)
        
        d1 = self.upconv1(d2)
        d1 = torch.cat([d1, e1], dim=1)
        d1 = self.dec1(d1)
        
        return self.out(d1)


class DeepLearningPipeline:
    """Pipeline for CNN and U-Net models"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.device = torch.device(config.DL_DEVICE)
        self.preprocessor = FeaturePreprocessor()
        
    def create_model(self, in_channels):
        """Create DL model based on configuration"""
        # For ensemble mode, default to CNN
        model_type = self.config.MODEL_TYPE if self.config.MODEL_TYPE in ['cnn', 'unet'] else 'cnn'
        
        if model_type == 'cnn':
            print("Creating CNN model...")
            self.model = SimpleCNN(in_channels, num_classes=2)
        elif model_type == 'unet':
            print("Creating U-Net model...")
            self.model = UNet(in_channels, num_classes=2)
        
        if self.model is None:
            raise ValueError(f"Unknown model type: {model_type}")
            
        self.model = self.model.to(self.device)
        print(f"Model created and moved to {self.device}")
        
        return self.model
    
    def train(self, features_train, labels_train, features_val, labels_val):
        """Train deep learning model"""
        print("\n" + "="*70)
        print(f"Training {self.config.MODEL_TYPE.upper()} model...")
        print("="*70)
        
        print("Normalizing training features...")
        features_train_norm = self.preprocessor.normalize_raster(features_train)
        print("Normalizing validation features...")
        features_val_norm = self.preprocessor.normalize_raster(features_val)
        
        # Checking  NaN values
        train_nan = np.isnan(features_train_norm).sum()
        val_nan = np.isnan(features_val_norm).sum()
        print(f"NaN values in training data: {train_nan}")
        print(f"NaN values in validation data: {val_nan}")
        
        train_dataset = MiningDataset(
            features_train_norm, labels_train,
            patch_size=self.config.DL_PATCH_SIZE,
            stride=self.config.DL_PATCH_SIZE // 4,  
            oversample_mining=True  
        )
        val_dataset = MiningDataset(
            features_val_norm, labels_val,
            patch_size=self.config.DL_PATCH_SIZE,
            stride=self.config.DL_PATCH_SIZE,
            oversample_mining=False 
        )
        
        train_loader = DataLoader(
            train_dataset, batch_size=self.config.DL_BATCH_SIZE,
            shuffle=True, num_workers=0
        )
        val_loader = DataLoader(
            val_dataset, batch_size=self.config.DL_BATCH_SIZE,
            shuffle=False, num_workers=0
        )
        
        print(f"Training patches: {len(train_dataset)}")
        print(f"Validation patches: {len(val_dataset)}")
        
        # Loss and optimizer for extreme class imbalance
        class_counts = np.bincount(labels_train.flatten())
        pos_weight = class_counts[0] / class_counts[1] if class_counts[1] > 0 else 1000
        print(f"Calculated positive class weight: {pos_weight:.1f}")
        
        #  loss function based on config
        if self.config.LOSS_TYPE == 'focal':
            alpha = min(pos_weight, 5.0)
            gamma = 1.5
            print(f"Using focal loss alpha: {alpha:.1f}, gamma: {gamma}")
            criterion = FocalLoss(alpha=alpha, gamma=gamma)
        elif self.config.LOSS_TYPE == 'dice':
            print("Using dice loss")
            criterion = DiceLoss()
        elif self.config.LOSS_TYPE == 'dice_focal':
            alpha = min(pos_weight, 5.0)
            gamma = 1.5
            print(f"Using combined dice + focal loss alpha: {alpha:.1f}, gamma: {gamma}")
            dice_loss = DiceLoss()
            focal_loss = FocalLoss(alpha=alpha, gamma=gamma)
            criterion = lambda pred, target: 0.5 * dice_loss(pred, target) + 0.5 * focal_loss(pred, target)
        else:
            criterion = FocalLoss(alpha=5.0, gamma=1.5)  # Default
        optimizer = optim.AdamW(self.model.parameters(), lr=self.config.DL_LEARNING_RATE, weight_decay=1e-4)  # AdamW with weight decay for better generalization
        scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=10, T_mult=2  
        )
        
        # Training loop with early stopping
        best_val_loss = float('inf')
        patience = 20  
        patience_counter = 0
        
        for epoch in range(self.config.DL_EPOCHS):
            self.model.train()
            train_loss = 0
            train_batches = 0
            
            for features, labels in train_loader:
                features = features.to(self.device)
                labels = labels.to(self.device)
                
                if torch.isnan(features).any() or torch.isnan(labels).any():
                    print(f"Warning: NaN detected in batch at epoch {epoch+1}")
                    continue
                
                optimizer.zero_grad()
                outputs = self.model(features)
                loss = criterion(outputs, labels)
                
                if torch.isnan(loss):
                    print(f"Warning: NaN loss detected at epoch {epoch+1}")
                    continue
                    
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                train_batches += 1
            
            self.model.eval()
            val_loss = 0
            val_batches = 0
            
            with torch.no_grad():
                for features, labels in val_loader:
                    features = features.to(self.device)
                    labels = labels.to(self.device)
                    
                    outputs = self.model(features)
                    loss = criterion(outputs, labels)
                    
                    if not torch.isnan(loss):
                        val_loss += loss.item()
                        val_batches += 1
            
            if train_batches > 0:
                train_loss /= train_batches
            if val_batches > 0:
                val_loss /= val_batches
            
            print(f"Epoch [{epoch+1}/{self.config.DL_EPOCHS}] "
                  f"Train Loss: {train_loss:.4f} Val Loss: {val_loss:.4f}")
            scheduler.step(val_loss)
            
            # best model and early stopping
            if val_loss < best_val_loss and not np.isnan(val_loss):
                best_val_loss = val_loss
                patience_counter = 0  
                model_checkpoint = {
                    'model_state_dict': self.model.state_dict(),
                    'model_type': self.config.MODEL_TYPE,
                    'in_channels': self.model.enc1[0].in_channels if hasattr(self.model, 'enc1') else self.model.encoder[0].in_channels,
                    'num_classes': 2,
                    'patch_size': self.config.DL_PATCH_SIZE,
                    'normalization_params': {'method': 'percentile', 'lower': 2, 'upper': 98},
                    'training_crs': 'EPSG:32735',
                    'val_loss': val_loss,
                    'epoch': epoch + 1
                }
                torch.save(model_checkpoint, f"{self.config.OUTPUT_DIR}/best_model.pth")
                torch.save(self.model.state_dict(), f"{self.config.OUTPUT_DIR}/best_model_weights.pth")
                print(f"  -> Best model saved (val_loss: {val_loss:.4f})")
            else:
                patience_counter += 1  
                if patience_counter >= patience:
                    print(f"\n Early stopping triggered after {epoch+1} epochs (patience={patience})")
                    break
        
        # Loading best model
        if os.path.exists(f"{self.config.OUTPUT_DIR}/best_model.pth"):
            checkpoint = torch.load(f"{self.config.OUTPUT_DIR}/best_model.pth")
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            else:
                self.model.load_state_dict(checkpoint)
        
        return self.evaluate_dl(val_loader)
    
    def evaluate_dl(self, val_loader):
        """Evaluate deep learning model"""
        self.model.eval()
        all_preds = []
        all_labels = []
        all_probs = []
        
        with torch.no_grad():
            for features, labels in val_loader:
                features = features.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(features)
                probs = F.softmax(outputs, dim=1)
                preds = torch.argmax(outputs, dim=1)
                
                all_preds.append(preds.cpu().numpy().flatten())
                all_labels.append(labels.cpu().numpy().flatten())
                all_probs.append(probs[:, 1].cpu().numpy().flatten())
        
        y_pred = np.concatenate(all_preds)
        y_true = np.concatenate(all_labels)
        y_prob = np.concatenate(all_probs)
        
        print("\nValidation Results:")
        print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
        print(f"F1-Score: {f1_score(y_true, y_pred):.4f}")
        print(f"Precision: {precision_score(y_true, y_pred):.4f}")
        print(f"Recall: {recall_score(y_true, y_pred):.4f}")
        print(f"ROC AUC: {roc_auc_score(y_true, y_prob):.4f}")

        # Printing class distribution
        unique, counts = np.unique(y_true, return_counts=True)
        print(f"True class distribution: {dict(zip(unique, counts))}")
        unique, counts = np.unique(y_pred, return_counts=True)
        print(f"Predicted class distribution: {dict(zip(unique, counts))}")
        
        #  metrics imbalanced data
        from sklearn.metrics import precision_recall_fscore_support, balanced_accuracy_score
        precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, average=None)
        print(f"\nPer-class metrics:")
        print(f"Non-Mining - Precision: {precision[0]:.4f}, Recall: {recall[0]:.4f}, F1: {f1[0]:.4f}, Support: {support[0]}")
        print(f"Mining     - Precision: {precision[1]:.4f}, Recall: {recall[1]:.4f}, F1: {f1[1]:.4f}, Support: {support[1]}")
        print(f"Balanced Accuracy: {balanced_accuracy_score(y_true, y_pred):.4f}")
        
        # optimal threshold for better recall
        from sklearn.metrics import precision_recall_curve
        precisions, recalls, thresholds = precision_recall_curve(y_true, y_prob)
        
        target_recall = 0.5
        valid_idx = recalls >= target_recall
        if np.any(valid_idx):
            best_idx = np.where(valid_idx)[0][np.argmax(precisions[valid_idx])]
            optimal_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
            optimal_precision = precisions[best_idx]
            optimal_recall = recalls[best_idx]
            
            print(f"\nOptimal threshold for {target_recall*100:.0f}% recall: {optimal_threshold:.3f}")
            print(f"  Precision at this threshold: {optimal_precision:.4f}")
            print(f"  Recall at this threshold: {optimal_recall:.4f}")
            
            y_pred_optimal = (y_prob >= optimal_threshold).astype(int)
            optimal_f1 = f1_score(y_true, y_pred_optimal)
            print(f"  F1-Score at this threshold: {optimal_f1:.4f}")
        
        return {
            'y_val': y_true,
            'y_pred_val': y_pred,
            'y_pred_proba_val': y_prob,
            'optimal_threshold': optimal_threshold if np.any(valid_idx) else 0.5
        }
    
    def predict_full_raster(self, features):
        """Generate prediction map for full raster with overlapping sliding window (matches training)"""
        print("\nGenerating probability map...")

        features_norm = self.preprocessor.normalize_raster(features)
        n_bands, height, width = features_norm.shape
        
        
        patch_size = self.config.DL_PATCH_SIZE
        stride = patch_size // 4
        
        prob_accumulator = np.zeros((height, width), dtype=np.float32)
        count_accumulator = np.zeros((height, width), dtype=np.float32)

        self.model.eval()
        with torch.no_grad():
            for i in range(0, height - patch_size + 1, stride):
                for j in range(0, width - patch_size + 1, stride):
                    patch = features_norm[:, i:i+patch_size, j:j+patch_size]
                    
                  
                    patch_tensor = torch.FloatTensor(patch).unsqueeze(0).to(self.device)
                    output = self.model(patch_tensor)
                    prob = F.softmax(output, dim=1)[0, 1].cpu().numpy()
                    prob_accumulator[i:i+patch_size, j:j+patch_size] += prob
                    count_accumulator[i:i+patch_size, j:j+patch_size] += 1
            
            for i in range(max(0, height - patch_size), height, stride):
                for j in range(max(0, width - patch_size), width, stride):
                    if i >= height - patch_size + 1 or j >= width - patch_size + 1:
                        i_start = min(i, height - patch_size)
                        j_start = min(j, width - patch_size)
                        patch = features_norm[:, i_start:i_start+patch_size, j_start:j_start+patch_size]
                        
                        patch_tensor = torch.FloatTensor(patch).unsqueeze(0).to(self.device)
                        output = self.model(patch_tensor)
                        prob = F.softmax(output, dim=1)[0, 1].cpu().numpy()
                        
                        prob_accumulator[i_start:i_start+patch_size, j_start:j_start+patch_size] += prob
                        count_accumulator[i_start:i_start+patch_size, j_start:j_start+patch_size] += 1
        
        # Average overlapping predictions
        prob_map = np.divide(prob_accumulator, count_accumulator, 
                            out=np.zeros_like(prob_accumulator),
                            where=count_accumulator > 0)

        from scipy.ndimage import maximum_filter
        local_max = maximum_filter(prob_map, size=5)  
        enhanced_prob = np.where(prob_map == local_max, prob_map * 2, prob_map)  
        enhanced_prob = np.clip(enhanced_prob, 0, 1) 

        # Post-processing: Morphological operations for better hotspot detection
        from scipy.ndimage import binary_closing, binary_opening
      
        binary_mask = enhanced_prob > 0.3  
        closed_mask = binary_closing(binary_mask, structure=np.ones((3,3)))
        opened_mask = binary_opening(closed_mask, structure=np.ones((2,2)))
        
        # Apply back to probability map (smooth the probabilities)
        enhanced_prob = enhanced_prob * opened_mask.astype(float)
        
        # Additional enhancement: Gaussian smoothing for noise reduction
        from scipy.ndimage import gaussian_filter
        enhanced_prob = gaussian_filter(enhanced_prob, sigma=0.5)

        print(f"Post-processed probability range: {enhanced_prob.min():.4f} - {enhanced_prob.max():.4f}")
        print(f"Pixels with prob > 0.1: {np.sum(enhanced_prob > 0.1)}")

        return enhanced_prob

# Evaluating and visualizing results


class Evaluator:
    """Model evaluation and visualization"""
    
    def __init__(self, config):
        self.config = config
        
    def plot_confusion_matrix(self, y_true, y_pred, save_path):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Non-Mining', 'Mining'],
                   yticklabels=['Non-Mining', 'Mining'])
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.PLOT_DPI)
        plt.close()
        print(f"Confusion matrix saved to: {save_path}")
    
    def plot_roc_curve(self, y_true, y_pred_proba, save_path):
        """Plot ROC curve"""
        fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
        auc = roc_auc_score(y_true, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.4f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.PLOT_DPI)
        plt.close()
        print(f"ROC curve saved to: {save_path}")
    
    def plot_feature_importance(self, model, feature_names, save_path):
        """Plot feature importance for tree-based models"""
        if not hasattr(model, 'feature_importances_'):
            print("Model does not have feature importances")
            return
        
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(importances)), importances[indices])
        plt.xlabel('Feature Index')
        plt.ylabel('Importance')
        plt.title('Feature Importance')
        plt.xticks(range(len(importances)), indices)
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.PLOT_DPI)
        plt.close()
        print(f"Feature importance plot saved to: {save_path}")
    
    def save_classification_report(self, y_true, y_pred, save_path):
        """Save detailed classification report"""
        
        unique_classes = np.unique(np.concatenate([y_true, y_pred]))
        if len(unique_classes) == 1:
            target_names = ['Non-Mining'] if unique_classes[0] == 0 else ['Mining']
            labels = [unique_classes[0]]
        else:
            target_names = ['Non-Mining', 'Mining']
            labels = [0, 1]
        
        report = classification_report(y_true, y_pred,
                                       target_names=target_names,
                                       labels=labels,
                                       zero_division=0)
        
        with open(save_path, 'w') as f:
            f.write("Classification Report\n")
            f.write("=" * 70 + "\n\n")
            f.write(report)
        
        print(f"Classification report saved to: {save_path}")
        print("\n" + report)

# Generating outputs


class OutputGenerator:
    """Generate output probability maps"""
    
    @staticmethod
    def save_probability_map(prob_map, profile, output_path):
        """Save probability map as GeoTIFF"""
        out_profile = profile.copy()
        out_profile.update({
            'count': 1,
            'dtype': 'float32',
            'compress': 'lzw'
        })
        
        with rasterio.open(output_path, 'w', **out_profile) as dst:
            dst.write(prob_map.astype(np.float32), 1)
        
        print(f"Probability map saved to: {output_path}")
    
    @staticmethod
    def visualize_probability_map(prob_map, save_path, dpi=300):
        """Visualize probability map"""
        plt.figure(figsize=(12, 10))
        im = plt.imshow(prob_map, cmap='RdYlGn_r', vmin=0, vmax=1)
        plt.colorbar(im, label='Mining Probability')
        plt.title('Illegal Mining Probability Map')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        plt.close()
        print(f"Probability map visualization saved to: {save_path}")




def main():
    """Main execution pipeline"""
    
    config = Config()
    if config.SET_SEED:
        np.random.seed(config.SEED)
        torch.manual_seed(config.SEED)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(config.SEED)
        import random
        random.seed(config.SEED)
        print(f"Random seeds set to {config.SEED} for reproducibility\n")
    
    if not os.path.exists(config.FEATURE_STACK_PATH):
        raise FileNotFoundError(f"Feature stack not found: {config.FEATURE_STACK_PATH}")
    if not os.path.exists(config.LABELS_GEOJSON_PATH):
        raise FileNotFoundError(f"Labels file not found: {config.LABELS_GEOJSON_PATH}")
    
    #  output directory
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    print("\n" + "="*70)
    print("ILLEGAL MINING HOTSPOT DETECTION PIPELINE")
    print("="*70 + "\n")

    print("STEP 1: Loading data...")
    print("-" * 70)
    
    data_loader = GeospatialDataLoader(config)
    features, transform, crs, profile = data_loader.load_feature_stack()
    gdf_labels = data_loader.load_labels(crs)
    label_mask = data_loader.create_label_mask(
        gdf_labels, 
        (features.shape[1], features.shape[2]), 
        transform
    )
 

    print("\n" + "="*70)
    print("STEP 2: Preparing features...")
    print("-" * 70)
    
    # models to train
    train_ml = config.TRAIN_BOTH_ML_DL or config.MODEL_TYPE in ['random_forest', 'xgboost']
    train_dl = config.TRAIN_BOTH_ML_DL or config.MODEL_TYPE in ['cnn', 'unet']
    
    ml_prob_map = None
    dl_prob_map = None
    
    if train_ml:
        #  random sampling for ML to ensure valid samples
        preprocessor = FeaturePreprocessor()
        X_full, y_full, valid_mask_full = preprocessor.prepare_features_ml(features, label_mask)
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_full, y_full, test_size=config.TEST_SIZE,
            random_state=config.RANDOM_STATE,
            stratify=y_full
        )
        
        print(f"ML Training samples: {len(X_train)}")
        print(f"ML Validation samples: {len(X_val)}")
        
        print("\n" + "="*70)
        print("STEP 3: Training CLASSICAL ML model...")
        print("-" * 70)
        
        ml_pipeline = ClassicalMLPipeline(config)
        ml_pipeline.create_model()
        ml_results = ml_pipeline.train(X_train, y_train, X_val, y_val)
        
        print("\n" + "="*70)
        print("STEP 4: Evaluating ML model...")
        print("-" * 70)
        
        evaluator = Evaluator(config)
        suffix = "_ml" if config.TRAIN_BOTH_ML_DL else ""
        evaluator.plot_confusion_matrix(
            ml_results['y_val'], ml_results['y_pred_val'],
            f"{config.OUTPUT_DIR}/confusion_matrix{suffix}.png"
        )
        
        #  plotting ROC if both classes are present
        if len(np.unique(ml_results['y_val'])) > 1:
            evaluator.plot_roc_curve(
                ml_results['y_val'], ml_results['y_pred_proba_val'],
                f"{config.OUTPUT_DIR}/roc_curve{suffix}.png"
            )
        else:
            print("Skipping ROC curve - only one class in validation set")
            
        evaluator.plot_feature_importance(
            ml_pipeline.model, None,
            f"{config.OUTPUT_DIR}/feature_importance{suffix}.png"
        )
        evaluator.save_classification_report(
            ml_results['y_val'], ml_results['y_pred_val'],
            f"{config.OUTPUT_DIR}/classification_report{suffix}.txt"
        )
        
        print("\n" + "="*70)
        print("STEP 5: Generating ML probability map...")
        print("-" * 70)
        
        ml_prob_map = ml_pipeline.predict_full_raster(features, valid_mask_full)
        
    if train_dl:
        # Deep Learning approach
        print("\n" + "="*70)
        print("STEP 3: Training DEEP LEARNING model..." if train_ml else "STEP 3: Training model...")
        print("-" * 70)
        print("Validating data for deep learning...")
        nan_count = np.isnan(features).sum()
        print(f"NaN values in original features: {nan_count}")
        unique_labels = np.unique(label_mask)
        print(f"Unique labels in mask: {unique_labels}")
        print(f"Label distribution: {np.bincount(label_mask.flatten())}")
        
        h, w = features.shape[1], features.shape[2]
        split_idx = int(h * (1 - config.TEST_SIZE))
        
        features_train = features[:, :split_idx, :]
        features_val = features[:, split_idx:, :]
        labels_train = label_mask[:split_idx, :]
        labels_val = label_mask[split_idx:, :]
        
        print(f"Training region shape: {features_train.shape}")
        print(f"Validation region shape: {features_val.shape}")

        dl_pipeline = DeepLearningPipeline(config)
        dl_pipeline.create_model(features.shape[0])
        dl_results = dl_pipeline.train(
            features_train, labels_train,
            features_val, labels_val
        )
     
       
        print("\n" + "="*70)
        print("STEP 4: Evaluating DL model..." if train_ml else "STEP 4: Evaluating model...")
        print("-" * 70)
        
        evaluator = Evaluator(config)
        suffix = "_dl" if config.TRAIN_BOTH_ML_DL else ""
        evaluator.plot_confusion_matrix(
            dl_results['y_val'], dl_results['y_pred_val'],
            f"{config.OUTPUT_DIR}/confusion_matrix{suffix}.png"
        )
        evaluator.plot_roc_curve(
            dl_results['y_val'], dl_results['y_pred_proba_val'],
            f"{config.OUTPUT_DIR}/roc_curve{suffix}.png"
        )
        evaluator.save_classification_report(
            dl_results['y_val'], dl_results['y_pred_val'],
            f"{config.OUTPUT_DIR}/classification_report{suffix}.txt"
        )
        # Map Output 
        print("\n" + "="*70)
        print("STEP 5: Generating DL probability map..." if train_ml else "STEP 5: Generating output probability map...")
        print("-" * 70)
        
        dl_prob_map = dl_pipeline.predict_full_raster(features)
    
    #  ensemble if both models trained
    if config.TRAIN_BOTH_ML_DL and ml_prob_map is not None and dl_prob_map is not None:
        print("\n" + "="*70)
        print(f"Creating ensemble ({config.ENSEMBLE_METHOD})...")
        print("-" * 70)
        
        if config.ENSEMBLE_METHOD == 'average':
            prob_map = (ml_prob_map + dl_prob_map) / 2.0
        elif config.ENSEMBLE_METHOD == 'max':
            prob_map = np.maximum(ml_prob_map, dl_prob_map)
        elif config.ENSEMBLE_METHOD == 'weighted':
            prob_map = 0.4 * ml_prob_map + 0.6 * dl_prob_map  
        
        print(f"Ensemble probability range: {prob_map.min():.4f} - {prob_map.max():.4f}")
    else:
        # Using whichever model was trained
        prob_map = dl_prob_map if dl_prob_map is not None else ml_prob_map
    
    print("\n" + "="*70)
    print("STEP 6: Saving outputs...")
    print("-" * 70)
    
    output_gen = OutputGenerator()
    
    #  individual model outputs if both trained
    if config.TRAIN_BOTH_ML_DL:
        if ml_prob_map is not None:
            output_gen.save_probability_map(
                ml_prob_map, profile,
                f"{config.OUTPUT_DIR}/mining_probability_map_ml.tif"
            )
            output_gen.visualize_probability_map(
                ml_prob_map,
                f"{config.OUTPUT_DIR}/mining_probability_map_ml.png",
                dpi=config.PLOT_DPI
            )
        if dl_prob_map is not None:
            output_gen.save_probability_map(
                dl_prob_map, profile,
                f"{config.OUTPUT_DIR}/mining_probability_map_dl.tif"
            )
            output_gen.visualize_probability_map(
                dl_prob_map,
                f"{config.OUTPUT_DIR}/mining_probability_map_dl.png",
                dpi=config.PLOT_DPI
            )
    
    # Saving final/ensemble output
    output_gen.save_probability_map(
        prob_map, profile,
        f"{config.OUTPUT_DIR}/mining_probability_map.tif"
    )
    output_gen.visualize_probability_map(
        prob_map,
        f"{config.OUTPUT_DIR}/mining_probability_map.png",
        dpi=config.PLOT_DPI
    )
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"\nAll outputs saved to: {config.OUTPUT_DIR}/")
    print("\nGenerated files:")
    print(f"  - mining_probability_map.tif (GeoTIFF probability map)")
    print(f"  - mining_probability_map.png (Visualization)")
    print(f"  - confusion_matrix.png")
    print(f"  - roc_curve.png")
    print(f"  - classification_report.txt")
    if config.MODEL_TYPE in ['random_forest', 'xgboost']:
        print(f"  - feature_importance.png")


if __name__ == "__main__":
    main()
