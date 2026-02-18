import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import warnings
from skimage.measure import block_reduce
warnings.filterwarnings('ignore')

# Setting up the page configuration
st.set_page_config(
    page_title="Mining Hotspot Detection Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        color: #212529;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        margin: 0.5rem 0;
        color: #495057;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #0066cc;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
    }
    
    .success-box {
        background-color: #e8f5e8;
        border-left: 4px solid #28a745;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
    }
    
    .stButton>button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #0056b3;
    }
    
    h3 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


class MiningDashboard:
    """In this class, we're creating an enhanced dashboard for mining hotspot visualization"""

    def __init__(self):
        self.prob_map = None
        self.transform = None
        self.crs = None
        self.training_data_gdf = None
        self.metadata = None
        self.load_data()

    def load_data(self):
        """Load the probability map and training data with caching and downsampling"""
        try:
            # Loading the probability map from the trained model output
            with rasterio.open('outputs/mining_probability_map.tif') as src:
                # Downsampling by factor of 4 for faster processing 
                downsample_factor = 4
                prob_map_full = src.read(1)
                
                # Downsampling using block mean
                self.prob_map = block_reduce(prob_map_full, (downsample_factor, downsample_factor), np.mean)
                
                self.transform = src.transform * src.transform.scale(downsample_factor, downsample_factor)
                self.crs = src.crs
                self.bounds = src.bounds  
                
                # Getting the center in WGS84 for proper map centering
                from pyproj import Transformer
                transformer = Transformer.from_crs(self.crs, "EPSG:4326", always_xy=True)
                
                # Calculating the center from bounds
                center_x = (self.bounds.left + self.bounds.right) / 2
                center_y = (self.bounds.bottom + self.bounds.top) / 2
                
                # Transforming to WGS84
                self.center_lon, self.center_lat = transformer.transform(center_x, center_y)

            # Loading training data
            self.training_data_gdf = gpd.read_file('chingola_TrainingData_PERFECT.geojson')
            if self.training_data_gdf.crs != self.crs:
                self.training_data_gdf = self.training_data_gdf.to_crs(self.crs)
            
            # Loading metadata
            try:
                with open('chingola_Metadata_PERFECT.geojson', 'r') as f:
                    metadata_json = json.load(f)
                    if 'features' in metadata_json and len(metadata_json['features']) > 0:
                        self.metadata = metadata_json['features'][0]['properties']
            except:
                self.metadata = None

            st.success("Data loaded successfully!")

        except FileNotFoundError as e:
            st.error(f"Required file not found: {e}")
            st.error("Please ensure the mining detection pipeline has been run first.")
            st.stop()
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()

    @st.cache_data
    def create_hotspots_dataframe(_self, threshold=0.5, max_hotspots=50):
        """Create a DataFrame containing top detected hotspots above threshold (cached for performance)"""
        if _self.prob_map is None:
            return pd.DataFrame()

        flat_prob = _self.prob_map.flatten()
        indices_above_threshold = np.where(flat_prob > threshold)[0]
        
        if len(indices_above_threshold) == 0:
            return pd.DataFrame()
        
        # Getting probabilities for these indices
        probs_above = flat_prob[indices_above_threshold]
       
        sorted_indices = np.argsort(probs_above)[::-1][:max_hotspots]
        top_indices = indices_above_threshold[sorted_indices]
        top_probs = probs_above[sorted_indices]
        rows, cols = np.unravel_index(top_indices, _self.prob_map.shape)
        
        # Converting pixel coordinates to geographic coordinates (only for top hotspots)
        lon_coords = []
        lat_coords = []

        for row, col in zip(rows, cols):
            # Converting pixel to geographic coordinates using rasterio transform
            lon, lat = rasterio.transform.xy(_self.transform, row, col, offset='center')
            
            # Doing UTM to WGS84 conversion
            from pyproj import Transformer
            transformer = Transformer.from_crs(_self.crs, "EPSG:4326", always_xy=True)
            lon_wgs84, lat_wgs84 = transformer.transform(lon, lat)
            
            lon_coords.append(lon_wgs84)
            lat_coords.append(lat_wgs84)

        hotspots_df = pd.DataFrame({
            'longitude': lon_coords,
            'latitude': lat_coords,
            'probability': top_probs,
            'pixel_row': rows,
            'pixel_col': cols
        })

        hotspots_df['google_maps'] = hotspots_df.apply(
            lambda row: f"https://www.google.com/maps?q={row['latitude']},{row['longitude']}",
            axis=1
        )

        hotspots_df = hotspots_df.reset_index(drop=True)

        return hotspots_df

    def create_folium_map(self, threshold=0.5, show_training_data=False):
        """Create an interactive Folium map with hotspots"""

        center_lat = self.center_lat
        center_lon = self.center_lon

        # Creating the map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )

        # Adding satellite imagery layer
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles &copy; Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)

        # Adding detected hotspots
        hotspots_df = self.create_hotspots_dataframe(threshold, max_hotspots=50)

        if not hotspots_df.empty:
            # Creating feature group for detected hotspots
            detected_group = folium.FeatureGroup(name=f'Hotspots (>{threshold:.2f})', show=True)

            for idx, hotspot in hotspots_df.iterrows():
                prob = hotspot['probability']
                if prob > 0.7:
                    color = 'red'
                elif prob > 0.5:
                    color = 'orange'
                else:
                    color = 'yellow'

                popup_html = f"""
                <div style="width:200px">
                    <h4>Hotspot #{idx+1}</h4>
                    <b>Probability:</b> {prob:.3f}<br>
                    <b>Coords:</b> {hotspot['latitude']:.6f}, {hotspot['longitude']:.6f}<br>
                    <hr>
                    <a href="{hotspot['google_maps']}" target="_blank" style="color:#1f77b4">
                        Open in Google Maps
                    </a>
                </div>
                """

                folium.Marker(
                    location=[hotspot['latitude'], hotspot['longitude']],
                    popup=folium.Popup(popup_html, max_width=250),
                    icon=folium.Icon(color=color),
                    tooltip=f"Prob: {prob:.3f}"
                ).add_to(detected_group)

            detected_group.add_to(m)

        folium.LayerControl().add_to(m)

        return m, hotspots_df

    def get_hotspots_count(self, threshold=0.5):
        """Get the total number of hotspots above threshold without creating full dataframe"""
        if self.prob_map is None:
            return 0
        return np.sum(self.prob_map > threshold)

    def get_statistics(self, threshold=0.5):
        """Calculate comprehensive statistics for government reporting"""
        if self.prob_map is None:
            return {}

        hotspots_df = self.create_hotspots_dataframe(threshold, max_hotspots=1000)

        total_hotspots = self.get_hotspots_count(threshold)
        total_pixels = self.prob_map.size
        coverage_area_km2 = (total_hotspots * 0.0025) / 1000000  

        stats = {
            'total_pixels': total_pixels,
            'detected_hotspots': total_hotspots,
            'estimated_area_km2': round(coverage_area_km2, 3),
            'max_probability': float(self.prob_map.max()),
            'mean_probability': float(self.prob_map.mean()),
            'threshold': threshold,
            'coverage_percentage': total_hotspots / total_pixels * 100,
            'confidence_levels': {
                'high': len(hotspots_df[hotspots_df['probability'] > 0.8]),
                'medium': len(hotspots_df[(hotspots_df['probability'] > 0.6) & (hotspots_df['probability'] <= 0.8)]),
                'low': len(hotspots_df[hotspots_df['probability'] <= 0.6])
            },
            'performance_metrics': {
                'recall': 0.47,  
                'precision': 0.96,
                'f1_score': 0.63
            }
        }

        if not hotspots_df.empty:
            stats.update({
                'top_probability': float(hotspots_df.iloc[0]['probability']),
                'median_probability': float(hotspots_df['probability'].median()),
                'hotspots_by_region': 'Analysis pending'  
            })

        return stats


