# Mining Detection Web Application
# A Streamlit app to visualize U-Net mining detection results

import streamlit as st
import rasterio
from rasterio.plot import reshape_as_image
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# Set page config
st.set_page_config(
    page_title="Mining Detection System",
    page_icon="⛏️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("⛏️ Mining Area Detection & Change Analysis")
st.markdown("**AI-Powered Mining Detection using U-Net Deep Learning**")
st.markdown("---")

# Sidebar
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Select View", [
    "🏠 Overview",
    "📍 Ground Truth Analysis", 
    "🤖 Model Predictions",
    "📈 Change Detection",
    "📊 Statistics & Metrics",
    "🔍 Interactive Comparison"
])

st.sidebar.markdown("---")
st.sidebar.info("""
**Project:** Mining Detection System  
**Location:** Chingola, Zambia  
**Time Period:** 2016 - 2025  
**Model:** U-Net Deep Learning
""")

# File paths
RESULTS_DIR = "Mining_Analysis_Results"
MODELS_DIR = "models"

def load_geotiff(filepath):
    """Load a GeoTIFF file"""
    try:
        with rasterio.open(filepath) as src:
            data = src.read()
            if data.shape[0] > 1:  # Multi-band
                # Take first 3 bands for RGB visualization
                data = data[:3]
                data = reshape_as_image(data)
            else:  # Single band
                data = data[0]
            return data, src.meta
    except Exception as e:
        st.error(f"Error loading {filepath}: {e}")
        return None, None

def calculate_area(mask, pixel_size_m=9.8):
    """Calculate area in hectares"""
    mining_pixels = np.sum(mask == 1)
    area_m2 = mining_pixels * (pixel_size_m ** 2)
    area_ha = area_m2 / 10000
    return area_ha

# ====================
# PAGE: OVERVIEW
# ====================
if page == "🏠 Overview":
    st.header("🏠 Project Overview")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("About This System")
        st.write("""
        This application demonstrates an AI-powered system for detecting and monitoring 
        mining activities using satellite imagery and deep learning.
        
        **Key Features:**
        - 🛰️ Satellite image analysis (5-band multispectral)
        - 🤖 U-Net deep learning architecture
        - 📊 Automatic mining area detection
        - 📈 Change detection over time (2016-2025)
        - 🗺️ Geospatial accuracy preservation
        """)
        
        st.subheader("How It Works")
        st.write("""
        1. **Data Preparation:** Vector polygons converted to binary masks
        2. **Model Training:** U-Net trained on 256×256 patches
        3. **Prediction:** Sliding window inference on full images
        4. **Change Detection:** Pixel-wise comparison between years
        """)
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        # Load and display quick metrics
        try:
            mask, _ = load_geotiff(f"{RESULTS_DIR}/chingola_multiclass_mask.tif")
            if mask is not None:
                total_pixels = mask.size
                mining_pixels = np.sum(mask == 1)
                mining_pct = (mining_pixels / total_pixels) * 100
                area_ha = calculate_area(mask)
                
                st.metric("Total Area Analyzed", f"{total_pixels/1e6:.1f}M pixels")
                st.metric("Mining Coverage (2016)", f"{mining_pct:.2f}%")
                st.metric("Mining Area", f"{area_ha:.1f} hectares")
        except:
            st.warning("Load data to see statistics")
        
        st.subheader("🎯 Model Info")
        st.write("""
        **Architecture:** U-Net  
        **Input:** 5 spectral bands  
        **Output:** Binary segmentation  
        **Parameters:** ~13.4M  
        **Training:** 50 epochs  
        """)
    
    st.markdown("---")
    st.info("👈 Use the sidebar to navigate through different analysis views")

