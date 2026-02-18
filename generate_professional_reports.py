"""
Professional Report Generator for Mining Hotspot Detection
==========================================================
Generates comprehensive PDF and Excel reports with findings, statistics,
maps, and recommendations for stakeholders.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import rasterio
import geopandas as gpd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO


class ProfessionalReportGenerator:
    """Generate professional reports for mining detection results"""
    
    def __init__(self, prob_map_path, ground_truth_path):
        self.prob_map_path = prob_map_path
        self.ground_truth_path = ground_truth_path
        self.load_data()
        
    def load_data(self):
        """Load probability map and ground truth"""
        #  probability map
        with rasterio.open(self.prob_map_path) as src:
            self.prob_map = src.read(1)
            self.transform = src.transform
            self.crs = src.crs
            self.bounds = src.bounds
        
        #  ground truth
        self.ground_truth = gpd.read_file(self.ground_truth_path)
        
    def calculate_comprehensive_stats(self, threshold=0.5):
        """Calculate comprehensive statistics"""
        stats = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'threshold': threshold,
            'total_pixels': self.prob_map.size,
            'image_dimensions': f"{self.prob_map.shape[0]} × {self.prob_map.shape[1]}",
            'max_probability': float(self.prob_map.max()),
            'min_probability': float(self.prob_map.min()),
            'mean_probability': float(self.prob_map.mean()),
            'std_probability': float(self.prob_map.std()),
            'detected_hotspots': int(np.sum(self.prob_map > threshold)),
            'coverage_percentage': float(np.sum(self.prob_map > threshold) / self.prob_map.size * 100),
            'ground_truth_count': len(self.ground_truth)
        }
        
        # Confidence level breakdown
        stats['confidence_breakdown'] = {
            'critical (>70%)': int(np.sum(self.prob_map > 0.7)),
            'high (50-70%)': int(np.sum((self.prob_map > 0.5) & (self.prob_map <= 0.7))),
            'medium (30-50%)': int(np.sum((self.prob_map > 0.3) & (self.prob_map <= 0.5))),
            'low (10-30%)': int(np.sum((self.prob_map > 0.1) & (self.prob_map <= 0.3))),
            'minimal (<10%)': int(np.sum(self.prob_map <= 0.1))
        }
        
        return stats
    
    def get_top_hotspots(self, n=10, threshold=0.5):
        """Get top N hotspots with geographic coordinates"""
        # Finding pixels above threshold
        rows, cols = np.where(self.prob_map > threshold)
        probabilities = self.prob_map[rows, cols]
        
        # Converting pixel coordinates to geographic coordinates
        hotspots = []
        for row, col, prob in zip(rows, cols, probabilities):
            lon, lat = self.transform * (col + 0.5, row + 0.5)
            hotspots.append({
                'rank': 0,
                'latitude': lat,
                'longitude': lon,
                'probability': prob,
                'pixel_row': row,
                'pixel_col': col
            })
        
        # Sorting by probability and get top N
        hotspots_df = pd.DataFrame(hotspots).sort_values('probability', ascending=False).head(n)
        hotspots_df['rank'] = range(1, len(hotspots_df) + 1)
        
        return hotspots_df
    
    def generate_visualizations(self):
        """Generate all visualizations for the report"""
        visualizations = {}
        
        #  Probability distribution histogram
        fig, ax = plt.subplots(figsize=(8, 5))
        plt.hist(self.prob_map.flatten()[self.prob_map.flatten() > 0.01], bins=50, 
                 color='#667eea', edgecolor='black', alpha=0.7)
        plt.xlabel('Mining Probability', fontsize=12, fontweight='bold')
        plt.ylabel('Frequency', fontsize=12, fontweight='bold')
        plt.title('Distribution of Mining Probabilities', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        visualizations['histogram'] = buf
        plt.close()
        
        # Confidence levels pie chart
        confidence_data = {
            'Critical\n(>70%)': int(np.sum(self.prob_map > 0.7)),
            'High\n(50-70%)': int(np.sum((self.prob_map > 0.5) & (self.prob_map <= 0.7))),
            'Medium\n(30-50%)': int(np.sum((self.prob_map > 0.3) & (self.prob_map <= 0.5))),
            'Low\n(<30%)': int(np.sum(self.prob_map <= 0.3))
        }
        
        fig, ax = plt.subplots(figsize=(8, 8))
        colors_pie = ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
        plt.pie(confidence_data.values(), labels=confidence_data.keys(), autopct='%1.2f%%',
                colors=colors_pie, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
        plt.title('Hotspot Detection Confidence Levels', fontsize=14, fontweight='bold', pad=20)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        visualizations['pie_chart'] = buf
        plt.close()
        
        # Probability heatmap (downsampled for report)
        fig, ax = plt.subplots(figsize=(10, 6))
        # Downsample for visualization
        downsample_factor = 10
        prob_downsampled = self.prob_map[::downsample_factor, ::downsample_factor]
        im = ax.imshow(prob_downsampled, cmap='YlOrRd', aspect='auto', interpolation='bilinear')
        plt.colorbar(im, ax=ax, label='Mining Probability')
        plt.title('Mining Hotspot Probability Map', fontsize=14, fontweight='bold')
        plt.xlabel('Longitude (pixels)', fontsize=12)
        plt.ylabel('Latitude (pixels)', fontsize=12)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        visualizations['heatmap'] = buf
        plt.close()
        
        return visualizations
    
    def generate_excel_report(self, output_path, threshold=0.5):
        """Generate comprehensive Excel report"""
        stats = self.calculate_comprehensive_stats(threshold)
        hotspots_df = self.get_top_hotspots(n=50, threshold=threshold)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Analysis Date',
                    'Detection Threshold',
                    'Total Pixels Analyzed',
                    'Image Dimensions',
                    'Total Detections',
                    'Detection Coverage (%)',
                    'Maximum Probability',
                    'Mean Probability',
                    'Standard Deviation',
                    'Ground Truth Hotspots'
                ],
                'Value': [
                    stats['analysis_date'],
                    f"{stats['threshold']:.2f}",
                    f"{stats['total_pixels']:,}",
                    stats['image_dimensions'],
                    f"{stats['detected_hotspots']:,}",
                    f"{stats['coverage_percentage']:.4f}%",
                    f"{stats['max_probability']:.4f}",
                    f"{stats['mean_probability']:.4f}",
                    f"{stats['std_probability']:.4f}",
                    f"{stats['ground_truth_count']}"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Confidence breakdown sheet
            confidence_df = pd.DataFrame([
                {'Confidence Level': k, 'Count': v, 'Percentage': f"{v/stats['total_pixels']*100:.4f}%"} 
                for k, v in stats['confidence_breakdown'].items()
            ])
            confidence_df.to_excel(writer, sheet_name='Confidence Breakdown', index=False)
            
            # Top hotspots sheet
            hotspots_export = hotspots_df[['rank', 'latitude', 'longitude', 'probability']].copy()
            hotspots_export['probability'] = hotspots_export['probability'].round(4)
            hotspots_export.to_excel(writer, sheet_name='Top Hotspots', index=False)
            
        print(f"✅ Excel report generated: {output_path}")
        return output_path
    
    def export_geojson(self, output_path, threshold=0.5):
        """Export detected hotspots as GeoJSON"""
        hotspots_df = self.get_top_hotspots(n=1000, threshold=threshold)
        
        # Create GeoDataFrame
        from shapely.geometry import Point
        geometry = [Point(lon, lat) for lon, lat in zip(hotspots_df['longitude'], hotspots_df['latitude'])]
        gdf = gpd.GeoDataFrame(hotspots_df, geometry=geometry, crs=self.crs)
        
        # Export
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"✅ GeoJSON exported: {output_path}")
        return output_path


def generate_all_reports(threshold=0.5):
    """Generate all report formats"""
    print("📊 Generating Professional Reports...")
    
    report_gen = ProfessionalReportGenerator(
        'outputs/mining_probability_map.tif',
        'chingola_Top30_Hotspots.geojson'
    )
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
  
    excel_path = f'outputs/mining_detection_report_{timestamp}.xlsx'
    report_gen.generate_excel_report(excel_path, threshold)
    
    geojson_path = f'outputs/detected_hotspots_{timestamp}.geojson'
    report_gen.export_geojson(geojson_path, threshold)
    
    viz = report_gen.generate_visualizations()
    
    for name, buf in viz.items():
        with open(f'outputs/viz_{name}_{timestamp}.png', 'wb') as f:
            f.write(buf.getvalue())
    
    print("All reports generated successfully!")
    print(f"   - Excel: {excel_path}")
    print(f"   - GeoJSON: {geojson_path}")
    print(f"   - Visualizations: outputs/viz_*_{timestamp}.png")
    
    return excel_path, geojson_path


if __name__ == "__main__":
    generate_all_reports(threshold=0.5)