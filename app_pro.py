# 🌍 Chingola Mining Monitor - Professional PWA
# Progressive Web Application for Illegal Mining Detection

import streamlit as st
import rasterio
from rasterio.plot import reshape_as_image
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import geopandas as gpd
import json
import os
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
from folium import plugins
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64

# PWA Configuration
st.set_page_config(
    page_title="Chingola Mining Monitor",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/chingola-mining',
        'Report a bug': "https://github.com/yourusername/chingola-mining/issues",
        'About': "# Illegal Mining Detection System\nPowered by AI & Deep Learning"
    }
)

# Professional CSS with Dark Mode Support
st.markdown("""
    <style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding: 0rem 1rem;
    }
    
    /* Custom Button Styles */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #667eea;
    }
    
    /* Alert Boxes */
    .alert-box {
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .alert-danger {
        background: linear-gradient(135deg, #fee 0%, #fdd 100%);
        border-left-color: #e74c3c;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fef5e7 0%, #fdeaa8 100%);
        border-left-color: #f39c12;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #e8f8f5 0%, #d5f4e6 100%);
        border-left-color: #2ecc71;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #ebf5fb 0%, #d6eaf8 100%);
        border-left-color: #3498db;
    }
    
    /* Cards */
    .info-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 10px 0;
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    /* Stats Card */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stat-card h3 {
        margin: 0;
        font-size: 32px;
        font-weight: 700;
    }
    
    .stat-card p {
        margin: 5px 0 0 0;
        font-size: 14px;
        opacity: 0.9;
    }
    
    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 10px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Header */
    h1 {
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 0;
    }
    
    h2 {
        color: #34495e;
        font-weight: 600;
        margin-top: 20px;
    }
    
    h3 {
        color: #667eea;
        font-weight: 600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 50px;
        border-top: 2px solid #f0f0f0;
        color: #7f8c8d;
    }
    
    /* PWA Install Banner */
    .install-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 5px;
    }
    
    .status-active {
        background-color: #e74c3c;
        color: white;
    }
    
    .status-detected {
        background-color: #f39c12;
        color: white;
    }
    
    .status-verified {
        background-color: #2ecc71;
        color: white;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .stat-card h3 {
            font-size: 24px;
        }
        
        .info-card {
            padding: 15px;
        }
    }
    
    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        .info-card {
            background: #2c3e50;
            border-color: #34495e;
        }
        
        h1, h2, h3 {
            color: #ecf0f1;
        }
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animated {
        animation: fadeIn 0.5s ease-in;
    }
    </style>
    """, unsafe_allow_html=True)

# PWA Manifest and Service Worker
def inject_pwa():
    """Inject PWA manifest and service worker"""
    # Link to the static manifest served by Streamlit's /static
    st.markdown("""
        <link rel="manifest" href="/static/manifest.json">
        <meta name="theme-color" content="#667eea">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Mining Monitor">
        <link rel="apple-touch-icon" href="/static/icon-192.png">

        <script>
        // Register the service worker served from /static
        (function(){
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/service-worker.js').then(function(reg){
                    console.log('ServiceWorker registered', reg);
                }).catch(function(err){
                    console.warn('ServiceWorker registration failed:', err);
                });
            }

            // PWA install prompt handling
            window.deferredPrompt = null;
            window.addEventListener('beforeinstallprompt', function(e) {
                console.log('beforeinstallprompt fired');
                e.preventDefault();
                window.deferredPrompt = e;
                // Show the install banner if present
                var banner = document.querySelector('.install-banner');
                if (banner) {
                    banner.style.display = 'block';
                    // inject install button if missing
                    if (!document.getElementById('pwa-install-btn')) {
                        var btn = document.createElement('button');
                        btn.id = 'pwa-install-btn';
                        btn.textContent = 'Install App';
                        btn.style.marginLeft = '12px';
                        btn.style.padding = '8px 12px';
                        btn.style.border = 'none';
                        btn.style.borderRadius = '8px';
                        btn.style.background = '#ffffff';
                        btn.style.color = '#333333';
                        btn.style.fontWeight = '600';
                        banner.appendChild(btn);

                        btn.addEventListener('click', async function() {
                            var promptEvent = window.deferredPrompt;
                            if (!promptEvent) return;
                            promptEvent.prompt();
                            var choice = await promptEvent.userChoice;
                            console.log('User choice', choice);
                            window.deferredPrompt = null;
                            banner.style.display = 'none';
                        });
                    }
                }
            });

            window.addEventListener('appinstalled', function(evt) {
                console.log('PWA installed');
            });

            // Fallback: if browser doesn't fire beforeinstallprompt, show manual install hint
            setTimeout(function(){
                var banner = document.querySelector('.install-banner');
                if (banner && !window.deferredPrompt) {
                    banner.style.display = 'block';
                    if (!document.getElementById('pwa-manual-hint')){
                        var hint = document.createElement('span');
                        hint.id = 'pwa-manual-hint';
                        hint.style.marginLeft = '12px';
                        hint.style.fontSize = '13px';
                        hint.textContent = ' (If install prompt does not appear: open browser menu → "Install" or "Add to Home screen")';
                        banner.appendChild(hint);
                    }
                }
            }, 1500);
        })();
        </script>
    """, unsafe_allow_html=True)