def main():
    """Main Streamlit application function"""

    st.title("Mining Hotspot Detection")

    dashboard = MiningDashboard()
    threshold = st.sidebar.slider(
        "Detection Threshold",
        min_value=0.1,
        max_value=0.9,
        value=0.426,
        step=0.01,
        help="Minimum probability for hotspot detection"
    )

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Detection Map")

        # Creating and display map
        with st.spinner("Loading map..."):
            m, hotspots_df = dashboard.create_folium_map(threshold, show_training_data=False)

        st_folium(m, width=800, height=600)

        # Hotspots table
        if not hotspots_df.empty:
            st.subheader(f"Top {len(hotspots_df)} Hotspots")
            
            display_df = hotspots_df[['probability', 'latitude', 'longitude', 'google_maps']].copy()
            display_df.columns = ['Probability', 'Latitude', 'Longitude', 'Google Maps']
            display_df['Probability'] = display_df['Probability'].round(4)
            display_df['Latitude'] = display_df['Latitude'].round(6)
            display_df['Longitude'] = display_df['Longitude'].round(6)
            
            
            display_df['Google Maps'] = display_df['Google Maps'].apply(
                lambda x: f'<a href="{x}" target="_blank">Open Map</a>'
            )
            
            st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
        
            csv = hotspots_df.to_csv(index=False)
            st.download_button(
                label="Download Hotspots (CSV)",
                data=csv,
                file_name=f"hotspots_{threshold:.2f}.csv",
                mime="text/csv"
            )

    with col2:
        st.subheader("Statistics")

        stats = dashboard.get_statistics(threshold)

        st.metric("Detections", f"{stats['detected_hotspots']:,}")
        st.metric("Max Probability", f"{stats['max_probability']:.1%}")
        st.metric("Coverage", f"{stats['coverage_percentage']:.2f}%")


if __name__ == "__main__":
    main()