# ====================
# PAGE: GROUND TRUTH
# ====================
elif page == "📍 Ground Truth Analysis":
    st.header("📍 Ground Truth Analysis")
    
    st.write("""
    Ground truth data consists of manually labeled mining polygons converted to raster masks.
    This serves as the training target for the U-Net model.
    """)
    
    # Load mask visualization
    mask_viz_path = f"{RESULTS_DIR}/mask_visualization.png"
    if os.path.exists(mask_viz_path):
        st.subheader("Mask Visualization")
        img = Image.open(mask_viz_path)
        st.image(img, use_container_width=True)
    
    # Load and analyze mask
    mask_path = f"{RESULTS_DIR}/chingola_multiclass_mask.tif"
    if os.path.exists(mask_path):
        mask, meta = load_geotiff(mask_path)
        
        if mask is not None:
            col1, col2, col3 = st.columns(3)
            
            total_pixels = mask.size
            background = np.sum(mask == 0)
            mining = np.sum(mask == 1)
            
            with col1:
                st.metric("Total Pixels", f"{total_pixels:,}")
            with col2:
                st.metric("Background Pixels", f"{background:,}")
                st.caption(f"{(background/total_pixels)*100:.2f}%")
            with col3:
                st.metric("Mining Pixels", f"{mining:,}")
                st.caption(f"{(mining/total_pixels)*100:.2f}%")
            
            st.subheader("Class Distribution")
            fig, ax = plt.subplots(figsize=(10, 4))
            classes = ['Background', 'Mining']
            values = [background, mining]
            colors = ['#87CEEB', '#FF4B4B']
            ax.bar(classes, values, color=colors)
            ax.set_ylabel('Number of Pixels')
            ax.set_title('Ground Truth Class Distribution')
            for i, v in enumerate(values):
                ax.text(i, v, f'{v:,}\n({(v/total_pixels)*100:.1f}%)', 
                       ha='center', va='bottom')
            st.pyplot(fig)
            
            # Edge analysis
            edge_path = f"{RESULTS_DIR}/mask_edge_analysis.png"
            if os.path.exists(edge_path):
                st.subheader("Edge Quality Analysis")
                edge_img = Image.open(edge_path)
                st.image(edge_img, use_container_width=True)

# ====================
# PAGE: PREDICTIONS
# ====================
elif page == "🤖 Model Predictions":
    st.header("🤖 Model Predictions")
    
    st.write("""
    U-Net model predictions on 2016 and 2025 satellite images.
    The model identifies mining areas with high accuracy.
    """)
    
    year = st.selectbox("Select Year", ["2016", "2025"])
    
    pred_path = f"{RESULTS_DIR}/prediction_{year}.tif"
    
    if os.path.exists(pred_path):
        pred, meta = load_geotiff(pred_path)
        
        if pred is not None:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"{year} Prediction Map")
                fig, ax = plt.subplots(figsize=(12, 8))
                cmap = plt.cm.colors.ListedColormap(['#87CEEB', '#FF4B4B'])
                im = ax.imshow(pred, cmap=cmap)
                ax.set_title(f'Mining Detection - {year}', fontsize=16, fontweight='bold')
                ax.axis('off')
                cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                cbar.set_ticks([0.25, 0.75])
                cbar.set_ticklabels(['Background', 'Mining'])
                st.pyplot(fig)
            
            with col2:
                st.subheader("Statistics")
                total = pred.size
                mining = np.sum(pred == 1)
                background = np.sum(pred == 0)
                
                st.metric("Mining Pixels", f"{mining:,}")
                st.metric("Coverage", f"{(mining/total)*100:.2f}%")
                st.metric("Area", f"{calculate_area(pred):.1f} ha")
                
                st.markdown("---")
                st.write("**Class Distribution:**")
                st.progress(mining / total)
                st.caption(f"Mining: {mining:,} ({(mining/total)*100:.1f}%)")
                st.progress(background / total)
                st.caption(f"Background: {background:,} ({(background/total)*100:.1f}%)")
    else:
        st.warning(f"Prediction file for {year} not found.")

