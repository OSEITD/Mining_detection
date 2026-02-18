"""
Advanced False Positive Filtering for Mining Detection
Filters out water bodies, vegetation, and other non-mining features
"""

import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, mapping
import geopandas as gpd
from pathlib import Path
import json

class FalsePositiveFilter:
    """Filter false positives using spectral indices"""
    
    def __init__(self, image_path=None):
        """
        Initialize filter with optional satellite image
        
        Args:
            image_path: Path to multi-band satellite image (for calculating indices)
        """
        self.image_path = image_path
        self.image_data = None
        self.transform = None
        
        if image_path and Path(image_path).exists():
            self._load_image()
    
    def _load_image(self):
        """Load satellite image"""
        try:
            with rasterio.open(self.image_path) as src:
                self.image_data = src.read()  # All bands
                self.transform = src.transform
            print(f" Loaded image with {self.image_data.shape[0]} bands")
        except Exception as e:
            print(f" Could not load image: {e}")
    
    def calculate_ndvi(self, red_band=0, nir_band=3):
        """Calculate NDVI (vegetation index)"""
        if self.image_data is None or self.image_data.shape[0] < 4:
            return None
        
        red = self.image_data[red_band].astype(float)
        nir = self.image_data[nir_band].astype(float)
        
        # Avoid division by zero
        ndvi = np.where(
            (nir + red) != 0,
            (nir - red) / (nir + red),
            0
        )
        
        return ndvi
    
    def calculate_ndwi(self, green_band=1, nir_band=3):
        """Calculate NDWI (water index)"""
        if self.image_data is None or self.image_data.shape[0] < 4:
            return None
        
        green = self.image_data[green_band].astype(float)
        nir = self.image_data[nir_band].astype(float)
        
        # NDWI = (Green - NIR) / (Green + NIR)
        ndwi = np.where(
            (green + nir) != 0,
            (green - nir) / (green + nir),
            0
        )
        
        return ndwi
    
    def calculate_bsi(self, blue_band=2, red_band=0, nir_band=3, swir_band=4):
        """Calculate BSI (Bare Soil Index) - mining areas have high BSI"""
        if self.image_data is None or self.image_data.shape[0] < 5:
            return None
        
        blue = self.image_data[blue_band].astype(float)
        red = self.image_data[red_band].astype(float)
        nir = self.image_data[nir_band].astype(float)
        swir = self.image_data[swir_band].astype(float)
        
        # BSI = ((SWIR + Red) - (NIR + Blue)) / ((SWIR + Red) + (NIR + Blue))
        numerator = (swir + red) - (nir + blue)
        denominator = (swir + red) + (nir + blue)
        
        bsi = np.where(denominator != 0, numerator / denominator, 0)
        
        return bsi
    
    def filter_zones_by_indices(self, zones, prediction_mask, 
                                 exclude_water=True, 
                                 exclude_vegetation=True,
                                 min_bsi=0.0):
        """
        Filter zones using spectral indices
        
        Args:
            zones: List of zone dictionaries
            prediction_mask: Binary prediction mask
            exclude_water: Remove water bodies (NDWI > 0.3)
            exclude_vegetation: Remove dense vegetation (NDVI > 0.6)
            min_bsi: Minimum Bare Soil Index (mining areas typically > 0)
            
        Returns:
            Filtered zones list
        """
        if not zones:
            return []
        
        # Calculate indices
        ndvi = self.calculate_ndvi()
        ndwi = self.calculate_ndwi()
        bsi = self.calculate_bsi()
        
        filtered_zones = []
        stats = {
            'total': len(zones),
            'removed_water': 0,
            'removed_vegetation': 0,
            'removed_low_bsi': 0,
            'kept': 0
        }
        
        for zone in zones:
            # Get zone pixels
            try:
                coords = zone['geometry']['coordinates'][0]
                
                # Create mask for this zone
                from rasterio.features import rasterize
                from shapely.geometry import Polygon
                
                poly = Polygon(coords)
                
                # Skip if indices not available
                if ndvi is None and ndwi is None and bsi is None:
                    filtered_zones.append(zone)
                    continue
                
                # Get bounds of zone
                bounds = zone['bounds']
                
                # Calculate average indices within zone (approximate)
                center_lat = zone['centroid_lat']
                center_lon = zone['centroid_lon']
                
                # Convert to pixel coordinates (approximate)
                if self.transform:
                    from rasterio.transform import rowcol
                    row, col = rowcol(self.transform, center_lon, center_lat)
                    
                    # Get surrounding area (5x5 pixels)
                    row = max(0, min(row, prediction_mask.shape[0] - 1))
                    col = max(0, min(col, prediction_mask.shape[1] - 1))
                    
                    row_start = max(0, row - 2)
                    row_end = min(prediction_mask.shape[0], row + 3)
                    col_start = max(0, col - 2)
                    col_end = min(prediction_mask.shape[1], col + 3)
                    
                    # Calculate average indices in this area
                    keep_zone = True
                    
                    if exclude_water and ndwi is not None:
                        avg_ndwi = np.mean(ndwi[row_start:row_end, col_start:col_end])
                        if avg_ndwi > 0.3:  # Water threshold
                            stats['removed_water'] += 1
                            zone['filtered_reason'] = 'water_body'
                            keep_zone = False
                    
                    if keep_zone and exclude_vegetation and ndvi is not None:
                        avg_ndvi = np.mean(ndvi[row_start:row_end, col_start:col_end])
                        if avg_ndvi > 0.6:  # Dense vegetation threshold
                            stats['removed_vegetation'] += 1
                            zone['filtered_reason'] = 'dense_vegetation'
                            keep_zone = False
                    
                    if keep_zone and bsi is not None:
                        avg_bsi = np.mean(bsi[row_start:row_end, col_start:col_end])
                        if avg_bsi < min_bsi:  # Low bare soil
                            stats['removed_low_bsi'] += 1
                            zone['filtered_reason'] = 'low_bare_soil'
                            keep_zone = False
                    
                    if keep_zone:
                        # Add indices to zone data
                        zone['ndvi'] = float(avg_ndvi) if ndvi is not None else None
                        zone['ndwi'] = float(avg_ndwi) if ndwi is not None else None
                        zone['bsi'] = float(avg_bsi) if bsi is not None else None
                        filtered_zones.append(zone)
                        stats['kept'] += 1
                else:
                    # No transform available, keep zone
                    filtered_zones.append(zone)
                    stats['kept'] += 1
                    
            except Exception as e:
                print(f" Error filtering zone {zone.get('zone_number', '?')}: {e}")
                filtered_zones.append(zone)  # Keep on error
                stats['kept'] += 1
        
        print(f"\n Filtering Results:")
        print(f"   Total zones: {stats['total']}")
        print(f"   Removed water bodies: {stats['removed_water']}")
        print(f"   Removed vegetation: {stats['removed_vegetation']}")
        print(f"   Removed low BSI: {stats['removed_low_bsi']}")
        print(f"    Kept: {stats['kept']} zones")
        
        return filtered_zones
    
    def filter_by_shape_metrics(self, zones):
        """
        Filter zones by shape characteristics
        Mining areas tend to have specific shapes
        """
        filtered = []
        
        for zone in zones:
            try:
                from shapely.geometry import Polygon
                
                coords = zone['geometry']['coordinates'][0]
                poly = Polygon(coords)
                
                # Calculate shape metrics
                area = poly.area
                perimeter = poly.length
                
                # Compactness (circle = 1, line = 0)
                compactness = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
                
                # Skip very elongated shapes (likely roads, rivers)
                if compactness < 0.1:  # Very elongated
                    zone['filtered_reason'] = 'elongated_shape'
                    continue
                
                # Skip very small or very large
                area_ha = zone['area_ha']
                if area_ha < 0.1 or area_ha > 500:
                    zone['filtered_reason'] = 'size_outlier'
                    continue
                
                zone['compactness'] = float(compactness)
                filtered.append(zone)
                
            except Exception as e:
                print(f" Error calculating shape metrics: {e}")
                filtered.append(zone)  # Keep on error
        
        return filtered