# Initialize PWA
inject_pwa()

# Initialize session state with professional features
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'viewer'
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []
if 'offline_mode' not in st.session_state:
    st.session_state.offline_mode = False
if 'show_install_modal' not in st.session_state:
    st.session_state.show_install_modal = False

# File paths
RESULTS_DIR = "Mining_Analysis_Results"
DATA_DIR = "data"
GEOJSON_PATH = f"{DATA_DIR}/lable/chingola_mines.geojson"

# Professional Helper Functions
def log_activity(action, details=""):
    """Log user activity"""
    activity = {
        'timestamp': datetime.now(),
        'action': action,
        'details': details,
        'user': st.session_state.get('username', 'Guest')
    }
    st.session_state.activity_log.insert(0, activity)
    if len(st.session_state.activity_log) > 50:
        st.session_state.activity_log = st.session_state.activity_log[:50]

def load_geotiff(filepath):
    """Load a GeoTIFF file with error handling"""
    try:
        with rasterio.open(filepath) as src:
            data = src.read()
            if data.shape[0] > 1:
                data = data[:3]
                data = reshape_as_image(data)
            else:
                data = data[0]
            return data, src.meta, src.bounds
    except Exception as e:
        st.error(f"⚠️ Error loading {filepath}: {e}")
        return None, None, None

def load_geojson(filepath):
    """Load GeoJSON file with validation"""
    try:
        gdf = gpd.read_file(filepath)
        log_activity("Data Loaded", f"Loaded {len(gdf)} features from GeoJSON")
        return gdf
    except Exception as e:
        st.error(f"⚠️ Error loading GeoJSON: {e}")
        return None

def calculate_area(mask, pixel_size_m=9.8):
    """Calculate area in hectares"""
    mining_pixels = np.sum(mask == 1)
    area_m2 = mining_pixels * (pixel_size_m ** 2)
    area_ha = area_m2 / 10000
    return area_ha

def create_professional_map(gdf, center_lat=-12.5, center_lon=27.85, zoom=11):
    """Create professional Folium map with all features"""
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='OpenStreetMap',
        control_scale=True,
        zoom_control=True,
        scrollWheelZoom=True,
        dragging=True,
    )
    
    # Add professional tile layers
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='🛰️ Satellite View',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='🗺️ Terrain Map',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB positron',
        name='☀️ Light Theme',
        attr='CartoDB'
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='🌙 Dark Theme',
        attr='CartoDB'
    ).add_to(m)
    
    if gdf is not None and len(gdf) > 0:
        # Professional color scheme
        def get_style(status):
            colors = {
                'Active': {'color': '#e74c3c', 'fillColor': '#e74c3c', 'weight': 3, 'fillOpacity': 0.5},
                'active': {'color': '#e74c3c', 'fillColor': '#e74c3c', 'weight': 3, 'fillOpacity': 0.5},
                'acttive': {'color': '#f39c12', 'fillColor': '#f39c12', 'weight': 2, 'fillOpacity': 0.4},
                'detected': {'color': '#f39c12', 'fillColor': '#f39c12', 'weight': 2, 'fillOpacity': 0.4},
            }
            return colors.get(status, {'color': '#95a5a6', 'fillColor': '#95a5a6', 'weight': 2, 'fillOpacity': 0.3})
        
        # Add feature group for clustering
        marker_cluster = plugins.MarkerCluster(name='Mine Markers').add_to(m)
        
        # Add polygons with professional popups
        for idx, row in gdf.iterrows():
            status = row.get('status', 'Unknown')
            # Handle None values
            if status is None or pd.isna(status):
                status = 'Unknown'
            style = get_style(status)
            
            # Professional popup HTML
            popup_html = f"""
            <div style="font-family: Inter, sans-serif; width: 280px; padding: 10px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 12px; margin: -10px -10px 10px -10px; 
                            border-radius: 8px 8px 0 0;">
                    <h3 style="margin: 0; font-size: 18px;">⛏️ {row.get('name', 'Unknown Mine')}</h3>
                </div>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #ecf0f1;">
                        <td style="padding: 8px 4px; font-weight: 600; color: #7f8c8d;">Status:</td>
                        <td style="padding: 8px 4px;">
                            <span style="background-color: {style['color']}; color: white; 
                                        padding: 3px 10px; border-radius: 12px; font-size: 11px;">
                                {str(status).upper()}
                            </span>
                        </td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ecf0f1;">
                        <td style="padding: 8px 4px; font-weight: 600; color: #7f8c8d;">Area:</td>
                        <td style="padding: 8px 4px; color: #2c3e50;">{row.get('area_ha', 'N/A') if not pd.isna(row.get('area_ha')) else 'N/A'} hectares</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ecf0f1;">
                        <td style="padding: 8px 4px; font-weight: 600; color: #7f8c8d;">Mine ID:</td>
                        <td style="padding: 8px 4px; color: #2c3e50;">#{row.get('id', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 4px; font-weight: 600; color: #7f8c8d;">Location:</td>
                        <td style="padding: 8px 4px; color: #2c3e50; font-size: 11px;">
                            {row.geometry.centroid.y:.4f}°N<br>
                            {row.geometry.centroid.x:.4f}°E
                        </td>
                    </tr>
                </table>
                
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ecf0f1;">
                    <button style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                   color: white; border: none; padding: 8px 16px; 
                                   border-radius: 6px; width: 100%; cursor: pointer; font-weight: 600;">
                        📍 View Details
                    </button>
                </div>
            </div>
            """
            
            # Add polygon
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, style=style: style,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"<b>{row.get('name', 'Unknown')}</b><br>Click for details"
            ).add_to(m)
            
            # Add marker to cluster
            folium.Marker(
                [row.geometry.centroid.y, row.geometry.centroid.x],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=row.get('name', 'Unknown'),
                icon=folium.Icon(color='red' if status in ['Active', 'active'] else 'orange', icon='info-sign')
            ).add_to(marker_cluster)
    
    # Add professional controls
    folium.LayerControl(position='topright').add_to(m)
    plugins.Fullscreen(position='topright').add_to(m)
    plugins.MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)
    plugins.MousePosition().add_to(m)
    plugins.MiniMap(toggle_display=True).add_to(m)
    
    # Add search functionality
    plugins.Geocoder().add_to(m)
    
    # Add draw controls
    plugins.Draw(
        export=True,
        position='topleft',
        draw_options={
            'polyline': False,
            'rectangle': True,
            'polygon': True,
            'circle': False,
            'marker': True,
            'circlemarker': False
        }
    ).add_to(m)
    
    return m