# ====================
# PAGE: CHANGE DETECTION
# ====================
elif page == "📈 Change Detection":
    st.header("📈 Change Detection Analysis")
    
    st.write("""
    Comparison of mining areas between 2016 and 2025 to identify:
    - 🟢 **New mining areas** (expansion)
    - 🔴 **Removed mining areas** (rehabilitation/closure)
    - ⚪ **Unchanged areas**
    """)
    
    # Load inference results
    inference_path = f"{RESULTS_DIR}/inference_results.png"
    if os.path.exists(inference_path):
        st.subheader("Complete Analysis")
        img = Image.open(inference_path)
        st.image(img, use_container_width=True)
    
    # Load change map
    change_path = f"{RESULTS_DIR}/change_map.tif"
    pred_2016_path = f"{RESULTS_DIR}/prediction_2016.tif"
    pred_2025_path = f"{RESULTS_DIR}/prediction_2025.tif"
    
    if all(os.path.exists(p) for p in [change_path, pred_2016_path, pred_2025_path]):
        change_map, _ = load_geotiff(change_path)
        pred_2016, _ = load_geotiff(pred_2016_path)
        pred_2025, _ = load_geotiff(pred_2025_path)
        
        if all(x is not None for x in [change_map, pred_2016, pred_2025]):
            # Calculate actual change (reconstruct from predictions)
            actual_change = pred_2025.astype(int) - pred_2016.astype(int)
            
            col1, col2, col3 = st.columns(3)
            
            new_mining = np.sum(actual_change == 1)
            removed_mining = np.sum(actual_change == -1)
            unchanged = np.sum(actual_change == 0)
            
            with col1:
                st.metric("🟢 New Mining", f"{new_mining:,} pixels")
                st.caption(f"{calculate_area(actual_change == 1):.1f} hectares")
            
            with col2:
                st.metric("🔴 Mining Removed", f"{removed_mining:,} pixels")
                st.caption(f"{calculate_area(actual_change == -1):.1f} hectares")
            
            with col3:
                st.metric("⚪ Unchanged", f"{unchanged:,} pixels")
                st.caption(f"{(unchanged/actual_change.size)*100:.1f}%")
            
            # Visualization
            st.subheader("Change Map Visualization")
            fig, ax = plt.subplots(figsize=(14, 8))
            cmap = plt.cm.colors.ListedColormap(['#FF4B4B', '#E0E0E0', '#4CAF50'])
            bounds = [-1.5, -0.5, 0.5, 1.5]
            norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)
            im = ax.imshow(actual_change, cmap=cmap, norm=norm)
            ax.set_title('Mining Change Detection (2016 → 2025)', 
                        fontsize=16, fontweight='bold')
            ax.axis('off')
            cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_ticks([-1, 0, 1])
            cbar.set_ticklabels(['Removed', 'Unchanged', 'New Mining'])
            st.pyplot(fig)
            
            # Change statistics
            st.subheader("Change Analysis")
            
            mining_2016 = np.sum(pred_2016 == 1)
            mining_2025 = np.sum(pred_2025 == 1)
            net_change = mining_2025 - mining_2016
            percent_change = (net_change / mining_2016) * 100 if mining_2016 > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("2016 Mining Area", 
                         f"{calculate_area(pred_2016):.1f} ha",
                         f"{mining_2016:,} pixels")
            with col2:
                st.metric("2025 Mining Area", 
                         f"{calculate_area(pred_2025):.1f} ha",
                         f"{mining_2025:,} pixels")
            
            st.metric("Net Change (2016 → 2025)", 
                     f"{abs(calculate_area(np.full_like(pred_2016, net_change >= 0).astype(int) * abs(net_change))):.1f} ha",
                     f"{percent_change:+.1f}%",
                     delta_color="normal" if net_change >= 0 else "inverse")