def apply_advanced_filtering(zones_path, satellite_image_path=None, output_path=None):
    """
    Apply advanced filtering to remove false positives
    
    Args:
        zones_path: Path to zones JSON file
        satellite_image_path: Path to multi-band satellite image
        output_path: Path to save filtered zones
        
    Returns:
        Filtered zones list
    """
    print("\n" + "="*60)
    print(" ADVANCED FALSE POSITIVE FILTERING")
    print("="*60)
    
    # Load zones
    with open(zones_path, 'r') as f:
        zones_data = json.load(f)
    
    zones = zones_data['zones']
    print(f" Loaded {len(zones)} zones")
    
    # Initialize filter
    filter_obj = FalsePositiveFilter(satellite_image_path)
    
    # Apply shape filtering
    print("\n Step 1: Filtering by shape metrics...")
    zones = filter_obj.filter_by_shape_metrics(zones)
    print(f"    {len(zones)} zones after shape filtering")
    
    # Apply spectral filtering if image available
    if satellite_image_path and Path(satellite_image_path).exists():
        print("\n Step 2: Filtering by spectral indices...")
        
        # Load prediction mask
        prediction_mask = np.ones((100, 100))  # Placeholder
        
        zones = filter_obj.filter_zones_by_indices(
            zones,
            prediction_mask,
            exclude_water=True,
            exclude_vegetation=True,
            min_bsi=0.0
        )
    else:
        print("\n No satellite image provided, skipping spectral filtering")
    
    # Save filtered zones
    if output_path:
        filtered_data = {
            **zones_data,
            'zones': zones,
            'total_zones': len(zones),
            'filtering_applied': True,
            'filtered_at': json.dumps(str(np.datetime64('now')))
        }
        
        with open(output_path, 'w') as f:
            json.dump(filtered_data, f, indent=2)
        
        print(f"\n Filtered zones saved to: {output_path}")
    
    print("\n" + "="*60)
    print(f" FILTERING COMPLETED: {len(zones)} zones remaining")
    print("="*60)
    
    return zones


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python filter_false_positives.py <zones_json_path> [satellite_image_path]")
        sys.exit(1)
    
    zones_path = sys.argv[1]
    satellite_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = zones_path.replace('.json', '_filtered.json')
    
    filtered_zones = apply_advanced_filtering(zones_path, satellite_path, output_path)