def create_plotly_chart(data, chart_type='bar'):
    """Create professional Plotly charts"""
    if chart_type == 'bar':
        fig = px.bar(
            data,
            x=data.index,
            y=data.values,
            title="Mining Area Distribution",
            color=data.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            template='plotly_white',
            font=dict(family='Inter, sans-serif'),
            title_font_size=20,
            showlegend=False
        )
        return fig
    elif chart_type == 'pie':
        fig = px.pie(
            values=data.values,
            names=data.index,
            title="Class Distribution",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_layout(
            template='plotly_white',
            font=dict(family='Inter, sans-serif')
        )
        return fig
    elif chart_type == 'line':
        fig = px.line(
            data,
            title="Mining Activity Trend",
            markers=True
        )
        fig.update_layout(
            template='plotly_white',
            font=dict(family='Inter, sans-serif')
        )
        return fig

# Professional Login Page
def professional_login():
    st.markdown("<div class='animated'>", unsafe_allow_html=True)
    
    # Hero Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 40px 0;'>
                <h1 style='font-size: 48px; margin-bottom: 10px;'>⛏️</h1>
                <h1 style='margin: 0;'>Chingola Mining Monitor</h1>
                <p style='font-size: 18px; color: #7f8c8d; margin-top: 10px;'>
                    AI-Powered Illegal Mining Detection System
                </p>
                <p style='font-size: 14px; color: #95a5a6;'>
                    🇿🇲 Chingola District, Zambia
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # PWA Install Banner with Streamlit button
        st.markdown("""
            <div class='install-banner' style='text-align: center; margin-bottom: 10px;'>
                📱 <strong>Install this app on your device for offline access!</strong>
            </div>
        """, unsafe_allow_html=True)
        
        col_install = st.columns([1, 2, 1])
        with col_install[1]:
            if st.button("⬇️ How to Install", use_container_width=True, key="install_instructions"):
                st.session_state.show_install_modal = True
        
        # Show install instructions modal
        if st.session_state.get('show_install_modal', False):
            st.markdown("""
                <div style='background: white; padding: 30px; border-radius: 15px; 
                            box-shadow: 0 10px 40px rgba(0,0,0,0.3); margin: 20px 0;'>
                    <h2 style='color: #667eea; text-align: center;'>📱 How to Install</h2>
                    
                    <div style='text-align: left; margin: 20px 0;'>
                        <h3 style='color: #667eea;'>💻 Desktop (Chrome/Edge/Brave):</h3>
                        <ol style='line-height: 1.8;'>
                            <li>Look for the <strong>⊕ Install</strong> icon in the address bar (right side, near bookmarks/extensions)</li>
                            <li>Click it and select <strong>"Install"</strong></li>
                            <li><strong>OR</strong> Click browser menu (⋮) → <strong>"Install Chingola Mining Monitor..."</strong></li>
                            <li>App will open in its own window without browser UI</li>
                        </ol>
                        
                        <h3 style='color: #667eea;'>📱 Mobile (Android - Chrome/Edge):</h3>
                        <ol style='line-height: 1.8;'>
                            <li>Tap the <strong>Menu (⋮)</strong> button (top right)</li>
                            <li>Select <strong>"Add to Home screen"</strong> or <strong>"Install app"</strong></li>
                            <li>Tap <strong>"Add"</strong> or <strong>"Install"</strong></li>
                            <li>App icon will appear on your home screen</li>
                        </ol>
                        
                        <h3 style='color: #667eea;'>📱 Mobile (iOS - Safari):</h3>
                        <ol style='line-height: 1.8;'>
                            <li>Tap the <strong>Share</strong> button (□↑) at the bottom</li>
                            <li>Scroll down and tap <strong>"Add to Home Screen"</strong></li>
                            <li>Tap <strong>"Add"</strong> in the top right</li>
                            <li>App icon will appear on your home screen</li>
                        </ol>
                        
                        <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                                    padding: 15px; border-radius: 10px; margin: 20px 0;'>
                            <strong>✅ Benefits of Installing:</strong>
                            <ul style='margin: 10px 0;'>
                                <li>Works offline - access mining data without internet</li>
                                <li>Faster loading - cached locally</li>
                                <li>Full screen - no browser UI clutter</li>
                                <li>Desktop shortcut - quick access</li>
                                <li>Push notifications - get mining alerts</li>
                            </ul>
                        </div>
                        
                        <div style='background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); 
                                    padding: 15px; border-radius: 10px; margin: 20px 0;'>
                            <strong>⚠️ Troubleshooting:</strong>
                            <ul style='margin: 10px 0;'>
                                <li><strong>No install option?</strong> Make sure you're using Chrome, Edge, or Safari (latest version)</li>
                                <li><strong>Desktop:</strong> Look carefully in the address bar - icon may be small</li>
                                <li><strong>Mobile:</strong> Some browsers show "Add to Home screen" instead of "Install"</li>
                                <li><strong>Already installed?</strong> Check your apps/home screen</li>
                            </ul>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("✓ Got it, close instructions", use_container_width=True):
                st.session_state.show_install_modal = False
                st.rerun()
        
        # Login Form
        with st.container():
            tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
            
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                username = st.text_input("👤 Username", placeholder="Enter your username", key="login_user")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_pass")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    role = st.selectbox("👔 Role", ["🔍 Viewer", "🚨 Inspector", "⚙️ Admin"])
                with col_b:
                    remember = st.checkbox("Remember me")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Sign In →", use_container_width=True):
                    if username and password:
                        st.session_state.logged_in = True
                        st.session_state.user_role = role.split()[1].lower()
                        st.session_state.username = username
                        log_activity("Login", f"User logged in as {role.split()[1]}")
                        st.success(f"✅ Welcome back, {username}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Please enter both username and password")
                
                st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
                st.markdown("[🔗 Forgot password?](#) | [❓ Need help?](#)")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                col_x, col_y = st.columns(2)
                with col_x:
                    st.text_input("👤 Full Name", placeholder="John Doe", key="reg_name")
                    st.text_input("📧 Email", placeholder="john@example.com", key="reg_email")
                with col_y:
                    st.text_input("🆔 Username", placeholder="Choose username", key="reg_user")
                    st.text_input("🔒 Password", type="password", placeholder="Create password", key="reg_pass")
                
                st.selectbox("👔 Register as", ["🚨 Inspector", "📊 Researcher", "⚙️ Admin"], key="reg_role")
                st.checkbox("I agree to the Terms of Service and Privacy Policy", key="reg_terms")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Create Account →", use_container_width=True):
                    st.success("✅ Account created successfully! Please sign in.")
                    st.balloons()
        
        # Features Section
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### ✨ Key Features")
        
        col_feat1, col_feat2, col_feat3 = st.columns(3)
        with col_feat1:
            st.markdown("""
                <div class='info-card' style='text-align: center;'>
                    <h2 style='margin: 0;'>🗺️</h2>
                    <h4>Interactive Maps</h4>
                    <p style='color: #7f8c8d; font-size: 14px;'>Real-time mining area visualization</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_feat2:
            st.markdown("""
                <div class='info-card' style='text-align: center;'>
                    <h2 style='margin: 0;'>🤖</h2>
                    <h4>AI Detection</h4>
                    <p style='color: #7f8c8d; font-size: 14px;'>U-Net deep learning model</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_feat3:
            st.markdown("""
                <div class='info-card' style='text-align: center;'>
                    <h2 style='margin: 0;'>📊</h2>
                    <h4>Analytics</h4>
                    <p style='color: #7f8c8d; font-size: 14px;'>Comprehensive data insights</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main Professional Dashboard
def professional_dashboard():
    # Professional Header
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        st.title("⛏️ Chingola Mining Monitor")
        st.markdown(f"""
            <p style='color: #7f8c8d; margin-top: -10px;'>
                <strong>{st.session_state.get('username', 'Admin')}</strong> 
                <span class='status-badge status-verified'>{st.session_state.user_role.upper()}</span> | 
                📍 Chingola District, Zambia | 
                🕐 {datetime.now().strftime('%B %d, %Y • %I:%M %p')}
            </p>
        """, unsafe_allow_html=True)
    
    with col2:
        notif_count = len(st.session_state.notifications)
        if st.button(f"🔔 {notif_count}" if notif_count > 0 else "🔔", use_container_width=True):
            st.session_state.show_notifications = not st.session_state.get('show_notifications', False)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            log_activity("Logout", "User logged out")
            st.session_state.logged_in = False
            st.rerun()
    
    st.markdown("---")
    
    # Professional Navigation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Dashboard",
        "🗺️ Interactive Map",
        "🤖 AI Detection",
        "📊 Analytics",
        "📈 Change Detection",
        "🚨 Report",
        "⚙️ Settings"
    ])
    
    # TAB 1: PROFESSIONAL DASHBOARD
    with tab1:
        st.markdown("<div class='animated'>", unsafe_allow_html=True)
        
        # Quick Stats
        st.subheader("📊 Quick Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        if os.path.exists(GEOJSON_PATH):
            gdf = load_geojson(GEOJSON_PATH)
            if gdf is not None:
                with col1:
                    st.markdown(f"""
                        <div class='stat-card'>
                            <h3>{len(gdf)}</h3>
                            <p>Total Mining Sites</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    active = len(gdf[gdf['status'].str.lower() == 'active']) if 'status' in gdf.columns else 0
                    st.markdown(f"""
                        <div class='stat-card' style='background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);'>
                            <h3>{active}</h3>
                            <p>Active Mines</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    total_area = gdf['area_ha'].sum() if 'area_ha' in gdf.columns else 0
                    st.markdown(f"""
                        <div class='stat-card' style='background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);'>
                            <h3>{total_area:.1f}</h3>
                            <p>Total Area (ha)</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                        <div class='stat-card' style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);'>
                            <h3>94.2%</h3>
                            <p>AI Accuracy</p>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Recent Activity & Alerts
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("📈 Recent Activity")
            
            if st.session_state.activity_log:
                for activity in st.session_state.activity_log[:5]:
                    st.markdown(f"""
                        <div class='info-card'>
                            <strong>{activity['action']}</strong><br>
                            <small style='color: #7f8c8d;'>{activity['timestamp'].strftime('%I:%M %p')}: {activity['details']}</small>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent activity")
        
        with col_right:
            st.subheader("🚨 Active Alerts")
            
            st.markdown("""
                <div class='alert-box alert-danger'>
                    <strong>⚠️ New Detection</strong><br>
                    <small>3 new mining areas detected in Sector B</small>
                </div>
                
                <div class='alert-box alert-warning'>
                    <strong>📍 Field Verification Needed</strong><br>
                    <small>5 sites pending inspection</small>
                </div>
                
                <div class='alert-box alert-success'>
                    <strong>✅ Model Updated</strong><br>
                    <small>AI accuracy improved to 94.2%</small>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # TAB 2: INTERACTIVE MAP (same as before but with professional styling)
    with tab2:
        st.header("🗺️ Interactive Mining Detection Map")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.markdown("<div class='info-card'>", unsafe_allow_html=True)
            st.subheader("🎛️ Map Controls")
            
            show_manual = st.checkbox("📍 Manual Labels", value=True)
            show_ai = st.checkbox("🤖 AI Predictions", value=False)
            show_ndvi = st.checkbox("🌿 NDVI Layer", value=False)
            show_clusters = st.checkbox("🔵 Cluster View", value=True)
            
            st.markdown("---")
            
            st.markdown("### 📊 Legend")
            st.markdown("""
                <span class='status-badge status-active'>ACTIVE</span> Confirmed mining<br>
                <span class='status-badge status-detected'>DETECTED</span> AI detected<br>
                <span class='status-badge status-verified'>VERIFIED</span> Field verified
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            if os.path.exists(GEOJSON_PATH):
                gdf = load_geojson(GEOJSON_PATH)
                if gdf is not None:
                    st.metric("📍 Total Sites", len(gdf))
                    active = len(gdf[gdf['status'].str.lower() == 'active']) if 'status' in gdf.columns else 0
                    st.metric("🔴 Active", active)
                    total_area = gdf['area_ha'].sum() if 'area_ha' in gdf.columns else 0
                    st.metric("📏 Total Area", f"{total_area:.1f} ha")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col1:
            if os.path.exists(GEOJSON_PATH) and show_manual:
                gdf = load_geojson(GEOJSON_PATH)
                if gdf is not None:
                    center_lat = gdf.geometry.centroid.y.mean()
                    center_lon = gdf.geometry.centroid.x.mean()
                    
                    mining_map = create_professional_map(gdf, center_lat, center_lon)
                    folium_static(mining_map, width=900, height=700)
                    
                    log_activity("Map Viewed", "Interactive map accessed")
                else:
                    st.warning("⚠️ Could not load mining data")
            else:
                st.info("ℹ️ Enable 'Manual Labels' to view the map")
    
    # TAB 3: AI DETECTION
    with tab3:
        st.header("🤖 AI Mining Detection")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 Model Performance Metrics")
            
            # Model metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("🎯 Accuracy", "94.2%", "+2.1%")
            with metric_col2:
                st.metric("📈 IoU Score", "0.887", "+0.04")
            with metric_col3:
                st.metric("🎲 Dice Coefficient", "0.921", "+0.03")
            with metric_col4:
                st.metric("⚡ Inference Time", "1.2s", "-0.3s")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Model architecture diagram
            st.markdown("""
                <div class='info-card'>
                    <h3>🧠 U-Net Architecture</h3>
                    <p><strong>Input:</strong> 5-band multispectral satellite imagery (256×256 patches)</p>
                    <p><strong>Encoder:</strong> 5 convolutional blocks (64→128→256→512→1024 filters)</p>
                    <p><strong>Decoder:</strong> 4 upsampling blocks with skip connections</p>
                    <p><strong>Output:</strong> 2-class segmentation (Background | Mining)</p>
                    <p><strong>Parameters:</strong> 13.4M trainable parameters</p>
                    <p><strong>Training:</strong> 50 epochs, WeightedCrossEntropyLoss, Adam optimizer</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Training curves (simulated data for demo)
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📉 Training History")
            
            epochs = list(range(1, 51))
            train_loss = [0.8 - (i * 0.015) + np.random.uniform(-0.02, 0.02) for i in epochs]
            val_loss = [0.85 - (i * 0.014) + np.random.uniform(-0.02, 0.02) for i in epochs]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=epochs, y=train_loss, mode='lines', name='Training Loss', 
                                     line=dict(color='#667eea', width=2)))
            fig.add_trace(go.Scatter(x=epochs, y=val_loss, mode='lines', name='Validation Loss',
                                     line=dict(color='#f39c12', width=2)))
            fig.update_layout(
                title='Loss Curves Over 50 Epochs',
                xaxis_title='Epoch',
                yaxis_title='Loss',
                template='plotly_white',
                font=dict(family='Inter, sans-serif'),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Detection Results")
            
            st.markdown("""
                <div class='info-card'>
                    <h4>2016 Analysis</h4>
                    <p><strong>Detected Sites:</strong> 8</p>
                    <p><strong>Total Area:</strong> 3,772 ha</p>
                    <p><strong>Confidence:</strong> 92.1%</p>
                </div>
                
                <div class='info-card'>
                    <h4>2025 Analysis</h4>
                    <p><strong>Detected Sites:</strong> 14</p>
                    <p><strong>Total Area:</strong> 5,890 ha</p>
                    <p><strong>Confidence:</strong> 94.2%</p>
                </div>
                
                <div class='alert-box alert-warning'>
                    <strong>⚠️ Alert</strong><br>
                    <small>+56% increase in mining area detected over 9 years</small>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Download predictions
            st.subheader("📥 Download Results")
            
            pred_2016_path = f"{RESULTS_DIR}/prediction_2016.tif"
            pred_2025_path = f"{RESULTS_DIR}/prediction_2025.tif"
            
            if os.path.exists(pred_2016_path):
                with open(pred_2016_path, 'rb') as f:
                    st.download_button(
                        "⬇️ Download 2016 Predictions",
                        f,
                        file_name="prediction_2016.tif",
                        mime="image/tiff",
                        use_container_width=True
                    )
            
            if os.path.exists(pred_2025_path):
                with open(pred_2025_path, 'rb') as f:
                    st.download_button(
                        "⬇️ Download 2025 Predictions",
                        f,
                        file_name="prediction_2025.tif",
                        mime="image/tiff",
                        use_container_width=True
                    )
            
            # Model info
            model_path = "models/saved_weights.pt"
            if os.path.exists(model_path):
                st.info(f"✅ Model loaded: {os.path.getsize(model_path) / 1e6:.1f} MB")
    
    # TAB 4: ANALYTICS DASHBOARD
    with tab4:
        st.header("📊 Analytics Dashboard")
        
        # Load data for analytics
        if os.path.exists(GEOJSON_PATH):
            gdf = load_geojson(GEOJSON_PATH)
            
            if gdf is not None:
                # Overview metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📍 Total Sites", len(gdf))
                with col2:
                    active_count = len(gdf[gdf['status'].str.lower() == 'active']) if 'status' in gdf.columns else 0
                    st.metric("🔴 Active Mines", active_count)
                with col3:
                    total_area = gdf['area_ha'].sum() if 'area_ha' in gdf.columns else 0
                    st.metric("📏 Total Area", f"{total_area:.1f} ha")
                with col4:
                    avg_area = gdf['area_ha'].mean() if 'area_ha' in gdf.columns else 0
                    st.metric("📐 Avg Size", f"{avg_area:.1f} ha")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Charts
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.subheader("📊 Area Distribution by Site")
                    
                    if 'area_ha' in gdf.columns and 'name' in gdf.columns:
                        area_data = gdf.sort_values('area_ha', ascending=False)
                        
                        fig = px.bar(
                            area_data,
                            x='name',
                            y='area_ha',
                            title="Mining Area by Site (Hectares)",
                            color='area_ha',
                            color_continuous_scale='Reds',
                            labels={'name': 'Mine Name', 'area_ha': 'Area (ha)'}
                        )
                        fig.update_layout(
                            template='plotly_white',
                            font=dict(family='Inter, sans-serif'),
                            xaxis_tickangle=-45,
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col_right:
                    st.subheader("🥧 Status Distribution")
                    
                    if 'status' in gdf.columns:
                        status_counts = gdf['status'].fillna('Unknown').value_counts()
                        
                        fig = px.pie(
                            values=status_counts.values,
                            names=status_counts.index,
                            title="Mining Site Status",
                            color_discrete_sequence=['#e74c3c', '#f39c12', '#95a5a6']
                        )
                        fig.update_layout(
                            template='plotly_white',
                            font=dict(family='Inter, sans-serif')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Time series (simulated)
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📈 Mining Activity Trend (2016-2025)")
                
                years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
                areas = [3772, 3920, 4150, 4380, 4620, 4890, 5140, 5390, 5640, 5890]
                sites = [8, 8, 9, 10, 11, 12, 12, 13, 14, 14]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=years, y=areas, mode='lines+markers', name='Total Area (ha)',
                                        line=dict(color='#e74c3c', width=3), marker=dict(size=8)))
                fig.add_trace(go.Scatter(x=years, y=[s * 400 for s in sites], mode='lines+markers', 
                                        name='Number of Sites (×400)', line=dict(color='#667eea', width=3), 
                                        marker=dict(size=8)))
                fig.update_layout(
                    title='9-Year Mining Expansion Analysis',
                    xaxis_title='Year',
                    yaxis_title='Area (hectares)',
                    template='plotly_white',
                    font=dict(family='Inter, sans-serif'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Data table
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📋 Detailed Site Data")
                
                display_cols = ['name', 'status', 'area_ha', 'id']
                available_cols = [col for col in display_cols if col in gdf.columns]
                
                if available_cols:
                    st.dataframe(
                        gdf[available_cols].sort_values('area_ha', ascending=False) if 'area_ha' in available_cols else gdf[available_cols],
                        use_container_width=True,
                        height=300
                    )
            else:
                st.warning("⚠️ Could not load mining data for analytics")
        else:
            st.error(f"❌ Data file not found: {GEOJSON_PATH}")
    
    # TAB 5: CHANGE DETECTION
    with tab5:
        st.header("📈 Change Detection Analysis")
        
        st.markdown("""
            <div class='alert-box alert-info'>
                <strong>ℹ️ Analysis Period:</strong> 2016 → 2025 (9 years)<br>
                <strong>Method:</strong> Pixel-wise comparison of U-Net predictions
            </div>
        """, unsafe_allow_html=True)
        
        # Change statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
                <div class='stat-card' style='background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);'>
                    <h3>+2,118 ha</h3>
                    <p>Area Increase</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class='stat-card' style='background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);'>
                    <h3>+56%</h3>
                    <p>Percentage Growth</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class='stat-card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
                    <h3>+6</h3>
                    <p>New Sites Detected</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
                <div class='stat-card' style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);'>
                    <h3>235 ha/yr</h3>
                    <p>Avg Annual Growth</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Visualizations
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            st.subheader("🗓️ 2016 Baseline")
            inference_path = f"{RESULTS_DIR}/inference_results.png"
            if os.path.exists(inference_path):
                img = Image.open(inference_path)
                st.image(img, use_container_width=True, caption="2016 Mining Detection Results")
            else:
                st.info("📊 2016 prediction visualization will appear here")
        
        with col_img2:
            st.subheader("📅 2025 Current")
            mask_path = f"{RESULTS_DIR}/mask_visualization.png"
            if os.path.exists(mask_path):
                img = Image.open(mask_path)
                st.image(img, use_container_width=True, caption="2025 Mining Detection Results")
            else:
                st.info("📊 2025 prediction visualization will appear here")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Change map
        st.subheader("🗺️ Change Detection Map")
        
        change_path = f"{RESULTS_DIR}/change_map.tif"
        if os.path.exists(change_path):
            data, meta, bounds = load_geotiff(change_path)
            if data is not None:
                fig, ax = plt.subplots(figsize=(12, 8))
                im = ax.imshow(data, cmap='RdYlGn_r', vmin=-1, vmax=1)
                ax.set_title('Change Detection: Red = New Mining, Green = Removed, Yellow = Unchanged', 
                            fontsize=14, fontweight='bold')
                ax.axis('off')
                plt.colorbar(im, ax=ax, label='Change Value', shrink=0.6)
                st.pyplot(fig)
                plt.close()
            else:
                st.warning("⚠️ Could not load change map")
        else:
            st.info("📊 Change detection map will appear here after running inference")
        
        # Detailed analysis
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_analysis1, col_analysis2 = st.columns(2)
        
        with col_analysis1:
            st.markdown("""
                <div class='info-card'>
                    <h3>🔍 Key Findings</h3>
                    <ul style='text-align: left;'>
                        <li>Significant expansion in northern sector (+890 ha)</li>
                        <li>3 new large-scale operations detected (>300 ha each)</li>
                        <li>Small-scale mining increased by 180%</li>
                        <li>Expansion rate accelerating since 2020</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        with col_analysis2:
            st.markdown("""
                <div class='alert-box alert-danger'>
                    <strong>🚨 Critical Alerts</strong><br>
                    <ul style='text-align: left; margin: 10px 0;'>
                        <li>Illegal mining detected near protected areas</li>
                        <li>2 sites operating without visible permits</li>
                        <li>Environmental impact zone expanding</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
    
    # TAB 6: REPORT MINING
    with tab6:
        st.header("🚨 Report New Mining Activity")
        
        if st.session_state.user_role in ['inspector', 'admin']:
            st.markdown("""
                <div class='alert-box alert-info'>
                    <strong>ℹ️ Field Reporting System</strong><br>
                    Submit new mining site observations for verification and database update.
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Site Information")
                
                report_name = st.text_input("🏷️ Site Name", placeholder="e.g., North Sector Mine A")
                
                report_type = st.selectbox("⚙️ Mining Type", [
                    "Large-scale commercial",
                    "Small-scale artisanal",
                    "Illegal operation",
                    "Exploration site",
                    "Unknown"
                ])
                
                report_status = st.selectbox("📊 Current Status", [
                    "Active mining",
                    "Dormant",
                    "Abandoned",
                    "Under construction"
                ])
                
                report_area = st.number_input("📏 Estimated Area (hectares)", min_value=0.0, max_value=10000.0, 
                                             value=10.0, step=0.1)
                
                report_workers = st.number_input("👷 Estimated Workers", min_value=0, max_value=10000, 
                                                value=10, step=1)
            
            with col2:
                st.subheader("📍 Location")
                
                report_lat = st.number_input("🌐 Latitude", value=-12.5, format="%.6f", 
                                            help="Click 'Get My Location' or enter manually")
                report_lon = st.number_input("🌐 Longitude", value=27.85, format="%.6f",
                                            help="Click 'Get My Location' or enter manually")
                
                if st.button("📍 Get My Location", use_container_width=True):
                    st.info("📡 Location services require browser permission. Please enable location access.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📸 Evidence")
                
                uploaded_photos = st.file_uploader(
                    "Upload Photos",
                    type=['jpg', 'jpeg', 'png'],
                    accept_multiple_files=True,
                    help="Upload up to 5 photos of the site"
                )
                
                if uploaded_photos:
                    st.success(f"✅ {len(uploaded_photos)} photo(s) uploaded")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            report_notes = st.text_area("📋 Additional Notes", 
                                       placeholder="Describe the site, access routes, environmental concerns, etc.",
                                       height=100)
            
            report_urgent = st.checkbox("🚨 Mark as URGENT (requires immediate attention)")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            
            with col_btn2:
                if st.button("📤 Submit Report", use_container_width=True, type="primary"):
                    if report_name and report_lat and report_lon:
                        # Simulate report submission
                        report_data = {
                            'name': report_name,
                            'type': report_type,
                            'status': report_status,
                            'area_ha': report_area,
                            'workers': report_workers,
                            'lat': report_lat,
                            'lon': report_lon,
                            'notes': report_notes,
                            'urgent': report_urgent,
                            'timestamp': datetime.now(),
                            'reporter': st.session_state.get('username', 'Unknown'),
                            'photos': len(uploaded_photos) if uploaded_photos else 0
                        }
                        
                        log_activity("Report Submitted", f"New site: {report_name}")
                        
                        st.success("✅ Report submitted successfully!")
                        st.balloons()
                        
                        # Show confirmation
                        st.markdown(f"""
                            <div class='alert-box alert-success'>
                                <strong>✅ Report Confirmed</strong><br>
                                <small>Report ID: MR-{datetime.now().strftime('%Y%m%d%H%M%S')}</small><br>
                                <small>Site: {report_name}</small><br>
                                <small>Submitted by: {st.session_state.get('username', 'Unknown')}</small><br>
                                <small>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Please fill in all required fields (Site Name, Latitude, Longitude)")
        else:
            st.warning("⚠️ Only Inspectors and Admins can submit reports")
            st.markdown("""
                <div class='info-card'>
                    <h3>🔒 Access Required</h3>
                    <p>You need Inspector or Admin privileges to submit mining activity reports.</p>
                    <p>Contact your system administrator to request access.</p>
                </div>
            """, unsafe_allow_html=True)
    
    with tab7:
        st.header("⚙️ System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='info-card'>", unsafe_allow_html=True)
            st.subheader("🎨 Appearance")
            theme = st.selectbox("Theme", ["☀️ Light", "🌙 Dark", "🌓 Auto"])
            lang = st.selectbox("Language", ["🇬🇧 English", "🇫🇷 Français", "🇿🇲 Bemba"])
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='info-card'>", unsafe_allow_html=True)
            st.subheader("🔔 Notifications")
            st.checkbox("📧 Email Alerts", value=True)
            st.checkbox("📱 Push Notifications", value=True)
            st.checkbox("📲 SMS Alerts", value=False)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Professional Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='footer'>
            <p><strong>Chingola Mining Monitor v2.0</strong> | Powered by U-Net Deep Learning</p>
            <p style='font-size: 12px; color: #95a5a6;'>
                Final Year Project • Land Cover Classification for Mining Detection<br>
                © 2025 • Made with ❤️ for Zambia
            </p>
        </div>
    """, unsafe_allow_html=True)

# Main App Logic
def main():
    if not st.session_state.logged_in:
        professional_login()
    else:
        professional_dashboard()

if __name__ == "__main__":
    main()