# ====================
# PAGE: STATISTICS
# ====================
elif page == "📊 Statistics & Metrics":
    st.header("📊 Statistics & Metrics")
    
    st.subheader("Model Performance")
    
    # Model info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Model Architecture", "U-Net")
    with col2:
        st.metric("Parameters", "~13.4M")
    with col3:
        st.metric("Training Epochs", "50")
    
    st.markdown("---")
    
    # Load all predictions and calculate metrics
    files = {
        "Ground Truth": f"{RESULTS_DIR}/chingola_multiclass_mask.tif",
        "Prediction 2016": f"{RESULTS_DIR}/prediction_2016.tif",
        "Prediction 2025": f"{RESULTS_DIR}/prediction_2025.tif"
    }
    
    data = {}
    for name, path in files.items():
        if os.path.exists(path):
            arr, _ = load_geotiff(path)
            if arr is not None:
                data[name] = arr
    
    if data:
        st.subheader("Area Coverage Comparison")
        
        areas = {}
        for name, arr in data.items():
            mining_pixels = np.sum(arr == 1)
            area_ha = calculate_area(arr)
            areas[name] = {
                'pixels': mining_pixels,
                'hectares': area_ha,
                'percentage': (mining_pixels / arr.size) * 100
            }
        
        # Table
        import pandas as pd
        df = pd.DataFrame(areas).T
        df.columns = ['Mining Pixels', 'Area (hectares)', 'Coverage (%)']
        df['Mining Pixels'] = df['Mining Pixels'].apply(lambda x: f"{int(x):,}")
        df['Area (hectares)'] = df['Area (hectares)'].apply(lambda x: f"{x:.1f}")
        df['Coverage (%)'] = df['Coverage (%)'].apply(lambda x: f"{x:.2f}")
        st.dataframe(df, use_container_width=True)
        
        # Bar chart
        st.subheader("Visual Comparison")
        fig, ax = plt.subplots(figsize=(10, 5))
        names = list(areas.keys())
        hectares = [areas[n]['hectares'] for n in names]
        colors = ['#4CAF50', '#2196F3', '#FF9800']
        bars = ax.bar(names, hectares, color=colors)
        ax.set_ylabel('Area (hectares)', fontsize=12)
        ax.set_title('Mining Area Comparison', fontsize=14, fontweight='bold')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f} ha',
                   ha='center', va='bottom', fontsize=10)
        st.pyplot(fig)

# ====================
# PAGE: INTERACTIVE COMPARISON
# ====================
elif page == "🔍 Interactive Comparison":
    st.header("🔍 Interactive Comparison")
    
    st.write("Compare different views side-by-side")
    
    col1, col2 = st.columns(2)
    
    with col1:
        view1 = st.selectbox("Left View", [
            "Ground Truth",
            "Prediction 2016",
            "Prediction 2025",
            "Change Map"
        ], key="view1")
    
    with col2:
        view2 = st.selectbox("Right View", [
            "Prediction 2016",
            "Prediction 2025",
            "Change Map",
            "Ground Truth"
        ], key="view2")
    
    # Map selections to files
    view_map = {
        "Ground Truth": f"{RESULTS_DIR}/chingola_multiclass_mask.tif",
        "Prediction 2016": f"{RESULTS_DIR}/prediction_2016.tif",
        "Prediction 2025": f"{RESULTS_DIR}/prediction_2025.tif",
        "Change Map": f"{RESULTS_DIR}/change_map.tif"
    }
    
    col1, col2 = st.columns(2)
    
    for col, view, title in [(col1, view1, "Left"), (col2, view2, "Right")]:
        with col:
            st.subheader(view)
            path = view_map[view]
            if os.path.exists(path):
                arr, _ = load_geotiff(path)
                if arr is not None:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    
                    if "Change" in view:
                        # Reconstruct actual change
                        pred_2016, _ = load_geotiff(f"{RESULTS_DIR}/prediction_2016.tif")
                        pred_2025, _ = load_geotiff(f"{RESULTS_DIR}/prediction_2025.tif")
                        if pred_2016 is not None and pred_2025 is not None:
                            actual_change = pred_2025.astype(int) - pred_2016.astype(int)
                            cmap = plt.cm.colors.ListedColormap(['#FF4B4B', '#E0E0E0', '#4CAF50'])
                            bounds = [-1.5, -0.5, 0.5, 1.5]
                            norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)
                            im = ax.imshow(actual_change, cmap=cmap, norm=norm)
                            cbar = plt.colorbar(im, ax=ax)
                            cbar.set_ticks([-1, 0, 1])
                            cbar.set_ticklabels(['Removed', 'Unchanged', 'New'])
                    else:
                        cmap = plt.cm.colors.ListedColormap(['#87CEEB', '#FF4B4B'])
                        im = ax.imshow(arr, cmap=cmap)
                        cbar = plt.colorbar(im, ax=ax)
                        cbar.set_ticks([0.25, 0.75])
                        cbar.set_ticklabels(['Background', 'Mining'])
                    
                    ax.set_title(view, fontweight='bold')
                    ax.axis('off')
                    st.pyplot(fig)
            else:
                st.warning(f"File not found: {view}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Mining Detection System</strong> | Powered by U-Net Deep Learning</p>
    <p>Final Year Project - Land Cover Classification for Mining Detection</p>
</div>
""", unsafe_allow_html=True)
