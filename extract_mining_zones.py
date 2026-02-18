"""
 Extract Mining Zones from AI Predictions
Converts binary prediction masks to polygon geometries with detailed metadata
"""

import numpy as np
import cv2
from shapely.geometry import shape, mapping, Polygon
from shapely.ops import unary_union
import rasterio
from rasterio.features import shapes
from rasterio.transform import from_bounds
import json
from datetime import datetime
from pathlib import Path

# Configuration
PIXEL_SIZE_M = 9.8  # Sentinel-2 resolution (10m, but using 9.8 for accuracy)
MIN_AREA_HA = 0.1  # Minimum area to consider (0.1 hectares = 1000 m²)
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to extract polygon


class MiningZoneExtractor:
    """Extract mining zones from prediction masks"""
    
    def __init__(self, prediction_mask, bounds=None, transform=None):
        """
        Initialize extractor
        
        Args:
            prediction_mask: Binary mask (numpy array) where 1 = mining, 0 = vegetation
            bounds: Geographic bounds [min_lon, min_lat, max_lon, max_lat]
            transform: Rasterio affine transform (if available)
        """
        self.mask = prediction_mask
        self.bounds = bounds or [-12.52, 27.82, -12.48, 27.88]
        self.transform = transform or self._create_transform()
        
        print(f" Mining Zone Extractor initialized")
        print(f"   Mask shape: {self.mask.shape}")
        print(f"   Bounds: {self.bounds}")
    
    def _create_transform(self):
        """Create affine transform from bounds"""
        height, width = self.mask.shape
        return from_bounds(
            self.bounds[0], self.bounds[1],  # west, south
            self.bounds[2], self.bounds[3],  # east, north
            width, height
        )
    
    def extract_zones(self, min_area_ha=MIN_AREA_HA, simplify_tolerance=0.0001):
        """
        Extract mining zones as polygons
        
        Args:
            min_area_ha: Minimum area in hectares to extract
            simplify_tolerance: Tolerance for simplifying polygon boundaries
            
        Returns:
            List of zone dictionaries with properties
        """
        print(f"\n Extracting mining zones...")
        print(f"   Min area: {min_area_ha} ha")
        print(f"   Simplify tolerance: {simplify_tolerance}")
        
        zones = []
        
        # Find contours in the mask
        contours, hierarchy = cv2.findContours(
            self.mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,  # Only external contours
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        print(f" Found {len(contours)} contours")
        
        for idx, contour in enumerate(contours):
            # Skip very small contours
            if len(contour) < 4:
                continue
            
            # Calculate area in pixels
            area_pixels = cv2.contourArea(contour)
            area_m2 = area_pixels * (PIXEL_SIZE_M ** 2)
            area_ha = area_m2 / 10000
            
            # Filter by minimum area
            if area_ha < min_area_ha:
                continue
            
            # Convert contour to polygon
            try:
                # Get contour points in pixel coordinates
                points = contour.squeeze()
                
                # Handle single point or line contours
                if points.ndim != 2 or len(points) < 3:
                    continue
                
                # Convert pixel coordinates to geographic coordinates
                geo_points = []
                for point in points:
                    x, y = point
                    # Convert from pixel to geographic using transform
                    lon = self.bounds[0] + (x / self.mask.shape[1]) * (self.bounds[2] - self.bounds[0])
                    lat = self.bounds[3] - (y / self.mask.shape[0]) * (self.bounds[3] - self.bounds[1])
                    geo_points.append([lon, lat])
                
                # Create polygon
                polygon = Polygon(geo_points)
                
                # Simplify polygon
                if simplify_tolerance > 0:
                    polygon = polygon.simplify(simplify_tolerance, preserve_topology=True)
                
                # Skip invalid polygons
                if not polygon.is_valid or polygon.is_empty:
                    continue
                
                # Calculate properties
                centroid = polygon.centroid
                bounds = polygon.bounds  # (minx, miny, maxx, maxy)
                
                # Calculate confidence (average prediction value in polygon region)
                confidence = self._calculate_confidence(contour)
                
                # Create zone dictionary
                zone = {
                    'id': f"zone_{idx + 1}",
                    'zone_number': idx + 1,
                    'area_ha': round(area_ha, 3),
                    'area_m2': round(area_m2, 2),
                    'perimeter_m': round(cv2.arcLength(contour, True) * PIXEL_SIZE_M, 2),
                    'centroid_lat': round(centroid.y, 6),
                    'centroid_lon': round(centroid.x, 6),
                    'confidence': round(confidence, 3),
                    'bounds': {
                        'min_lon': round(bounds[0], 6),
                        'min_lat': round(bounds[1], 6),
                        'max_lon': round(bounds[2], 6),
                        'max_lat': round(bounds[3], 6)
                    },
                    'geometry': mapping(polygon),
                    'detected_date': datetime.now().strftime('%Y-%m-%d'),
                    'status': self._classify_status(area_ha, confidence),
                    'priority': self._calculate_priority(area_ha, confidence)
                }
                
                zones.append(zone)
                
            except Exception as e:
                print(f" Error processing contour {idx}: {e}")
                continue
        
        # Sort by area (largest first)
        zones.sort(key=lambda x: x['area_ha'], reverse=True)
        
        print(f" Extracted {len(zones)} valid zones")
        
        # Print summary
        if zones:
            total_area = sum(z['area_ha'] for z in zones)
            avg_confidence = sum(z['confidence'] for z in zones) / len(zones)
            print(f"   Total mining area: {total_area:.2f} ha")
            print(f"   Average confidence: {avg_confidence:.2%}")
            print(f"   Largest zone: {zones[0]['area_ha']:.2f} ha")
            print(f"   Smallest zone: {zones[-1]['area_ha']:.2f} ha")
        
        return zones
    
    def _calculate_confidence(self, contour):
        """Calculate confidence score for a contour"""
        # Create mask for this contour
        contour_mask = np.zeros_like(self.mask, dtype=np.uint8)
        cv2.drawContours(contour_mask, [contour], 0, 1, -1)
        
        # Calculate average prediction value
        if np.sum(contour_mask) == 0:
            return 0.5
        
        confidence = np.sum(self.mask * contour_mask) / np.sum(contour_mask)
        return float(confidence)
    
    def _classify_status(self, area_ha, confidence):
        """Classify zone status based on area and confidence"""
        # More strict classification to reduce false positives
        if confidence >= 0.95 and area_ha >= 5.0:
            return 'confirmed_active'
        elif confidence >= 0.90 and area_ha >= 2.0:
            return 'likely_active'
        elif confidence >= 0.80 and area_ha >= 0.5:
            return 'suspected'
        else:
            return 'low_confidence'
    
    def _calculate_priority(self, area_ha, confidence):
        """Calculate priority level (1-5, 5 = highest)"""
        # More conservative priority calculation
        # Requires both high confidence AND significant area for high priority
        
        # Critical: Large area + very high confidence
        if area_ha >= 10.0 and confidence >= 0.95:
            return 5  # Critical - definitely needs inspection
        
        # High: Moderate to large area + high confidence
        elif area_ha >= 5.0 and confidence >= 0.90:
            return 4  # High priority
        
        # Medium: Significant area OR high confidence (but not both)
        elif (area_ha >= 2.0 and confidence >= 0.85) or (area_ha >= 5.0 and confidence >= 0.80):
            return 3  # Medium priority
        
        # Low: Small area or lower confidence
        elif area_ha >= 1.0 and confidence >= 0.75:
            return 2  # Low priority
        
        # Very Low: Everything else
        else:
            return 1  # Very low - likely false positive
    
    def save_zones_geojson(self, zones, output_path):
        """Save zones as GeoJSON"""
        try:
            geojson = {
                'type': 'FeatureCollection',
                'features': [],
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'total_zones': len(zones),
                    'total_area_ha': sum(z['area_ha'] for z in zones),
                    'bounds': self.bounds
                }
            }
            
            for zone in zones:
                feature = {
                    'type': 'Feature',
                    'geometry': zone['geometry'],
                    'properties': {
                        k: v for k, v in zone.items() 
                        if k != 'geometry'
                    }
                }
                geojson['features'].append(feature)
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            print(f" Zones saved to {output_path}")
            return True
            
        except Exception as e:
            print(f" Error saving GeoJSON: {e}")
            return False
    
    def visualize_zones(self, zones, output_path=None):
        """Create visualization of detected zones"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.patches import Polygon as MplPolygon
            
            fig, ax = plt.subplots(figsize=(14, 10))
            
            # Show base mask
            ax.imshow(self.mask, cmap='Greys', alpha=0.5, extent=[
                self.bounds[0], self.bounds[2],
                self.bounds[1], self.bounds[3]
            ])
            
            # Draw each zone
            colors = plt.cm.RdYlGn_r(np.linspace(0, 1, 10))
            
            for zone in zones:
                coords = zone['geometry']['coordinates'][0]
                polygon = MplPolygon(
                    coords,
                    facecolor=colors[zone['priority'] - 1],
                    edgecolor='red',
                    linewidth=2,
                    alpha=0.6,
                    label=f"Zone {zone['zone_number']}: {zone['area_ha']:.2f} ha"
                )
                ax.add_patch(polygon)
                
                # Add label at centroid
                ax.text(
                    zone['centroid_lon'],
                    zone['centroid_lat'],
                    f"{zone['zone_number']}",
                    fontsize=12,
                    fontweight='bold',
                    color='white',
                    ha='center',
                    va='center',
                    bbox=dict(boxstyle='circle', facecolor='red', alpha=0.8)
                )
            
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            ax.set_title('Detected Mining Zones', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Legend
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(
                    handles[:min(10, len(handles))],
                    labels[:min(10, len(labels))],
                    loc='upper right',
                    fontsize=10
                )
            
            plt.tight_layout()
            
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                print(f" Visualization saved to {output_path}")
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            print(f" Error creating visualization: {e}")
            return False


def extract_zones_from_prediction(prediction_path, bounds=None, output_dir=None):
    """
    Main function to extract zones from a prediction file
    
    Args:
        prediction_path: Path to prediction GeoTIFF or numpy array
        bounds: Geographic bounds [min_lon, min_lat, max_lon, max_lat]
        output_dir: Directory to save outputs
        
    Returns:
        List of extracted zones
    """
    print("\n" + "="*60)
    print(" EXTRACTING MINING ZONES FROM PREDICTION")
    print("="*60)
    
    try:
        # Load prediction
        if isinstance(prediction_path, (str, Path)):
            prediction_path = Path(prediction_path)
            
            if prediction_path.suffix == '.tif':
                # Load GeoTIFF
                with rasterio.open(prediction_path) as src:
                    mask = src.read(1)
                    if bounds is None:
                        bounds_obj = src.bounds
                        bounds = [bounds_obj.left, bounds_obj.bottom, 
                                 bounds_obj.right, bounds_obj.top]
                    transform = src.transform
            else:
                # Load numpy array
                mask = np.load(prediction_path)
                transform = None
        else:
            # Assume it's already a numpy array
            mask = prediction_path
            transform = None
        
        # Create extractor
        extractor = MiningZoneExtractor(mask, bounds, transform)
        
        # Extract zones
        zones = extractor.extract_zones(min_area_ha=0.1)
        
        # Save outputs if directory specified
        if output_dir and zones:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save GeoJSON
            geojson_path = output_dir / 'detected_zones.geojson'
            extractor.save_zones_geojson(zones, geojson_path)
            
            # Save visualization
            viz_path = output_dir / 'detected_zones_map.png'
            extractor.visualize_zones(zones, viz_path)
            
            # Save summary JSON
            summary_path = output_dir / 'zones_summary.json'
            with open(summary_path, 'w') as f:
                json.dump({
                    'extraction_date': datetime.now().isoformat(),
                    'total_zones': len(zones),
                    'total_area_ha': sum(z['area_ha'] for z in zones),
                    'zones': zones
                }, f, indent=2)
            print(f" Summary saved to {summary_path}")
        
        print("\n" + "="*60)
        print(" ZONE EXTRACTION COMPLETED")
        print("="*60)
        
        return zones
        
    except Exception as e:
        print(f" Error extracting zones: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_mining_zones.py <prediction_path> [output_dir]")
        sys.exit(1)
    
    prediction_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'mining_zones_output'
    
    zones = extract_zones_from_prediction(prediction_path, output_dir=output_dir)
    
    if zones:
        print(f"\n Extracted {len(zones)} zones:")
        for zone in zones[:5]:  # Show top 5
            print(f"   Zone {zone['zone_number']}: {zone['area_ha']:.2f} ha "
                  f"(Priority: {zone['priority']}, Status: {zone['status']})")
