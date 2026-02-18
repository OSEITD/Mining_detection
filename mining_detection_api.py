"""
Mining Hotspot Detection API
============================

A Flask-based REST API for detecting illegal mining hotspots using deep learning.
This API provides endpoints for uploading satellite imagery and receiving mining
probability maps and hotspot locations.

Features:
- RESTful API with CORS support
- Deep learning-based mining detection using CNN
- GeoJSON output for detected hotspots
- Configurable probability thresholds
- Batch processing capabilities (planned)

Model: Pre-trained CNN with 19 spectral bands (Sentinel-1/2 + derived indices)
Input: GeoTIFF satellite imagery
Output: Mining probability map + hotspot GeoJSON features

Author: Mining Detection System
Date: January 2026
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import numpy as np
import rasterio
from datetime import datetime
import logging
from pathlib import Path
import torch
import torch.nn.functional as F
from skimage.measure import block_reduce


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Model configuration constants
MODEL_PATH = "outputs/best_model.pth"  
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  #
class MiningDetectionAPI:
    """
    Main API class for mining hotspot detection.

    This class handles model loading, preprocessing of satellite imagery,
    and inference to detect mining activities. It uses a pre-trained CNN
    model that analyzes 19 spectral bands from satellite data.

    Attributes:
        model: PyTorch CNN model for mining detection
    """

    def __init__(self):
        """
        Initialize the mining detection API.

        Loads the pre-trained model and prepares it for inference.
        """
        self.model = None
        self.load_model()

    def load_model(self):
        """
        Load the trained mining detection model from disk.

        Loads model weights from the checkpoint file and initializes
        the CNN architecture with 19 input channels (spectral bands).
        The model is moved to the appropriate device (GPU/CPU) and
        set to evaluation mode for inference.

        Raises:
            Exception: If model loading fails due to missing files or corruption
        """
        try:
            #  model checkpoint containing weights and metadata
            checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)

            from mining_hotspot_detection import SimpleCNN
            self.model = SimpleCNN(in_channels=19)  # 19 spectral bands

            # Load trained weights into the model
            self.model.load_state_dict(checkpoint['model_state_dict'])

            self.model.to(DEVICE)
            self.model.eval()

            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def preprocess_raster(self, raster_path, downsample_factor=4):
        """
        Preprocess input satellite raster for model inference.

        This method loads a GeoTIFF file, applies downsampling for computational
        efficiency, and normalizes the spectral bands using percentile-based
        scaling (same as training preprocessing).

        Args:
            raster_path (str): Path to input GeoTIFF file
            downsample_factor (int): Factor by which to downsample spatial dimensions
                                   (default: 4x for ~16x speedup)

        Returns:
            tuple: (features, transform, crs)
                - features: Normalized spectral bands as numpy array (bands, height, width)
                - transform: Rasterio transform object for georeferencing
                - crs: Coordinate reference system

        Note:
            Normalization uses 2nd-98th percentiles to handle outliers robustly.
            This matches the preprocessing used during model training.
        """
        with rasterio.open(raster_path) as src:
            # Loading all spectral bands (19 bands: optical + SAR + indices + terrain)
            features = src.read()
            transform = src.transform
            crs = src.crs

            # Downsample spatial dimensions for computational efficiency
            features = block_reduce(features, (1, downsample_factor, downsample_factor), np.mean)

            # Apply percentile-based normalization to each spectral band
            for i in range(features.shape[0]):
                band = features[i].flatten()

                #  mask for valid (non-NaN) pixels
                valid_mask = ~np.isnan(band)

                if valid_mask.sum() > 0:
                 
                    valid_values = band[valid_mask]

                    p2, p98 = np.percentile(valid_values, [2, 98])

                    band = np.clip(band, p2, p98)
                    band = (band - p2) / (p98 - p2)
                    features[i] = band.reshape(features[i].shape)

            return features, transform, crs

    def predict_hotspots(self, features, threshold=0.426):
        """
        Run the mining hotspot detection inference on preprocessed features.

        This method performs patch-based inference across the entire raster,
        accumulating probabilities from overlapping patches for smooth results.
        Post-processing includes morphological operations and smoothing.

        Args:
            features (numpy.ndarray): Preprocessed spectral bands (bands, height, width)
            threshold (float): Probability threshold for hotspot detection (default: 0.426)

        Returns:
            numpy.ndarray: Probability map where values > threshold indicate mining hotspots

        Note:
            Uses sliding window approach with 75% overlap for seamless probability maps.
            Post-processing removes noise and improves hotspot connectivity.
        """
        height, width = features.shape[1], features.shape[2]
        patch_size = 32  # Must match training patch size
        stride = patch_size // 4  # 75% overlap between patches

        #  accumulators for probability averaging
        prob_accumulator = np.zeros((height, width), dtype=np.float32)
        count_accumulator = np.zeros((height, width), dtype=np.float32)

        # Disabling gradient computation for inference efficiency
        with torch.no_grad():
           
            for i in range(0, height - patch_size + 1, stride):
                for j in range(0, width - patch_size + 1, stride):
                    # Extract current patch
                    patch = features[:, i:i+patch_size, j:j+patch_size]

                    # Convert to PyTorch tensor and add batch dimension
                    patch_tensor = torch.FloatTensor(patch).unsqueeze(0).to(DEVICE)

                    # Forward pass through model
                    output = self.model(patch_tensor)

                    # Extract mining class probability (class 1)
                    prob = F.softmax(output, dim=1)[0, 1].cpu().numpy()

                   
                    prob_accumulator[i:i+patch_size, j:j+patch_size] += prob
                    count_accumulator[i:i+patch_size, j:j+patch_size] += 1

        # Average overlapping predictions for smooth probability map
        prob_map = np.divide(prob_accumulator, count_accumulator,
                           out=np.zeros_like(prob_accumulator),
                           where=count_accumulator > 0)

        #  morphological post-processing to reduce noise
        from scipy.ndimage import binary_closing, binary_opening, gaussian_filter

        binary_mask = prob_map > threshold

        closed_mask = binary_closing(binary_mask, structure=np.ones((3,3)))

        # Morphological opening to remove small noise regions
        opened_mask = binary_opening(closed_mask, structure=np.ones((2,2)))

        # Apply mask to probability map and smooth with Gaussian filter
        prob_map = prob_map * opened_mask.astype(float)
        prob_map = gaussian_filter(prob_map, sigma=0.5)

        return prob_map

# Initialize the mining detection API instance
api = MiningDetectionAPI()

# Flask API Endpoints


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for API monitoring.

    Returns the current status of the API, including model loading status
    and timestamp. Used by load balancers and monitoring systems.

    Returns:
        JSON: Health status information
            - status: "healthy" if API is functioning
            - timestamp: ISO format timestamp
            - model_loaded: Boolean indicating if model is loaded
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': api.model is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint for mining hotspot detection.

    Accepts a GeoTIFF file upload, processes it through the mining detection
    model, and returns detected hotspots as GeoJSON features.

    Expected Input:
        - file: GeoTIFF satellite imagery (multipart/form-data)
        - threshold: Optional probability threshold (default: 0.426)

    Returns:
        JSON: Detection results containing:
            - hotspots: GeoJSON features for detected mining locations
            - statistics: Summary statistics about the detection
            - timestamp: Processing timestamp

    Error Responses:
        400: No file provided
        500: Processing error
    """
    try:
        #  file upload validation
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        threshold = float(request.form.get('threshold', 0.426))

        temp_path = f"temp_{datetime.now().timestamp()}.tif"
        file.save(temp_path)

        # Preprocessing the satellite imagery
        features, transform, crs = api.preprocess_raster(temp_path)

        # Running mining detection inference
        prob_map = api.predict_hotspots(features, threshold)

        # Converting high-probability pixels to GeoJSON hotspots
        hotspots = []
        rows, cols = np.where(prob_map > threshold)

        for r, c in zip(rows, cols):
            # Converting pixel coordinates to geographic coordinates
            lon, lat = rasterio.transform.xy(transform, r, c, offset='center')
            hotspots.append({
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
                'properties': {
                    'probability': float(prob_map[r, c]),
                    'confidence': 'high' if prob_map[r, c] > 0.7 else 'medium'
                }
            })

        
        os.remove(temp_path)

        # comprehensive results
        return jsonify({
            'hotspots': hotspots,
            'statistics': {
                'total_pixels': prob_map.size,
                'detected_hotspots': len(hotspots),
                'max_probability': float(prob_map.max()),
                'mean_probability': float(prob_map.mean()),
                'threshold_used': threshold
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """
    Batch prediction endpoint for processing multiple areas.

    Planned feature for processing multiple satellite images in a single request.
    Currently returns placeholder response.

    TODO: Implement batch processing logic for multiple GeoTIFF files.
    """
    return jsonify({'message': 'Batch prediction not implemented yet'})

# ========================================
# Application Entry Point
# ========================================

if __name__ == '__main__':
    # Start Flask development server
    # Note: In production, use a WSGI server like gunicorn
    app.run(host='0.0.0.0', port=80, debug=False)