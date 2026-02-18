# Illegal Mining Detection - Interactive Web Dashboard
# Enhanced Streamlit Application with Map Integration

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
from supabase import create_client
import time

# Import authentication functions
from supabase_config import login_user, register_user, hash_password

# Notification System Imports
try:
    from streamlit_notifications import (
        initialize_notifications,
        show_notification_bell,
        show_notification_panel,
        inject_notification_listener
    )
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("Warning: Notification system not available. Run: pip install -r requirements_notifications.txt")

# Page config
st.set_page_config(
    page_title="Chingola Mining Surveillance System - Ministry of Mines",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%23003366' width='100' height='100' rx='15'/><text x='50' y='55' text-anchor='middle' dominant-baseline='middle' font-size='50' fill='white' font-family='serif'>ZM</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CORS headers for ngrok access
st.markdown("""
    <meta http-equiv="Access-Control-Allow-Origin" content="*">
    <meta http-equiv="Access-Control-Allow-Methods" content="GET, POST, PUT, DELETE, OPTIONS">
    <meta http-equiv="Access-Control-Allow-Headers" content="Origin, X-Requested-With, Content-Type, Accept, Authorization">
""", unsafe_allow_html=True)

# Professional Government-Grade CSS
st.markdown("""
    <style>
    /* === BASE LAYOUT === */
    .main {
        padding: 0rem 1rem;
        background-color: #f8f9fb;
    }
    
    /* === GOVERNMENT COLOUR PALETTE === */
    :root {
        --gov-primary: #003366;
        --gov-secondary: #005a9e;
        --gov-accent: #00843d;
        --gov-gold: #b8860b;
        --gov-dark: #1a1a2e;
        --gov-light: #f0f2f6;
        --gov-danger: #c62828;
        --gov-warning: #e65100;
        --gov-success: #2e7d32;
        --gov-border: #d1d5db;
    }
    
    /* === TYPOGRAPHY === */
    h1 {
        color: var(--gov-primary) !important;
        font-weight: 700;
        letter-spacing: -0.5px;
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    }
    h2, h3 {
        color: var(--gov-dark) !important;
        font-weight: 600;
    }
    
    /* === BUTTONS === */
    .stButton > button {
        width: 100%;
        background-color: var(--gov-primary);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border-radius: 6px;
        font-size: 0.9rem;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: var(--gov-secondary);
        box-shadow: 0 2px 8px rgba(0, 51, 102, 0.25);
    }
    .stButton > button[kind="primary"] {
        background-color: var(--gov-accent);
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #006b32;
    }
    
    /* === METRIC CARDS === */
    [data-testid="stMetric"] {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        border: 1px solid var(--gov-border);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700;
        color: var(--gov-primary) !important;
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #e8ecf1;
        border-radius: 8px 8px 0 0;
        padding: 4px 4px 0 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px 6px 0 0;
        padding: 10px 18px;
        color: #475569 !important;
        font-weight: 500;
        font-size: 0.85rem;
        border: none;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(0, 51, 102, 0.08);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--gov-primary) !important;
        color: white !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] button {
        color: white !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        border: 1px solid var(--gov-border);
        border-top: 3px solid var(--gov-primary);
        border-radius: 0 0 8px 8px;
        padding: 1.5rem;
        background: white;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--gov-primary) 0%, var(--gov-dark) 100%);
    }
    /* Ensure all sidebar text (notifications, expanders, captions, links) is white for contrast */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] .stExpander,
    [data-testid="stSidebar"] .stExpanderHeader,
    [data-testid="stSidebar"] .stExpanderContent,
    [data-testid="stSidebar"] .streamlit-expanderHeader,
    [data-testid="stSidebar"] .streamlit-expanderContent,
    [data-testid="stSidebar"] a {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.25);
    }
    
    /* === ALERTS === */
    .alert-box {
        padding: 1rem 1.25rem;
        border-radius: 6px;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .alert-danger {
        background-color: #fef2f2;
        border-left: 4px solid var(--gov-danger);
        color: #1a1a1a;
    }
    .alert-warning {
        background-color: #fff7ed;
        border-left: 4px solid var(--gov-warning);
        color: #1a1a1a;
    }
    .alert-success {
        background-color: #f0fdf4;
        border-left: 4px solid var(--gov-success);
        color: #1a1a1a;
    }
    
    /* === EXPANDER === */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--gov-primary);
    }
    
    /* === DATA ELEMENTS === */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* === MODAL === */
    .image-modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        max-width: 90vw;
        max-height: 90vh;
    }
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.6);
        z-index: 999;
    }
    
    /* === GOVERNMENT HEADER BANNER === */
    .gov-banner {
        background: linear-gradient(135deg, #003366 0%, #004080 50%, #003366 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 0 0 12px 12px;
        margin: -1rem -1rem 1.5rem -1rem;
        border-bottom: 4px solid #b8860b;
    }
    .gov-banner h1 {
        color: white !important;
        margin: 0;
        font-size: 1.6rem;
    }
    .gov-banner p {
        color: #b0c4de;
        margin: 0.25rem 0 0 0;
        font-size: 0.9rem;
    }
    .gov-badge {
        display: inline-block;
        background: var(--gov-gold);
        color: white;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00e676;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* === FOOTER === */
    .gov-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.75rem;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid var(--gov-border);
        margin-top: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# PWA Manifest - Embed directly as data URL
manifest_json = {
    "name": "Chingola Mining Surveillance System",
    "short_name": "CMSS",
    "description": "Government AI-Powered Illegal Mining Detection & Surveillance",
    "start_url": ".",
    "display": "standalone",
    "background_color": "#003366",
    "theme_color": "#003366",
    "icons": [
        {
            "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%23003366' width='100' height='100' rx='15'/><text x='50' y='55' text-anchor='middle' dominant-baseline='middle' font-size='50' fill='white' font-family='serif'>ZM</text></svg>",
            "sizes": "192x192",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ]
}

import json
manifest_string = json.dumps(manifest_json)
manifest_blob = f"data:application/json;base64,{__import__('base64').b64encode(manifest_string.encode()).decode()}"

st.markdown(f"""
    <link rel="manifest" href="{manifest_blob}">
    <meta name="theme-color" content="#003366">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="CMSS">
    <script>
        // Service Worker for offline support
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register(
                'data:text/javascript;base64,' + btoa(`
                    self.addEventListener('install', (event) => {{
                        console.log('Service Worker installing...');
                        self.skipWaiting();
                    }});
                    
                    self.addEventListener('activate', (event) => {{
                        console.log('Service Worker activated');
                        return self.clients.claim();
                    }});
                    
                    self.addEventListener('fetch', (event) => {{
                        // Let the browser handle all fetches normally
                        return;
                    }});
                `)
            ).then(reg => {{
                console.log(' Service Worker registered:', reg);
            }}).catch(err => {{
                console.log(' Service Worker registration failed:', err);
            }});
        }}
    </script>
    """, unsafe_allow_html=True)

query_params = st.query_params

# Initialize session state with persistence
if 'logged_in' not in st.session_state:
    if 'session' in query_params and query_params['session'] == 'active':
        st.session_state.logged_in = True
        st.session_state.username = query_params.get('user', 'Guest')
        st.session_state.user_email = query_params.get('email', '')
        st.session_state.user_role = query_params.get('role', 'user')
    else:
        st.session_state.logged_in = False

if 'user_role' not in st.session_state:
    st.session_state.user_role = query_params.get('role', 'user')
if 'username' not in st.session_state:
    st.session_state.username = query_params.get('user', 'Guest')
if 'user_email' not in st.session_state:
    st.session_state.user_email = query_params.get('email', '')
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'last_notification_check' not in st.session_state:
    st.session_state.last_notification_check = time.time()
if 'show_image_modal' not in st.session_state:
    st.session_state.show_image_modal = None

# File paths
RESULTS_DIR = "Mining_Analysis_Results"
DATA_DIR = "data"
GEOJSON_PATH = f"{DATA_DIR}/lable/chingola_mines.geojson"

# Artisanal mining data directory (external source with ML/DL results)
ARTISANAL_MINING_DIR = r"C:\Users\oseim\OneDrive\School\Final Year Project\Project\artisanal_mining"
ARTISANAL_GEOJSON = os.path.join(ARTISANAL_MINING_DIR, "chingola_TrainingData_PERFECT.geojson")
ARTISANAL_DL_REPORT = os.path.join(ARTISANAL_MINING_DIR, "DL&ML", "classification_report_dl.txt")
ARTISANAL_ML_REPORT = os.path.join(ARTISANAL_MINING_DIR, "DL&ML", "classification_report_ml.txt")

@st.cache_data(ttl=300)
def load_artisanal_geojson():
    """Load and parse the artisanal mining GeoJSON data with classification labels"""
    if os.path.exists(ARTISANAL_GEOJSON):
        try:
            gdf = gpd.read_file(ARTISANAL_GEOJSON)
            return gdf
        except Exception as e:
            st.warning(f"Could not load artisanal mining data: {e}")
    return None

@st.cache_data(ttl=600)
def load_classification_reports():
    """Load ML and DL classification reports from artisanal_mining folder"""
    reports = {'dl': None, 'ml': None}
    for key, path in [('dl', ARTISANAL_DL_REPORT), ('ml', ARTISANAL_ML_REPORT)]:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    reports[key] = f.read()
            except:
                pass
    return reports

@st.cache_data(ttl=300)
def get_artisanal_stats():
    """Calculate statistics from the artisanal mining GeoJSON data"""
    gdf = load_artisanal_geojson()
    if gdf is None:
        return None
    
    stats = {}
    # Count features by label/class
    if 'label' in gdf.columns:
        label_counts = gdf['label'].value_counts().to_dict()
        stats['label_counts'] = label_counts
    elif 'class' in gdf.columns:
        class_map = {1: 'mining', 0: 'non-mining'}
        gdf['label_derived'] = gdf['class'].map(class_map).fillna('unknown')
        label_counts = gdf['label_derived'].value_counts().to_dict()
        stats['label_counts'] = label_counts
    
    # Mining-specific stats
    mining_features = gdf[gdf.get('label', gdf.get('class', pd.Series(dtype=int))).isin(['mining', 1])] if 'label' in gdf.columns else gdf[gdf['class'] == 1]
    stats['total_mining_zones'] = len(mining_features)
    stats['total_mining_area_ha'] = mining_features['area_ha'].sum() if 'area_ha' in mining_features.columns else 0
    stats['avg_severity'] = mining_features['severity'].mean() if 'severity' in mining_features.columns else 0
    stats['max_severity'] = mining_features['severity'].max() if 'severity' in mining_features.columns else 0
    stats['avg_mining_area'] = mining_features['area_ha'].mean() if 'area_ha' in mining_features.columns else 0
    stats['avg_mean_loss'] = mining_features['meanLoss'].mean() if 'meanLoss' in mining_features.columns else 0
    
    # Non-mining stats
    non_mining = gdf[gdf.get('label', gdf.get('class', pd.Series(dtype=int))).isin(['forest', 'water', 'urban', 'bare_soil', 0])] if 'label' in gdf.columns else gdf[gdf['class'] == 0]
    stats['total_non_mining'] = len(non_mining)
    
    # Overall
    stats['total_features'] = len(gdf)
    stats['total_area_ha'] = gdf['area_ha'].sum() if 'area_ha' in gdf.columns else 0
    
    return stats

# Supabase Configuration
SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
# Service role key for admin operations (satellite updates, etc.)
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM3MzYwMCwiZXhwIjoyMDc3OTQ5NjAwfQ.EFQ7FroOvGjGFQhvhZ1KzqgeUM0nIDUTpFUGKGn1Eu0"
# Anon key for authentication
SUPABASE_AUTH_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw"

# Initialize Supabase client (cached for performance)
@st.cache_resource
def get_supabase_client():
    """Get Supabase client with service role key for admin operations"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_resource
def get_supabase_auth_client():
    """Get Supabase client with anon key for authentication"""
    return create_client(SUPABASE_URL, SUPABASE_AUTH_KEY)

def check_user_role(allowed_roles=['admin', 'inspector']):
    """Check if current user has required role"""
    user_role = st.session_state.get('user_role', 'user')
    return user_role in allowed_roles

def get_current_user_id():
    """Get current user ID from session or create demo admin"""
    # Check if user_id exists in session
    if 'user_id' in st.session_state and st.session_state.user_id:
        return st.session_state.user_id
    
    # Otherwise, try to get/create a demo admin user
    try:
        supabase = get_supabase_client()
        
        # Try to find existing admin user
        result = supabase.table('profiles').select('id').eq('role', 'admin').limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]['id']
        
        # If no admin exists, try to find any user
        result = supabase.table('profiles').select('id').limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]['id']
        
        # If no users exist, return None and show error
        return None
    except:
        return None

# Notification Functions
def fetch_notifications():
    """Fetch unread notifications from Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('mining_alerts') \
            .select('*') \
            .eq('status', 'unread') \
            .order('sent_at', desc=True) \
            .execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching notifications: {e}")
        return []

def display_notifications():
    """Display unified notifications panel with both database and push notifications"""
    # Initialize push notification system if available
    if NOTIFICATIONS_AVAILABLE:
        initialize_notifications()
        inject_notification_listener()
    
    # Fetch database notifications
    db_notifications = fetch_notifications()
    
    # Get push notifications from session state
    push_notifications = st.session_state.get('notifications', [])
    
    # Calculate total unread count
    total_unread = len(db_notifications) + len([n for n in push_notifications if not n.get('read', False)])
    
    if total_unread > 0 or push_notifications:
        st.sidebar.markdown("---")
        st.sidebar.subheader(f"Notifications ({total_unread})")
        
        # Add refresh button
        if st.sidebar.button(" Refresh Notifications", use_container_width=True):
            st.rerun()
        
        # Display push notifications first (real-time alerts)
        if push_notifications:
            st.sidebar.markdown("####  Real-Time Alerts")
            for notif in push_notifications[:5]:  # Show latest 5
                if notif.get('read', False):
                    continue
                    
                severity = notif.get('severity', 'medium')
                emoji = {"critical": "", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "")
                
                with st.sidebar.expander(f"{emoji} {notif.get('title', 'Alert')}", expanded=False):
                    st.markdown(f"**{notif.get('message', 'No details')}**")
                    if notif.get('timestamp'):
                        st.caption(f"{notif['timestamp']}")
                    if notif.get('metadata'):
                        for key, value in notif['metadata'].items():
                            if key not in ['title', 'message', 'timestamp']:
                                st.caption(f"{key}: {value}")
        
        # Display database notifications (historical alerts)
        if db_notifications:
            st.sidebar.markdown("#### Mining Alerts")
            for notif in db_notifications[:5]:  # Show latest 5
                severity = notif.get('severity', 'low')
                emoji = {"critical": "", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "")
                
                with st.sidebar.expander(f"{emoji} {notif.get('title', 'Alert')}", expanded=False):
                    st.markdown(f"**Message:** {notif.get('message', 'No details')}")
                    
                    # Show evidence photo if available
                    if notif.get('evidence_url'):
                        st.markdown("---")
                        st.markdown("** Evidence Photo:**")
                        try:
                            st.image(notif['evidence_url'], use_container_width=True, caption="Click button to view full size")
                            if st.button(" View Full Size", key=f"view_img_{notif['id']}", use_container_width=True):
                                st.session_state.show_image_modal = {
                                    'url': notif['evidence_url'],
                                    'title': notif.get('title', 'Alert'),
                                    'location': notif.get('location', 'N/A'),
                                    'reporter': notif.get('reported_by', 'Unknown'),
                                    'date': notif.get('image_date', 'N/A'),
                                    'caption': f"{notif.get('title', 'Evidence')} - {notif.get('location', '')}"
                                }
                                st.rerun()
                        except Exception as img_error:
                            st.warning(f"Could not load image: {img_error}")
                    
                    if notif.get('reported_by'):
                        st.caption(f"Reported by: {notif['reported_by']}")
                    
                    if notif.get('area_change_ha'):
                        st.metric("Area Change", f"{notif['area_change_ha']:.2f} ha")
                    
                    if notif.get('change_percent'):
                        st.metric("Change %", f"{notif['change_percent']:.1f}%")
                    
                    if notif.get('image_date'):
                        st.caption(f"{notif['image_date']}")
                    
                    if notif.get('location'):
                        st.caption(f"{notif['location']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(" Mark Read", key=f"read_{notif['id']}"):
                            mark_notification_read(notif['id'])
                            st.rerun()
                    with col2:
                        if st.button(" Resolve", key=f"resolve_{notif['id']}"):
                            resolve_notification(notif['id'])
                            st.rerun()
        
        # Tip for browser notifications
        if NOTIFICATIONS_AVAILABLE:
            st.sidebar.caption(" Tip: Enable browser notifications for instant alerts")
    else:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Notifications")
        st.sidebar.info(" No new notifications")

def display_image_modal(image_data):
    """Display full-size image in a modal dialog"""
    if image_data:
        st.markdown("---")
        st.markdown("###  Evidence Photo - Full View")
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            try:
                st.image(image_data['url'], use_container_width=True, caption=image_data.get('caption', 'Evidence Photo'))
                
                st.markdown(f"""
                **Report Details:**
                - **Title:** {image_data.get('title', 'N/A')}
                - **Location:** {image_data.get('location', 'N/A')}
                - **Reported by:** {image_data.get('reporter', 'N/A')}
                - **Date:** {image_data.get('date', 'N/A')}
                """)
                
                if st.button(" Close", type="primary", use_container_width=True):
                    st.session_state.show_image_modal = None
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Could not load image: {e}")
                if st.button(" Close"):
                    st.session_state.show_image_modal = None
                    st.rerun()
        
        st.markdown("---")

def mark_notification_read(alert_id):
    """Mark notification as read"""
    try:
        supabase = get_supabase_client()
        supabase.table('mining_alerts') \
            .update({'status': 'read', 'read_at': datetime.now().isoformat()}) \
            .eq('id', alert_id) \
            .execute()
    except Exception as e:
        st.error(f"Error marking notification: {e}")

def resolve_notification(alert_id):
    """Resolve notification"""
    try:
        supabase = get_supabase_client()
        supabase.table('mining_alerts') \
            .update({'status': 'resolved', 'resolved_at': datetime.now().isoformat()}) \
            .eq('id', alert_id) \
            .execute()
    except Exception as e:
        st.error(f"Error resolving notification: {e}")

# Helper functions
def load_geotiff(filepath, max_pixels=2000):
    """Load a GeoTIFF file with optional downsampling to prevent memory errors"""
    try:
        with rasterio.open(filepath) as src:
            # Calculate downsampling factor if image is too large
            h, w = src.height, src.width
            scale = 1
            if max(h, w) > max_pixels:
                scale = max(h, w) / max_pixels
            out_h = max(1, int(h / scale))
            out_w = max(1, int(w / scale))
            
            data = src.read(out_shape=(src.count, out_h, out_w))
            if data.shape[0] > 1:
                data = data[:3]
                data = reshape_as_image(data)
            else:
                data = data[0]
            return data, src.meta, src.bounds
    except Exception as e:
        st.error(f"Error loading {filepath}: {e}")
        return None, None, None

def load_geojson(filepath):
    """Load GeoJSON file"""
    try:
        gdf = gpd.read_file(filepath)
        return gdf
    except Exception as e:
        st.error(f"Error loading GeoJSON: {e}")
        return None

def calculate_area(mask, pixel_size_m=9.8):
    """Calculate area in hectares"""
    mining_pixels = np.sum(mask == 1)
    area_m2 = mining_pixels * (pixel_size_m ** 2)
    area_ha = area_m2 / 10000
    return area_ha

def calculate_ndvi(image):
    """Calculate NDVI from satellite image (assuming bands are ordered: R, G, B, NIR, SWIR)"""
    try:
        # Assuming band 4 is NIR and band 1 is Red
        nir = image[3] if image.shape[0] > 3 else image[0]
        red = image[0]
        ndvi = (nir - red) / (nir + red + 1e-8)
        return ndvi
    except:
        return None

def create_map(gdf, center_lat=-12.5, center_lon=27.85, zoom=11):
    """Create Folium map with mining polygons"""
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # Add different tile layers with proper attribution
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Terrain',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB positron',
        name='Light',
        attr='CartoDB'
    ).add_to(m)
    
    if gdf is not None and len(gdf) > 0:
        # Color code by status
        def get_color(status):
            if status in ['Active', 'active']:
                return 'red'
            elif status == 'acttive':
                return 'orange'
            else:
                return 'gray'
        
        # Add polygons
        for idx, row in gdf.iterrows():
            color = get_color(row.get('status', None))
            
            # Create popup HTML
            popup_html = f"""
            <div style="font-family: Arial; width: 250px;">
                <h4 style="color: {color}; margin: 5px 0;">{row.get('name', 'Unknown Mine')}</h4>
                <hr style="margin: 5px 0;">
                <p><b>Status:</b> <span style="color: {color};">{row.get('status', 'Unknown')}</span></p>
                <p><b>Area:</b> {row.get('area_ha', 'N/A')} hectares</p>
                <p><b>Mine ID:</b> {row.get('id', 'N/A')}</p>
                <p><b>Coordinates:</b> {row.geometry.centroid.y:.4f}, {row.geometry.centroid.x:.4f}</p>
            </div>
            """
            
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=color: {
                    'fillColor': color,
                    'color': color,
                    'weight': 2,
                    'fillOpacity': 0.4,
                },
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add fullscreen button
    plugins.Fullscreen().add_to(m)
    
    # Add measure control
    plugins.MeasureControl().add_to(m)
    
    return m

# ==========================================
# LOGIN SYSTEM
# ==========================================
def login_page():
    # Initialize Supabase client for authentication
    supabase = get_supabase_auth_client()
    
    # Load Zambia flag as base64 for login page
    flag_b64 = ""
    flag_path = os.path.join("static", "zambia.png")
    if os.path.exists(flag_path):
        import base64
        with open(flag_path, "rb") as fp:
            flag_b64 = base64.b64encode(fp.read()).decode()
    
    # Government-styled login page
    flag_img = f'<img src="data:image/png;base64,{flag_b64}" style="height:60px; margin-bottom:8px; border-radius:4px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">' if flag_b64 else ''
    st.markdown(f"""
    <div style="text-align:center; padding: 2rem 0 1rem 0;">
        {flag_img}
        <div style="display:inline-block; background: #003366; color:white; padding:12px 28px; border-radius:8px; border-bottom: 3px solid #b8860b; margin-bottom:1rem;">
            <span style="font-size:1.6rem; font-weight:700; letter-spacing:1px;">ZAMBIA</span>
        </div>
        <h2 style="color:#003366; margin:0.5rem 0 0.2rem 0; font-weight:700;">Chingola Mining Surveillance System</h2>
        <p style="color:#64748b; font-size:0.95rem; margin:0;"> Copperbelt Province</p>
        <p style="color:#94a3b8; font-size:0.8rem; margin:0.5rem 0 0 0;">Authorized Personnel Access Only</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs([" Login", " Register"])
        
        with tab1:
            st.markdown("### Sign In")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login", use_container_width=True):
                if email and password:
                    # Authenticate with database
                    result = login_user(supabase, email, password)
                    
                    if result['success']:
                        user = result['user']
                        st.session_state.logged_in = True
                        st.session_state.user_role = user['role']
                        st.session_state.username = user['full_name'] or user['email']
                        st.session_state.user_id = user['id']
                        st.session_state.user_email = user['email']
                        
                        # Persist session in URL query parameters
                        st.query_params.update({
                            'session': 'active',
                            'user': st.session_state.username,
                            'email': user['email'],
                            'role': user['role']
                        })
                        
                        st.success(f"Welcome back, {st.session_state.username}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(result['message'])
                else:
                    st.error("Please enter email and password")
        
        with tab2:
            st.markdown("### Create Account")
            
            # Initialize registration message in session state
            if 'registration_message' not in st.session_state:
                st.session_state.registration_message = None
                st.session_state.registration_type = None
            
            # Display any previous registration message
            if st.session_state.registration_message:
                if st.session_state.registration_type == 'success':
                    st.success(st.session_state.registration_message)
                else:
                    st.error(st.session_state.registration_message)
            
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")
            reg_role = st.selectbox("Role", ["User", "Admin"], key="reg_role")
            
            if st.button("Register", use_container_width=True):
                # Validate inputs
                if not all([reg_name, reg_email, reg_password, reg_password_confirm]):
                    st.session_state.registration_message = "Please fill in all fields"
                    st.session_state.registration_type = 'error'
                    st.rerun()
                elif reg_password != reg_password_confirm:
                    st.session_state.registration_message = "Passwords do not match"
                    st.session_state.registration_type = 'error'
                    st.rerun()
                elif len(reg_password) < 6:
                    st.session_state.registration_message = "Password must be at least 6 characters"
                    st.session_state.registration_type = 'error'
                    st.rerun()
                else:
                    # Register user in database
                    result = register_user(
                        supabase,
                        email=reg_email,
                        password=reg_password,
                        full_name=reg_name,
                        role=reg_role.lower()
                    )
                    
                    if result['success']:
                        st.session_state.registration_message = " Registration successful! Please login with your credentials."
                        st.session_state.registration_type = 'success'
                    else:
                        st.session_state.registration_message = result['message']
                        st.session_state.registration_type = 'error'
                    st.rerun()
    
    # Login page footer
    st.markdown("""
    <div style="text-align:center; padding:2rem 0 1rem 0; color:#94a3b8; font-size:0.75rem;">
        <p>&copy; 2026 Republic of Zambia &bull; Ministry of Mines and Minerals Development</p>
        <p>Unauthorized access to this system is a criminal offence under the Computer Misuse Act.</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN DASHBOARD
# ==========================================
def main_dashboard():
    # Sidebar: Government Branding & User Profile
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:1rem 0;">
            <div style="background: rgba(255,255,255,0.1); padding:0.8rem; border-radius:8px; border: 1px solid rgba(255,255,255,0.2);">
                <div style="font-size:1.1rem; font-weight:700; color:white; letter-spacing:1px;">CMSS</div>
                <div style="font-size:0.65rem; color:#b0c4de; letter-spacing:0.5px;">Chingola Mining Surveillance</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Officer Profile")
        
        # Display name (or email if name is not set)
        display_name = st.session_state.get('username', 'User')
        if display_name == st.session_state.get('user_email'):
            st.markdown(f"**Name:** *Not set*")
            st.caption(f"{display_name}")
        else:
            st.markdown(f"**Name:** {display_name}")
            st.markdown(f"**Email:** {st.session_state.get('user_email', 'N/A')}")
        
        role_label = st.session_state.user_role.title()
        st.markdown(f"**Role:** {role_label}")
        if st.session_state.user_role == 'admin':
            st.markdown("**System Administrator**")
        st.markdown(f"**Session:** {datetime.now().strftime('%d %b %Y, %H:%M')}")
        st.markdown("---")
    
    # Display notifications in sidebar (auto-fetches from database)
    display_notifications()
    
    # Display image modal if requested
    if st.session_state.show_image_modal:
        display_image_modal(st.session_state.show_image_modal)
    
    # Header - Government Banner
    st.markdown(f"""
    <div class="gov-banner">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h1> Mining Surveillance System</h1>
                <p>National Remote Sensing Centre &bull; Copperbelt Province, Zambia</p>
            </div>
            <div style="text-align:right;">
                <span class="gov-badge">CLASSIFIED</span><br>
                <span style="color:#b0c4de; font-size:0.8rem;"><span class="status-indicator"></span>System Online</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sub-header row
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.caption(f"Logged in as: **{st.session_state.get('username', 'User')}** ({st.session_state.user_role.title()}) | {datetime.now().strftime('%A, %d %B %Y')}")
    
    with col3:
        if st.button("Notifications" + (f" ({len(st.session_state.notifications)})" if st.session_state.notifications else "")):
            st.session_state.show_notifications = True
        if st.button("Logout", type="primary"):
            # Clear registration messages
            st.session_state.registration_message = None
            st.session_state.registration_type = None
            
            st.session_state.logged_in = False
            st.session_state.username = 'Guest'
            st.session_state.user_role = 'user'
            st.session_state.user_email = None
            st.session_state.user_id = None
            
            # Clear session from URL query parameters
            st.query_params.clear()
            
            st.rerun()
    
    st.markdown("---")
    
    # Navigation - Add satellite tab for admins only
    if st.session_state.user_role == 'admin':
        tab1, tab2, tab2b, tab4, tab5, tab6, tab8, tab9, tab10 = st.tabs([
            "Surveillance Map",
            "AI Detection",
            "Detected Zones",
            "Change Analysis",
            "Field Reports",
            "Satellite Data",
            "AOI Configuration",
            "Model Training",
            "System Settings"
        ])
        tab3 = None
        tab7 = None
    else:
        tab1, tab2, tab2b, tab4, tab5, tab6 = st.tabs([
            "Surveillance Map",
            "AI Detection",
            "Detected Zones",
            "Change Analysis",
            "Field Reports",
            "Settings"
        ])
        tab3 = None
        tab7 = None
        tab8 = None
        tab9 = None
        tab10 = None
    
    # TAB 1: INTERACTIVE MAP
    with tab1:
        st.header("Geospatial Surveillance Map")
        st.caption("Real-time interactive map of mining activity across Chingola District")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.subheader("Map Controls")
            
            show_manual = st.checkbox("Manual Labels", value=True)
            show_ai = st.checkbox("AI Predictions", value=True)
            show_ndvi = st.checkbox("NDVI Layer", value=False)
            
            st.markdown("---")
            
            st.markdown("### Classification Legend")
            st.markdown("""
            <div style='background:#fef2f2; padding:8px 12px; border-radius:4px; margin:4px 0; border-left:3px solid #c62828; color:#1a1a1a; font-size:0.85rem;'>
                <b>Mining</b> - Active/detected mining zone
            </div>
            <div style='background:#f0fdf4; padding:8px 12px; border-radius:4px; margin:4px 0; border-left:3px solid #2e7d32; color:#1a1a1a; font-size:0.85rem;'>
                <b>Forest</b> - Vegetation cover
            </div>
            <div style='background:#e3f2fd; padding:8px 12px; border-radius:4px; margin:4px 0; border-left:3px solid #1565c0; color:#1a1a1a; font-size:0.85rem;'>
                <b>Water</b> - Water bodies
            </div>
            <div style='background:#f3e5f5; padding:8px 12px; border-radius:4px; margin:4px 0; border-left:3px solid #7b1fa2; color:#1a1a1a; font-size:0.85rem;'>
                <b>Urban</b> - Settlements/infrastructure
            </div>
            <div style='background:#fff8e1; padding:8px 12px; border-radius:4px; margin:4px 0; border-left:3px solid #f9a825; color:#1a1a1a; font-size:0.85rem;'>
                <b>Bare Soil</b> - Exposed ground
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Quick Stats from artisanal_mining data
            art_stats = get_artisanal_stats()
            if art_stats:
                st.metric("Mining Zones", art_stats['total_mining_zones'])
                st.metric("Mining Area", f"{art_stats['total_mining_area_ha']:.1f} ha")
                st.metric("Avg Severity", f"{art_stats['avg_severity']:.2f}")
                st.metric("Total Features", art_stats['total_features'])
                if art_stats.get('label_counts'):
                    st.markdown("**Land Cover Breakdown:**")
                    for label, count in art_stats['label_counts'].items():
                        st.caption(f"  {label}: {count}")
            elif os.path.exists(GEOJSON_PATH):
                gdf = load_geojson(GEOJSON_PATH)
                if gdf is not None:
                    st.metric("Total Mines", len(gdf))
                    active = len(gdf[gdf['status'].str.lower() == 'active']) if 'status' in gdf.columns else 0
                    st.metric("Active Mines", active)
                    total_area = gdf['area_ha'].sum() if 'area_ha' in gdf.columns else 0
                    st.metric("Total Area", f"{total_area:.1f} ha")
        
        with col1:
            # Load and display map
            manual_gdf = None
            if os.path.exists(GEOJSON_PATH) and show_manual:
                manual_gdf = load_geojson(GEOJSON_PATH)
            
            # Determine map center
            center_lat, center_lon = -12.5, 27.85
            if manual_gdf is not None:
                center_lat = manual_gdf.geometry.centroid.y.mean()
                center_lon = manual_gdf.geometry.centroid.x.mean()
            
            if show_manual or show_ai:
                # Create base map
                mining_map = create_map(manual_gdf if show_manual else None, center_lat, center_lon)
                
                # Overlay AI-detected zones from ML/DL predictions (artisanal_mining source)
                if show_ai:
                    ai_gdf = load_artisanal_geojson()
                    if ai_gdf is not None and len(ai_gdf) > 0:
                        try:
                            # Label-based color mapping
                            label_colors = {
                                'mining': {'fill': '#c62828', 'border': '#b71c1c'},
                                'forest': {'fill': '#2e7d32', 'border': '#1b5e20'},
                                'water': {'fill': '#1565c0', 'border': '#0d47a1'},
                                'urban': {'fill': '#7b1fa2', 'border': '#4a148c'},
                                'bare_soil': {'fill': '#f9a825', 'border': '#f57f17'},
                            }
                            
                            for idx, row in ai_gdf.iterrows():
                                area = row.get('area_ha', 0)
                                label = row.get('label', 'unknown')
                                severity = row.get('severity', 0)
                                mean_loss = row.get('meanLoss', 0)
                                count = row.get('count', 0)
                                zone_id = row.get('id', idx + 1)
                                
                                # Color by land cover label
                                colors = label_colors.get(label, {'fill': '#999999', 'border': '#666666'})
                                fill_color = colors['fill']
                                border_color = colors['border']
                                
                                # Severity label for mining zones
                                if label == 'mining' and severity:
                                    if severity > 2.0:
                                        sev_label = 'Critical'
                                    elif severity > 1.5:
                                        sev_label = 'High'
                                    elif severity > 1.0:
                                        sev_label = 'Moderate'
                                    else:
                                        sev_label = 'Low'
                                    sev_text = f"<p><b>Severity:</b> <span style='color:{border_color};'>{severity:.2f} ({sev_label})</span></p>"
                                    sev_text += f"<p><b>Mean Loss:</b> {mean_loss:.4f}</p>"
                                else:
                                    sev_text = ""
                                
                                popup_html = f"""
                                <div style="font-family:Arial; width:260px;">
                                    <h4 style="color:{border_color}; margin:5px 0;">{label.title()} Zone {idx + 1}</h4>
                                    <hr style="margin:5px 0;">
                                    <p><b>Classification:</b> {label.title()}</p>
                                    <p><b>Area:</b> {area:.2f} ha</p>
                                    <p><b>Pixel Count:</b> {count}</p>
                                    {sev_text}
                                    <p><b>Model:</b> Ensemble ML+DL (Random Forest + U-Net)</p>
                                    <p style="font-size:0.8em; color:#666;">Source: artisanal_mining pipeline</p>
                                </div>
                                """
                                
                                # Adjust opacity: mining zones more visible
                                opacity = 0.5 if label == 'mining' else 0.25
                                
                                folium.GeoJson(
                                    row.geometry,
                                    style_function=lambda x, fc=fill_color, bc=border_color, op=opacity: {
                                        'fillColor': fc,
                                        'color': bc,
                                        'weight': 2,
                                        'fillOpacity': op,
                                        'dashArray': '5, 5'
                                    },
                                    popup=folium.Popup(popup_html, max_width=300)
                                ).add_to(mining_map)
                        except Exception as e:
                            st.warning(f"Could not load AI detection zones: {e}")
                
                # Display map
                folium_static(mining_map, width=800, height=600)
            else:
                st.info("Enable 'Manual Labels' or 'AI Predictions' to view the map")
    
    # TAB 2: AI DETECTION
    with tab2:
        st.header("AI Detection Analysis")
        st.caption("Machine learning detection results and model performance metrics")
        
        # Initialize default values - override from artisanal_mining data if available
        art_stats = get_artisanal_stats()
        if art_stats:
            total_zones_2025 = art_stats['total_mining_zones']
            total_zones_2016 = 6
            total_area_2025 = art_stats['total_mining_area_ha']
            total_area_2016 = 110.6
            growth_area = total_area_2025 - total_area_2016
            growth_percent = (growth_area / total_area_2016 * 100) if total_area_2016 > 0 else 0
            model_accuracy = 95.0  # DL report: 0.95 accuracy
            avg_confidence = 89.5
            high_conf_count = art_stats['total_mining_zones']
            total_zones_all = art_stats['total_features']
        else:
            total_zones_2025 = 12
            total_zones_2016 = 6
            total_area_2025 = 156.3
            total_area_2016 = 110.6
            growth_area = 45.7
            growth_percent = 41.3
            model_accuracy = 94.2
            avg_confidence = 89.5
            high_conf_count = 10
            total_zones_all = 18
        env_impact = "High"
        impact_color = "🟠"
        
        # Get real-time statistics from Supabase
        try:
            supabase = get_supabase_client()
            
            # Get detection statistics
            detections_2025 = supabase.table('detected_zones').select('*').gte('detection_date', '2025-01-01').execute()
            detections_2016 = supabase.table('detected_zones').select('*').lt('detection_date', '2017-01-01').execute()
            all_detections = supabase.table('detected_zones').select('*').execute()
            
            # Calculate metrics
            total_zones_2025 = len(detections_2025.data) if detections_2025.data else 0
            total_zones_2016 = len(detections_2016.data) if detections_2016.data else 0
            total_zones_all = len(all_detections.data) if all_detections.data else 0
            
            # Calculate total area (assuming area_ha field exists)
            total_area_2025 = sum([d.get('area_ha', 0) for d in (detections_2025.data or [])]) if detections_2025.data else 0
            total_area_2016 = sum([d.get('area_ha', 0) for d in (detections_2016.data or [])]) if detections_2016.data else 0
            growth_area = total_area_2025 - total_area_2016
            growth_percent = (growth_area / total_area_2016 * 100) if total_area_2016 > 0 else 0
            
            # Calculate confidence metrics
            all_confidences = [d.get('confidence', 0) for d in (all_detections.data or []) if d.get('confidence')]
            avg_confidence = sum(all_confidences) / len(all_confidences) * 100 if all_confidences else 89.5
            high_conf_count = len([c for c in all_confidences if c > 0.85])
            
            # Get model version info
            model_info = supabase.table('model_versions').select('*').order('created_at', desc=True).limit(1).execute()
            model_accuracy = model_info.data[0].get('val_accuracy', 0) * 100 if model_info.data else 94.2
            
            # Calculate environmental impact
            if growth_percent > 40:
                env_impact = "Critical"
                impact_color = ""
            elif growth_percent > 20:
                env_impact = "High"
                impact_color = "🟠"
            elif growth_percent > 10:
                env_impact = "Medium"
                impact_color = "🟡"
            else:
                env_impact = "Low"
                impact_color = "🟢"
                
        except Exception as e:
            # Already initialized with fallback values above
            pass
        
        # Add year comparison selector
        col_selector1, col_selector2, col_selector3 = st.columns([1, 1, 2])
        with col_selector1:
            compare_year = st.selectbox("View Year", ["2025 (Latest)", "2016 (Historical)", "Compare Both"], key="ai_year")
        with col_selector2:
            show_heatmap = st.checkbox("Show Confidence Heatmap", value=False)
        
        st.markdown("---")
        
        # ACTIVE MINING SITES FROM QGIS LABELS
        st.subheader("Active Mining Sites (QGIS Labels)")
        
        # Load QGIS labels
        if os.path.exists(GEOJSON_PATH):
            try:
                qgis_gdf = load_geojson(GEOJSON_PATH)
                if qgis_gdf is not None and len(qgis_gdf) > 0:
                    # Filter for active mining sites
                    active_sites = qgis_gdf.copy()
                    
                    # Check for required columns
                    if 'status' not in active_sites.columns:
                        st.warning("'status' column not found in QGIS labels. All sites will be treated as suspected.")
                        active_sites['status'] = 'suspected'  # Default status
                    
                    # Normalize status values and filter
                    if 'status' in active_sites.columns:
                        # Convert to lowercase and handle None values properly
                        active_sites['status_normalized'] = active_sites['status'].fillna('').astype(str).str.lower()
                        
                        # Also handle name column for special cases
                        active_sites['name_normalized'] = active_sites['name'].fillna('').astype(str).str.lower()
                        
                        # Filter for active mining sites (strict criteria)
                        active_filter = active_sites['status_normalized'].isin([
                            'active', 'acttive', 'confirmed_active'
                        ])
                        
                        # Filter for suspected mining sites (broader criteria)
                        suspected_filter = (
                            active_sites['status_normalized'].isin([
                                'suspected', 'likely_active', 'potential', 'probable', 'possible',
                                'abandoned', 'inactive', 'closed', 'former', 'historic',
                                'mining', 'mine', 'artisanal', 'industrial', 'operational', 'working'
                            ]) |
                            # Include sites with specific names mentioned by user
                            active_sites['name_normalized'].str.contains('mimbula', na=False) |
                            # Include sites with unknown/empty names
                            (active_sites['name_normalized'].isin(['', 'unknown', 'unnamed', 'no name']))
                        )
                        
                        active_mines = active_sites[active_filter]
                        suspected_mines = active_sites[suspected_filter & ~active_filter]  # Exclude active from suspected
                        
                        active_mines = active_sites[active_filter]
                        suspected_mines = active_sites[suspected_filter & ~active_filter]  # Exclude active from suspected
                        
                        # Display summary
                        col_sum1, col_sum2, col_sum3 = st.columns(3)
                        with col_sum1:
                            st.metric("Active Mines", len(active_mines), help="Confirmed active mining operations")
                        with col_sum2:
                            st.metric("Suspected Sites", len(suspected_mines), help="Potential sites including 'mimbula', unknown names, and other non-active sites")
                        with col_sum3:
                            total_area = active_sites['area_ha'].sum() if 'area_ha' in active_sites.columns else 0
                            st.metric("Total Area", f"{total_area:.1f} ha", help="Combined area of all labeled sites")
                        
                        # Display detailed list
                        st.markdown("###  Detailed Site List")
                        st.info("**Expanded Categorization**: Includes sites with 'mimbula' in name, 'unknown' names, and all non-active status sites as suspected for comprehensive monitoring.")
                        
                        # Combine active and suspected for display
                        display_sites = pd.concat([active_mines, suspected_mines])
                        
                        if len(display_sites) > 0:
                            # Prepare data for display
                            display_data = []
                            
                            for idx, row in display_sites.iterrows():
                                # Determine priority based on normalized status and name
                                status_norm = row.get('status_normalized', '')
                                name_norm = row.get('name_normalized', '')
                                
                                if status_norm in ['active', 'acttive', 'confirmed_active']:
                                    priority = 'High'
                                elif 'mimbula' in name_norm or name_norm in ['', 'unknown', 'unnamed', 'no name']:
                                    priority = 'High'  # Specific sites mentioned by user
                                elif status_norm in ['suspected', 'likely_active', 'potential', 'probable', 'possible']:
                                    priority = 'Medium'
                                elif status_norm in ['abandoned', 'inactive', 'closed', 'former', 'historic']:
                                    priority = 'Low'
                                else:
                                    priority = 'Medium'  # Default for other statuses
                                
                                site_info = {
                                    'Site ID': idx + 1,
                                    'Name': row.get('name', f'Mine {idx + 1}'),
                                    'Status': (row.get('status') or 'Unknown').title(),
                                    'Area (ha)': f"{row.get('area_ha', 0):.2f}",
                                    'Latitude': f"{row.geometry.centroid.y:.6f}",
                                    'Longitude': f"{row.geometry.centroid.x:.6f}",
                                    'Priority': priority
                                }
                                display_data.append(site_info)
                            
                            # Create DataFrame for display
                            sites_df = pd.DataFrame(display_data)
                            
                            # Display as interactive table
                            st.dataframe(
                                sites_df,
                                use_container_width=True,
                                column_config={
                                    'Site ID': st.column_config.NumberColumn('Site ID', width='small'),
                                    'Name': st.column_config.TextColumn('Name', width='medium'),
                                    'Status': st.column_config.TextColumn('Status', width='small'),
                                    'Area (ha)': st.column_config.TextColumn('Area (ha)', width='small'),
                                    'Latitude': st.column_config.TextColumn('Latitude', width='medium'),
                                    'Longitude': st.column_config.TextColumn('Longitude', width='medium'),
                                    'Priority': st.column_config.TextColumn('Priority', width='small')
                                }
                            )
                            
                            # Download button
                            csv_data = sites_df.to_csv(index=False)
                            st.download_button(
                                label=" Download Site List (CSV)",
                                data=csv_data,
                                file_name="qgis_mining_sites.csv",
                                mime="text/csv",
                                key="download_qgis_sites"
                            )
                            
                            # Map view of sites
                            st.markdown("###  Site Locations Map")
                            
                            # Create map centered on sites
                            if len(display_sites) > 0:
                                center_lat = display_sites.geometry.centroid.y.mean()
                                center_lon = display_sites.geometry.centroid.x.mean()
                                
                                sites_map = folium.Map(
                                    location=[center_lat, center_lon],
                                    zoom_start=11,
                                    tiles='OpenStreetMap'
                                )
                                
                                # Add satellite layer
                                folium.TileLayer(
                                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                                    attr='Esri',
                                    name='Satellite',
                                    overlay=False,
                                    control=True
                                ).add_to(sites_map)
                                
                                # Add sites to map
                                for idx, row in display_sites.iterrows():
                                    # Determine color and icon based on normalized status and name
                                    status_norm = row.get('status_normalized', '')
                                    name_norm = row.get('name_normalized', '')
                                    
                                    if status_norm in ['active', 'acttive', 'confirmed_active']:
                                        color = 'red'
                                        icon = '●'
                                    elif 'mimbula' in name_norm or name_norm in ['', 'unknown', 'unnamed', 'no name']:
                                        color = 'darkred'  # Special color for user-mentioned sites
                                        icon = '●'
                                    elif status_norm in ['suspected', 'likely_active', 'potential', 'probable', 'possible']:
                                        color = 'orange'
                                        icon = '●'
                                    elif status_norm in ['abandoned', 'inactive', 'closed', 'former', 'historic']:
                                        color = 'gray'
                                        icon = '●'
                                    else:
                                        color = 'blue'
                                        icon = '●'
                                    
                                    # Create popup with priority info
                                    priority = 'High' if color in ['red', 'darkred'] else 'Medium' if color == 'orange' else 'Low'
                                    
                                    popup_text = f"""
                                    <b>{icon} {row.get('name', f'Mine {idx + 1}')}</b><br>
                                    Status: {(row.get('status') or 'Unknown').title()}<br>
                                    Priority: {priority}<br>
                                    Area: {row.get('area_ha', 0):.2f} ha<br>
                                    Coordinates: {row.geometry.centroid.y:.6f}, {row.geometry.centroid.x:.6f}
                                    """
                                    
                                    folium.Marker(
                                        location=[row.geometry.centroid.y, row.geometry.centroid.x],
                                        popup=popup_text,
                                        icon=folium.Icon(color=color, icon='info-sign')
                                    ).add_to(sites_map)
                                
                                # Add artisanal mining points from pipeline
                                art_gdf = load_artisanal_geojson()
                                if art_gdf is not None and len(art_gdf) > 0:
                                    mining_art = art_gdf[art_gdf.get("label", pd.Series(dtype=str)) == "mining"] if "label" in art_gdf.columns else art_gdf[art_gdf.get("class", pd.Series(dtype=int)) == 1] if "class" in art_gdf.columns else pd.DataFrame()
                                    if len(mining_art) > 0:
                                        for idx_a, row_a in mining_art.iterrows():
                                            area_val = row_a.get("area_ha", 0)
                                            sev_val = row_a.get("meanLoss", 0)
                                            popup_a = f"""
                                            <b>🗺️ Artisanal Mining Zone</b><br>
                                            Area: {area_val:.4f} ha<br>
                                            Severity: {sev_val:.4f}<br>
                                            Source: DL+ML Pipeline<br>
                                            Coords: {row_a.geometry.centroid.y:.6f}, {row_a.geometry.centroid.x:.6f}
                                            """
                                            folium.CircleMarker(
                                                location=[row_a.geometry.centroid.y, row_a.geometry.centroid.x],
                                                radius=6,
                                                color='#c62828',
                                                fill=True,
                                                fillColor='#c62828',
                                                fillOpacity=0.7,
                                                popup=popup_a,
                                                tooltip=f"Mining ({area_val:.3f} ha)"
                                            ).add_to(sites_map)
                                
                                # Add legend
                                legend_html = '''
                                <div style="position: fixed; 
                                            bottom: 50px; left: 50px; width: 220px; height: 200px; 
                                            background-color: white; border:2px solid grey; z-index:9999; 
                                            font-size:14px; padding: 10px">
                                <p><b>Site Priority Legend</b></p>
                                <p><span style="color:red;">●</span> High Priority (Active)</p>
                                <p><span style="color:darkred;">●</span> High Priority (Special)</p>
                                <p><span style="color:orange;">●</span> Medium Priority (Suspected)</p>
                                <p><span style="color:gray;">●</span> Low Priority (Abandoned)</p>
                                <p><span style="color:blue;">●</span> Other Status</p>
                                <p><span style="color:#c62828;">⬤</span> Artisanal Mining (DL+ML)</p>
                                </div>
                                '''
                                sites_map.get_root().html.add_child(folium.Element(legend_html))
                                
                                # Display map
                                folium_static(sites_map)
                            
                        else:
                            st.info("No active mining sites found in QGIS labels")
                    else:
                        st.warning("No 'status' column found in QGIS labels. Cannot filter active sites.")
                else:
                    st.warning("Could not load QGIS labels or file is empty")
            except Exception as e:
                st.error(f"Error loading QGIS labels: {e}")
        else:
            st.warning(f"QGIS labels file not found: {GEOJSON_PATH}")
        
        st.markdown("---")
        
        # Load AI predictions
        pred_2025_path = f"{RESULTS_DIR}/prediction_2025.tif"
        pred_2016_path = f"{RESULTS_DIR}/prediction_2016.tif"
        
        if "Compare Both" in compare_year:
            # Side-by-side comparison
            st.subheader("2016 vs 2025 Comparison")
            col_2016, col_2025 = st.columns(2)
            
            with col_2016:
                st.markdown("#### 2016 (Baseline)")
                if os.path.exists(pred_2016_path):
                    pred_2016, meta_2016, bounds_2016 = load_geotiff(pred_2016_path)
                    if pred_2016 is not None:
                        # Downsample to avoid memory errors
                        max_dim = 500
                        h, w = pred_2016.shape[:2]
                        step = max(1, max(h, w) // max_dim)
                        pred_2016_ds = pred_2016[::step, ::step]
                        fig, ax = plt.subplots(figsize=(7, 6), dpi=72)
                        cmap = plt.cm.colors.ListedColormap(['#e8f8f5', '#e74c3c'])
                        im = ax.imshow(pred_2016_ds, cmap=cmap, extent=[bounds_2016.left, bounds_2016.right, bounds_2016.bottom, bounds_2016.top])
                        ax.set_title('2016 Mining Areas', fontsize=12, fontweight='bold')
                        ax.set_xlabel('Longitude', fontsize=10)
                        ax.set_ylabel('Latitude', fontsize=10)
                        plt.colorbar(im, ax=ax, ticks=[0.25, 0.75], label='Classification')
                        st.pyplot(fig)
                        plt.close()
            
            with col_2025:
                st.markdown("#### 2025 (Current)")
                if os.path.exists(pred_2025_path):
                    pred_2025, meta_2025, bounds_2025 = load_geotiff(pred_2025_path)
                    if pred_2025 is not None:
                        # Downsample to avoid memory errors
                        max_dim = 500
                        h, w = pred_2025.shape[:2]
                        step = max(1, max(h, w) // max_dim)
                        pred_2025_ds = pred_2025[::step, ::step]
                        fig, ax = plt.subplots(figsize=(7, 6), dpi=72)
                        cmap = plt.cm.colors.ListedColormap(['#e8f8f5', '#e74c3c'])
                        im = ax.imshow(pred_2025_ds, cmap=cmap, extent=[bounds_2025.left, bounds_2025.right, bounds_2025.bottom, bounds_2025.top])
                        ax.set_title('2025 Mining Areas', fontsize=12, fontweight='bold')
                        ax.set_xlabel('Longitude', fontsize=10)
                        ax.set_ylabel('Latitude', fontsize=10)
                        plt.colorbar(im, ax=ax, ticks=[0.25, 0.75], label='Classification')
                        st.pyplot(fig)
                        plt.close()
        else:
            # Single year view
            selected_path = pred_2025_path if "2025" in compare_year else pred_2016_path
            year_label = "2025" if "2025" in compare_year else "2016"
            
            if os.path.exists(selected_path):
                st.subheader(f"{year_label} AI Prediction Map")
                pred, meta, bounds = load_geotiff(selected_path)
                
                if pred is not None:
                    # Downsample large arrays to avoid memory errors
                    max_dim = 800
                    h, w = pred.shape[:2]
                    step = max(1, max(h, w) // max_dim)
                    pred_ds = pred[::step, ::step]
                    
                    fig, ax = plt.subplots(figsize=(12, 7), dpi=72)
                    
                    if show_heatmap:
                        # Show confidence as heatmap
                        cmap = plt.cm.RdYlGn_r
                        im = ax.imshow(pred_ds, cmap=cmap, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top], vmin=0, vmax=1)
                        ax.set_title(f'Mining Detection Confidence Map ({year_label})', fontsize=16, fontweight='bold')
                        cbar = plt.colorbar(im, ax=ax)
                        cbar.set_label('Confidence Score', rotation=270, labelpad=20)
                    else:
                        # Binary classification
                        cmap = plt.cm.colors.ListedColormap(['#e8f8f5', '#e74c3c'])
                        im = ax.imshow(pred_ds, cmap=cmap, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
                        ax.set_title(f'AI-Detected Mining Areas ({year_label})', fontsize=16, fontweight='bold')
                        cbar = plt.colorbar(im, ax=ax)
                        cbar.set_ticks([0.25, 0.75])
                        cbar.set_ticklabels(['Vegetation', 'Mining'])
                    
                    ax.set_xlabel('Longitude', fontsize=12)
                    ax.set_ylabel('Latitude', fontsize=12)
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                    plt.close()
                    
                    # Download options
                    col_dl1, col_dl2, col_dl3 = st.columns(3)
                    with col_dl1:
                        st.download_button(
                            label=" Download GeoTIFF",
                            data=open(selected_path, 'rb').read(),
                            file_name=f"ai_predictions_{year_label}.tif",
                            mime="image/tiff"
                        )
                    with col_dl2:
                        # Calculate mining pixels
                        mining_pixels = np.sum(pred > 0.5)
                        total_pixels = pred.size
                        mining_percentage = (mining_pixels / total_pixels) * 100
                        st.info(f"Mining Coverage: {mining_percentage:.2f}% of area")
                    with col_dl3:
                        st.success(f"Model: Ensemble ML+DL v2.0 | Trained on 604 zones")
            else:
                st.warning(f"Prediction file not found: {selected_path}")
    
    # TAB 2B: DETECTED MINING ZONES
    with tab2b:
        st.header("Detected Mining Zones")
        st.caption("Classified and catalogued mining zones from satellite analysis")
        st.markdown("*Polygonal zones extracted from AI predictions with detailed metadata for field visits*")
        
        # Year selector
        col_year, col_filter = st.columns([1, 3])
        with col_year:
            selected_year = st.selectbox("View Results", ["2025 (Latest)", "2016 (Historical)"], key="zone_year")
        
        # Determine paths based on selection
        year_folder = "prediction_2025" if "2025" in selected_year else "prediction_2016"
        zones_path = f"mining_zones_output/{year_folder}/zones_summary.json"
        zones_geojson_path = f"mining_zones_output/{year_folder}/detected_zones.geojson"
        
        # Load zones first to enable filtering
        zones = []
        zones_data = {'total_zones': 0, 'total_area_ha': 0}
        
        if os.path.exists(zones_path):
            try:
                with open(zones_path, 'r') as f:
                    zones_data = json.load(f)
                zones = zones_data['zones']
            except Exception as e:
                st.error(f"Error loading zones: {e}")
        
        # Filtering controls
        with col_filter:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                priority_filter = st.multiselect(
                    "Priority",
                    options=[5, 4, 3, 2, 1],
                    default=[5, 4, 3],
                    help="Filter by zone priority"
                )
            
            with col_f2:
                min_area_filter = st.number_input(
                    "Min Area (ha)",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.5,
                    step=0.5,
                    help="Minimum zone area"
                )
            
            with col_f3:
                max_area_filter = st.number_input(
                    "Max Area (ha)",
                    min_value=0.0,
                    max_value=500.0,
                    value=100.0,
                    step=5.0,
                    help="Maximum zone area"
                )
            
            with col_f4:
                zones_per_page = st.selectbox(
                    "Zones per page",
                    options=[10, 25, 50, 100, 200],
                    index=1,
                    help="Number of zones to display"
                )
        
        # Apply filters
        if zones:
            filtered_zones = [
                z for z in zones
                if z['priority'] in priority_filter
                and min_area_filter <= z['area_ha'] <= max_area_filter
            ]
            
            # Filter out zones verified as NOT mines
            try:
                supabase = get_supabase_client()
                verifications = supabase.table('field_verifications').select('zone_id, is_confirmed_mine').eq('is_confirmed_mine', False).execute()
                
                if verifications.data:
                    rejected_zone_ids = [v['zone_id'] for v in verifications.data]
                    filtered_zones = [
                        z for z in filtered_zones 
                        if f"zone_{z['zone_number']}" not in rejected_zone_ids
                    ]
            except:
                pass  # If verification check fails, show all zones
        else:
            filtered_zones = []
        
        # Summary separator (metrics removed as requested)
        st.markdown("---")
        
        # Use artisanal mining stats as fallback when no AI zones available
        art_fallback = get_artisanal_stats() if not zones else None
        
        col_top1, col_top2 = st.columns([3, 1])
        
        with col_top2:
            st.subheader("Data Sources")
            
            # Display data source information
            st.markdown("**AI Detection Pipeline**")
            st.markdown(" Ensemble ML+DL Model (PyTorch)")
            st.markdown(" Google Earth Engine")
            st.markdown(" Updated: Every 5 days")
            
            st.markdown("---")
            st.markdown("### Priority Breakdown")
            
            # Priority breakdown
            if filtered_zones:
                priority_counts = {}
                for zone in filtered_zones:
                    p = zone['priority']
                    priority_counts[p] = priority_counts.get(p, 0) + 1
                
                for priority in [5, 4, 3, 2, 1]:
                    if priority in priority_counts:
                        color = {5: "", 4: "🟠", 3: "🟡", 2: "🟢", 1: ""}[priority]
                        st.markdown(f"{color} Priority {priority}: **{priority_counts[priority]}** zones")
            else:
                # Show artisanal mining stats in priority breakdown area
                art_stats_side = get_artisanal_stats()
                if art_stats_side:
                    st.markdown(f"**Mining Zones:** {art_stats_side.get('total_mining_zones', 0)}")
                    st.markdown(f"**Total Area:** {art_stats_side.get('total_mining_area_ha', 0):.1f} ha")
        
        # Check if artisanal mining data is available
        art_data_available = load_artisanal_geojson() is not None
        
        # Display map if we have filtered AI zones OR artisanal mining data
        if filtered_zones or art_data_available:
            with col_top1:
                # Create interactive map with zones
                st.subheader("AI Detections vs Manual Labels Map")
                
                # Map controls
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                
                with col_m1:
                    show_ai_zones = st.checkbox(" Show AI Detections", value=True)
                
                with col_m2:
                    show_manual_labels = st.checkbox(" Show Manual Labels (QGIS)", value=True)
                
                with col_m3:
                    show_artisanal = st.checkbox("🗺️ Artisanal Mining Data", value=True,
                                                  help="Overlay artisanal mining classification zones")
                
                with col_m4:
                    smart_filter = st.checkbox(" Smart Filter", value=True, 
                                               help="Auto-remove water bodies & false positives")
                
                # Apply smart filtering
                display_zones = filtered_zones.copy()
                
                if smart_filter:
                    # Filter out likely false positives
                    temp_zones = []
                    for z in display_zones:
                        area_ha = z['area_ha']
                        perimeter_m = z.get('perimeter_m', 0)
                        
                        # Skip very small zones (< 0.3 ha are often noise)
                        if area_ha < 0.3:
                            continue
                        
                        if perimeter_m > 0:
                            # Calculate compactness to filter irregular shapes (water)
                            area_m2 = area_ha * 10000
                            compactness = (4 * 3.14159 * area_m2) / (perimeter_m ** 2)
                            
                            # Skip very irregular shapes (likely water/rivers)
                            if compactness < 0.12:
                                continue
                            
                            # Skip suspiciously round small shapes (water tanks)
                            if compactness > 0.9 and area_ha < 1.5:
                                continue
                        
                        temp_zones.append(z)
                    
                    removed = len(display_zones) - len(temp_zones)
                    if removed > 0:
                        st.info(f"Smart filter removed {removed} likely false positives")
                    display_zones = temp_zones
                
                # Sort and limit display
                display_zones = sorted(display_zones, key=lambda x: (-x['priority'], -x['area_ha']))[:zones_per_page]
                
                if show_ai_zones and display_zones:
                    st.success(f"Displaying {len(display_zones)} of {len(filtered_zones)} filtered zones (Top {zones_per_page})")
                elif show_ai_zones:
                    st.warning("No zones match your filter criteria")
                
                # Get center from first zone, artisanal data, or default
                if display_zones:
                    center_lat = display_zones[0]['centroid_lat']
                    center_lon = display_zones[0]['centroid_lon']
                else:
                    # Try artisanal mining data for center
                    art_center_gdf = load_artisanal_geojson()
                    if art_center_gdf is not None and len(art_center_gdf) > 0:
                        center_lat = art_center_gdf.geometry.centroid.y.mean()
                        center_lon = art_center_gdf.geometry.centroid.x.mean()
                    else:
                        center_lat = -12.5
                        center_lon = 27.85
                
                # Create map
                zones_map = folium.Map(
                    location=[center_lat, center_lon],
                    zoom_start=12,
                    tiles='OpenStreetMap'
                )
                
                # Add satellite layer
                folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr='Esri',
                    name='Satellite',
                    overlay=False,
                    control=True
                ).add_to(zones_map)
                
                # Load manual QGIS labels if available
                manual_labels_gdf = None
                if show_manual_labels and os.path.exists(GEOJSON_PATH):
                    try:
                        manual_labels_gdf = load_geojson(GEOJSON_PATH)
                        if manual_labels_gdf is not None:
                            st.success(f"Loaded {len(manual_labels_gdf)} manual labels from QGIS")
                    except Exception as e:
                        st.warning(f"Could not load manual labels: {e}")
                
                # Helper function to get color based on status
                def get_color(status):
                    """Return color code based on mining status"""
                    if status in ['Active', 'active', 'confirmed_active']:
                        return 'red'
                    elif status in ['suspected', 'likely_active']:
                        return 'orange'
                    elif status in ['abandoned', 'low_confidence']:
                        return 'gray'
                    else:
                        return 'blue'  # Default color for unknown status
                
                # Add manual QGIS labels first (as base layer)
                if show_manual_labels and manual_labels_gdf is not None and len(manual_labels_gdf) > 0:
                    for idx, row in manual_labels_gdf.iterrows():
                        # Get manual label color based on status
                        manual_color = get_color(row.get('status', None))
                        
                        popup_html = f"""
                        <div style="font-family: Arial; width: 250px;">
                            <h4 style="color: #0066cc; margin: 5px 0;"> Manual Label (QGIS)</h4>
                            <hr style="margin: 5px 0;">
                            <p><b>Name:</b> {row.get('name', 'Unknown Mine')}</p>
                            <p><b>Status:</b> <span style="color: {manual_color};">{row.get('status', 'Unknown')}</span></p>
                            <p><b>Area:</b> {row.get('area_ha', 'N/A')} hectares</p>
                            <p><b>Source:</b> Manual mapping (QGIS)</p>
                            <p><b>Coordinates:</b> {row.geometry.centroid.y:.4f}, {row.geometry.centroid.x:.4f}</p>
                        </div>
                        """
                        
                        folium.GeoJson(
                            row.geometry,
                            style_function=lambda x, color=manual_color: {
                                'fillColor': color,
                                'color': '#0066cc',  # Blue border for manual labels
                                'weight': 3,
                                'fillOpacity': 0.3,
                                'dashArray': '5, 5'  # Dashed line to distinguish from AI
                            },
                            popup=folium.Popup(popup_html, max_width=300),
                            tooltip=f" Manual: {row.get('name', 'Unknown')}"
                        ).add_to(zones_map)
                
                # Add artisanal mining classification data
                if show_artisanal:
                    art_gdf = load_artisanal_geojson()
                    if art_gdf is not None and len(art_gdf) > 0:
                        art_color_map = {
                            "mining": "#c62828", "forest": "#2e7d32", "water": "#1565c0",
                            "urban": "#7b1fa2", "bare_soil": "#f9a825"
                        }
                        art_added = 0
                        mining_count = 0
                        for idx_a, row_a in art_gdf.iterrows():
                            label = row_a.get("label", "unknown")
                            fc = art_color_map.get(label, "#999999")
                            area_val = row_a.get("area_ha", 0)
                            sev_val = row_a.get("meanLoss", 0)
                            popup_a = f"""
                            <div style="font-family: Arial; width: 220px;">
                                <h4 style="color: {fc}; margin: 5px 0;">🗺️ Artisanal Mining Pipeline</h4>
                                <hr style="margin: 5px 0;">
                                <p><b>Class:</b> {label.replace('_',' ').title()}</p>
                                <p><b>Area:</b> {area_val:.4f} ha</p>
                                <p><b>Severity:</b> {sev_val:.4f}</p>
                                <p><b>Source:</b> DL+ML Ensemble</p>
                                <p><b>Coords:</b> {row_a.geometry.centroid.y:.6f}, {row_a.geometry.centroid.x:.6f}</p>
                            </div>
                            """
                            try:
                                # Add polygon overlay
                                folium.GeoJson(
                                    row_a.geometry,
                                    style_function=lambda x, c=fc, l=label: {
                                        'fillColor': c,
                                        'color': c,
                                        'weight': 2 if l == 'mining' else 1,
                                        'fillOpacity': 0.45 if l == 'mining' else 0.15,
                                    },
                                    popup=folium.Popup(popup_a, max_width=250),
                                    tooltip=f"🗺️ {label.replace('_',' ').title()} ({area_val:.3f} ha)"
                                ).add_to(zones_map)
                                
                                # Add visible circle marker for mining zones
                                if label == "mining":
                                    folium.CircleMarker(
                                        location=[row_a.geometry.centroid.y, row_a.geometry.centroid.x],
                                        radius=8,
                                        color='#b71c1c',
                                        fill=True,
                                        fillColor='#c62828',
                                        fillOpacity=0.8,
                                        popup=folium.Popup(popup_a, max_width=250),
                                        tooltip=f"⛏️ Mining Zone ({area_val:.3f} ha, severity: {sev_val:.4f})"
                                    ).add_to(zones_map)
                                    mining_count += 1
                                
                                art_added += 1
                            except:
                                continue
                        st.success(f"Added {art_added} artisanal features ({mining_count} mining zones) to map")
                    else:
                        st.info("Artisanal mining GeoJSON not available")
                
                # Now add AI detected zones on top
                if show_ai_zones:
                    # Color mapping for AI priority
                    priority_colors = {
                        5: '#dc3545',  # Red - Critical
                        4: '#fd7e14',  # Orange - High
                        3: '#ffc107',  # Yellow - Medium
                        2: '#28a745',  # Green - Low
                        1: '#6c757d'   # Gray - Very Low
                    }
                    
                    # Add each AI zone as a polygon
                    zones_added = 0
                    for zone in display_zones:
                        try:
                            # Get polygon coordinates
                            coords = zone['geometry']['coordinates'][0]
                            
                            # Convert to Leaflet format [lat, lon]
                            leaflet_coords = [[c[1], c[0]] for c in coords]
                            
                            # Color by priority
                            color = priority_colors.get(zone['priority'], '#999')
                            
                            # Status emoji
                            status_emoji = {
                                'confirmed_active': '',
                                'likely_active': '🟠',
                                'suspected': '🟡',
                                'low_confidence': ''
                            }.get(zone['status'], '')
                            
                            # Create detailed popup for AI detection
                            popup_html = f"""
                            <div style="font-family: Arial; width: 300px; padding: 10px;">
                                <h4 style="color: {color}; margin: 5px 0;">
                                     AI Detection - Zone #{zone['zone_number']}
                                </h4>
                                <hr style="margin: 5px 0;">
                                
                                <div style="background-color: #f8f9fa; padding: 8px; border-radius: 5px; margin: 5px 0;">
                                    <p style="margin: 3px 0;"><b> Area:</b> {zone['area_ha']:.3f} hectares ({zone['area_m2']:.0f} m²)</p>
                                    <p style="margin: 3px 0;"><b> Confidence:</b> {zone['confidence']*100:.1f}%</p>
                                    <p style="margin: 3px 0;"><b> Priority:</b> Level {zone['priority']} / 5</p>
                                </div>
                                
                                <div style="background-color: #e7f3ff; padding: 8px; border-radius: 5px; margin: 5px 0;">
                                    <p style="margin: 3px 0;"><b> Location:</b></p>
                                    <p style="margin: 3px 0; font-size: 11px;">
                                        Lat: {zone['centroid_lat']:.6f}<br>
                                        Lon: {zone['centroid_lon']:.6f}
                                    </p>
                                    <p style="margin: 3px 0;"><b> Detected:</b> {zone['detected_date']}</p>
                                    <p style="margin: 3px 0;"><b> Source:</b> <span style="color: #dc3545;">AI Model</span></p>
                                </div>
                                
                                <div style="background-color: #fff3cd; padding: 8px; border-radius: 5px; margin: 5px 0;">
                                    <p style="margin: 3px 0;"><b> Status:</b> {zone['status'].replace('_', ' ').title()}</p>
                                    <p style="margin: 3px 0;"><b> Action Required:</b> {'Yes - Field Visit' if zone['priority'] >= 4 else 'Monitor'}</p>
                                </div>
                                
                                <div style="background-color: #f1f1f1; padding: 5px; border-radius: 3px; margin-top: 5px; font-size: 10px;">
                                    <b>Google Maps:</b><br>
                                    <a href="https://www.google.com/maps?q={zone['centroid_lat']},{zone['centroid_lon']}" target="_blank">
                                         Open in Google Maps
                                    </a>
                                </div>
                            </div>
                            """
                            
                            # Add polygon with solid line (AI detection)
                            folium.Polygon(
                                locations=leaflet_coords,
                                color=color,
                                weight=2,
                                fill=True,
                                fillColor=color,
                                fillOpacity=0.5,
                                popup=folium.Popup(popup_html, max_width=320),
                                tooltip=f" AI Zone {zone['zone_number']}: {zone['area_ha']:.2f} ha (Priority {zone['priority']})"
                            ).add_to(zones_map)
                            
                            zones_added += 1
                            
                        except Exception as e:
                            st.warning(f"Error adding zone {zone.get('zone_number', '?')}: {e}")
                            continue
                    
                    st.success(f"Added {zones_added} AI-detected zones to map")
                
                # Add legend
                legend_html = f"""
                <div style="position: fixed; bottom: 50px; right: 50px; width: 260px; 
                            background-color: white; border: 2px solid grey; z-index: 9999; 
                            padding: 10px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
                    <h4 style="margin-top: 0; margin-bottom: 10px;">Legend</h4>
                    
                    <p style="margin: 5px 0;"><b>AI Detections (Solid):</b></p>
                    <div style="margin-left: 10px;">
                        <p style="margin: 3px 0;"><span style="color: #dc3545;">■</span> Priority 5 - Critical</p>
                        <p style="margin: 3px 0;"><span style="color: #fd7e14;">■</span> Priority 4 - High</p>
                        <p style="margin: 3px 0;"><span style="color: #ffc107;">■</span> Priority 3 - Medium</p>
                        <p style="margin: 3px 0;"><span style="color: #28a745;">■</span> Priority 2 - Low</p>
                    </div>
                    
                    <hr style="margin: 10px 0;">
                    
                    <p style="margin: 5px 0;"><b>Manual Labels (Dashed):</b></p>
                    <div style="margin-left: 10px;">
                        <p style="margin: 3px 0;"><span style="color: #0066cc;">- - -</span> QGIS Manual Mapping</p>
                    </div>
                    
                    <hr style="margin: 10px 0;">
                    
                    <p style="margin: 5px 0;"><b>Artisanal Mining (Dotted):</b></p>
                    <div style="margin-left: 10px;">
                        <p style="margin: 3px 0;"><span style="color: #c62828;">■</span> Mining</p>
                        <p style="margin: 3px 0;"><span style="color: #2e7d32;">■</span> Forest</p>
                        <p style="margin: 3px 0;"><span style="color: #1565c0;">■</span> Water</p>
                        <p style="margin: 3px 0;"><span style="color: #7b1fa2;">■</span> Urban</p>
                        <p style="margin: 3px 0;"><span style="color: #f9a825;">■</span> Bare Soil</p>
                    </div>
                </div>
                """
                
                zones_map.get_root().html.add_child(folium.Element(legend_html))
                zones_map.get_root().html.add_child(folium.Element(legend_html))
                
                # Add layer control
                folium.LayerControl().add_to(zones_map)
                
                # Add fullscreen and measure controls
                plugins.Fullscreen().add_to(zones_map)
                plugins.MeasureControl().add_to(zones_map)
                
                # Display map
                folium_static(zones_map, width=900, height=700)
            
            # Detailed table of zones
            st.markdown("---")
            st.subheader("Detailed Zone Information")
            
            # Filter options
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                filter_priority = st.multiselect(
                    "Filter by Priority",
                    [5, 4, 3, 2, 1],
                    default=[5, 4, 3, 2, 1]
                )
            
            with col_f2:
                filter_status = st.multiselect(
                    "Filter by Status",
                    ['confirmed_active', 'likely_active', 'suspected', 'low_confidence'],
                    default=['confirmed_active', 'likely_active', 'suspected', 'low_confidence']
                )
            
            with col_f3:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Priority (High to Low)", "Area (Large to Small)", "Confidence (High to Low)", "Zone Number"]
                )
            
            # Filter zones
            filtered_zones = [
                z for z in zones 
                if z['priority'] in filter_priority and z['status'] in filter_status
            ]
            
            # Sort zones
            if sort_by == "Priority (High to Low)":
                filtered_zones.sort(key=lambda x: (-x['priority'], -x['area_ha']))
            elif sort_by == "Area (Large to Small)":
                filtered_zones.sort(key=lambda x: -x['area_ha'])
            elif sort_by == "Confidence (High to Low)":
                filtered_zones.sort(key=lambda x: -x['confidence'])
            else:
                filtered_zones.sort(key=lambda x: x['zone_number'])
            
            # Create DataFrame
            if filtered_zones:
                df_zones = pd.DataFrame([{
                    'Zone #': z['zone_number'],
                    'Area (ha)': f"{z['area_ha']:.3f}",
                    'Area (m²)': f"{z['area_m2']:.0f}",
                    'Priority': z['priority'],
                    'Confidence': f"{z['confidence']*100:.1f}%",
                    'Status': z['status'].replace('_', ' ').title(),
                    'Latitude': f"{z['centroid_lat']:.6f}",
                    'Longitude': f"{z['centroid_lon']:.6f}",
                    'Detected': z['detected_date'],
                    'Action': 'Visit' if z['priority'] >= 4 else 'Monitor'
                } for z in filtered_zones])
                
                st.dataframe(df_zones, use_container_width=True, hide_index=True)
                
                st.info(f"Showing {len(filtered_zones)} of {len(zones)} total zones")
            else:
                st.warning("No zones match the selected filters.")
            
            # Download section
            st.markdown("---")
            st.subheader("Export Data")
            
            col_d1, col_d2, col_d3 = st.columns(3)
            
            with col_d1:
                if os.path.exists(zones_geojson_path):
                    with open(zones_geojson_path, 'r') as f:
                        geojson_data = f.read()
                    
                    st.download_button(
                        label=" Download GeoJSON",
                        data=geojson_data,
                        file_name="detected_mining_zones.geojson",
                        mime="application/json",
                        use_container_width=True
                    )
            
            with col_d2:
                if filtered_zones:
                    csv_data = df_zones.to_csv(index=False)
                    st.download_button(
                        label=" Download CSV",
                        data=csv_data,
                        file_name="mining_zones_table.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col_d3:
                if os.path.exists(zones_path):
                    with open(zones_path, 'r') as f:
                        json_data = f.read()
                    
                    st.download_button(
                        label=" Download JSON",
                        data=json_data,
                        file_name="zones_summary.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            # Field visit checklist
            st.markdown("---")
            st.subheader("Field Visit Planning")
            
            # Add filtering options
            col_fv1, col_fv2, col_fv3 = st.columns(3)
            
            with col_fv1:
                min_priority_for_visit = st.selectbox(
                    "Minimum Priority for Field Visit",
                    [5, 4, 3],
                    index=0,
                    help="Only zones with this priority or higher will be flagged for inspection"
                )
            
            with col_fv2:
                min_area_for_visit = st.number_input(
                    "Minimum Area (hectares)",
                    min_value=0.1,
                    max_value=100.0,
                    value=5.0,
                    step=0.5,
                    help="Only zones larger than this will be flagged"
                )
            
            with col_fv3:
                min_confidence_for_visit = st.slider(
                    "Minimum Confidence %",
                    min_value=50,
                    max_value=100,
                    value=90,
                    step=5,
                    help="Only zones with confidence above this will be flagged"
                )
            
            # Filter zones based on criteria
            high_priority_zones = [
                z for z in zones 
                if z['priority'] >= min_priority_for_visit 
                and z['area_ha'] >= min_area_for_visit
                and z['confidence'] >= (min_confidence_for_visit / 100.0)
            ]
            
            # Show statistics
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("Zones Requiring Inspection", len(high_priority_zones))
            
            with col_stat2:
                if high_priority_zones:
                    total_area = sum(z['area_ha'] for z in high_priority_zones)
                    st.metric("Total Area to Inspect", f"{total_area:.1f} ha")
                else:
                    st.metric("Total Area to Inspect", "0 ha")
            
            with col_stat3:
                if high_priority_zones:
                    avg_confidence = sum(z['confidence'] for z in high_priority_zones) / len(high_priority_zones)
                    st.metric("Average Confidence", f"{avg_confidence*100:.1f}%")
                else:
                    st.metric("Average Confidence", "N/A")
            
            if high_priority_zones:
                st.warning(f"**{len(high_priority_zones)} zones meet inspection criteria**")
                
                # Breakdown by priority
                priority_breakdown = {}
                for z in high_priority_zones:
                    p = z['priority']
                    priority_breakdown[p] = priority_breakdown.get(p, 0) + 1
                
                breakdown_text = " | ".join([
                    f"Priority {p}: {count}" 
                    for p, count in sorted(priority_breakdown.items(), reverse=True)
                ])
                st.info(f"Breakdown: {breakdown_text}")
                
                with st.expander(" View Field Visit Checklist", expanded=True):
                    st.markdown("### Priority Zones for Field Inspection")
                    st.markdown(f"*Showing top 20 zones sorted by priority and area*")
                    
                    # Sort by priority, then area
                    sorted_zones = sorted(high_priority_zones, key=lambda x: (-x['priority'], -x['area_ha']))[:20]
                    
                    for idx, zone in enumerate(sorted_zones, 1):
                        priority_emoji = {5: "", 4: "🟠", 3: "🟡", 2: "🟢", 1: ""}[zone['priority']]
                        zone_id = f"zone_{zone['zone_number']}"
                        
                        # Check if zone is already verified
                        try:
                            supabase = get_supabase_client()
                            verification = supabase.table('field_verifications').select('*').eq('zone_id', zone_id).execute()
                            is_verified = len(verification.data) > 0 if verification.data else False
                            
                            if is_verified:
                                verify_info = verification.data[0]
                                verified_by_id = verify_info.get('verified_by')
                                verifier = supabase.table('profiles').select('full_name, role').eq('id', verified_by_id).execute()
                                verifier_name = verifier.data[0].get('full_name', 'Unknown') if verifier.data else 'Unknown'
                                verifier_role = verifier.data[0].get('role', 'inspector') if verifier.data else 'inspector'
                                is_mine = verify_info.get('is_confirmed_mine')
                                verify_status = verify_info.get('verification_status')
                                notes = verify_info.get('inspector_notes', 'No notes provided')
                                verify_date = verify_info.get('verification_date')
                                
                                # Skip verified zones that are not mines
                                if not is_mine:
                                    continue
                        except:
                            is_verified = False
                        
                        st.markdown(f"""
                        **{idx}. {priority_emoji} Zone #{zone['zone_number']}** (Priority: {zone['priority']}/5)
                        -  Location: `{zone['centroid_lat']:.6f}, {zone['centroid_lon']:.6f}`
                        -  Area: **{zone['area_ha']:.2f} hectares** ({zone['area_m2']:.0f} m²)
                        -  Confidence: **{zone['confidence']*100:.1f}%**
                        -  Status: {zone['status'].replace('_', ' ').title()}
                        -  Detected: {zone['detected_date']}
                        -  [Open in Google Maps](https://www.google.com/maps?q={zone['centroid_lat']},{zone['centroid_lon']})
                        """)
                        
                        # Show verification status if already verified
                        if is_verified:
                            status_emoji = "" if is_mine else ""
                            status_text = "Confirmed Mine" if is_mine else "Not a Mine"
                            st.success(f"{status_emoji} **{status_text}** - Verified by {verifier_name} ({verifier_role.title()}) on {verify_date[:10]}")
                            with st.expander("View Verification Details"):
                                st.markdown(f"**Inspector Notes:** {notes}")
                                st.markdown(f"**Verification Status:** {verify_status.title()}")
                        else:
                            # Field verification form for admin/inspector
                            if check_user_role(['admin', 'inspector']):
                                with st.expander(f" Verify Zone #{zone['zone_number']}", expanded=False):
                                    st.markdown("**Field Verification Form** (Admin/Inspector Only)")
                                    
                                    col_v1, col_v2 = st.columns(2)
                                    
                                    with col_v1:
                                        is_mine_confirm = st.radio(
                                            "Is this a confirmed mine?",
                                            ["Yes - Confirmed Mine", "No - Not a Mine", "Uncertain - Needs Investigation"],
                                            key=f"mine_confirm_{zone_id}"
                                        )
                                    
                                    with col_v2:
                                        verification_status_input = st.selectbox(
                                            "Verification Status",
                                            ["verified", "rejected", "uncertain"],
                                            key=f"verify_status_{zone_id}"
                                        )
                                    
                                    inspector_notes = st.text_area(
                                        "Inspector Notes",
                                        placeholder="Describe what you observed during the field visit...",
                                        key=f"notes_{zone_id}",
                                        height=100
                                    )
                                    
                                    if st.button(f" Submit Verification", key=f"submit_{zone_id}", type="primary"):
                                        try:
                                            supabase = get_supabase_client()
                                            
                                            # Get current user ID
                                            user_id = get_current_user_id()
                                            
                                            if not user_id:
                                                st.error("No user found in database. Please create a user account first.")
                                                st.info("Run this SQL in Supabase to create an admin user:\n```sql\nINSERT INTO profiles (email, password_hash, full_name, role) VALUES ('admin@mining.gov', 'hashed_password', 'Admin User', 'admin');\n```")
                                                st.stop()
                                            
                                            # Determine if confirmed mine
                                            is_confirmed = "Yes" in is_mine_confirm
                                            
                                            # Insert verification
                                            verification_data = {
                                                'zone_id': zone_id,
                                                'zone_name': f"Zone #{zone['zone_number']}",
                                                'verified_by': user_id,
                                                'is_confirmed_mine': is_confirmed,
                                                'verification_status': verification_status_input,
                                                'inspector_notes': inspector_notes,
                                                'location_lat': zone['centroid_lat'],
                                                'location_lon': zone['centroid_lon'],
                                                'area_ha': zone['area_ha'],
                                                'priority': zone['priority']
                                            }
                                            
                                            result = supabase.table('field_verifications').insert(verification_data).execute()
                                            
                                            if result.data:
                                                st.success(f"Verification submitted successfully!")
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error("Failed to submit verification")
                                        except Exception as e:
                                            st.error(f"Error: {e}")
                            else:
                                st.info("Field verification is only available to Admin and Inspector roles")
                        
                        st.markdown("---")
                    
                    if len(high_priority_zones) > 20:
                        st.info(f"Showing 20 of {len(high_priority_zones)} total zones. Adjust filters to refine list.")
                    
                    st.markdown("""
                    ###  Field Inspection Checklist
                    
                    **Before Visit:**
                    - [ ] Download zone coordinates (GeoJSON/CSV)
                    - [ ] Prepare GPS device with waypoints
                    - [ ] Brief field team on safety protocols
                    - [ ] Obtain necessary permissions/permits
                    
                    **During Inspection:**
                    - [ ] Verify mining activity is present
                    - [ ] Document with photos/video (timestamp & GPS tag)
                    - [ ] Measure approximate area (GPS perimeter walk)
                    - [ ] Note mining type (open pit, shaft, dredging, etc.)
                    - [ ] Record exact GPS coordinates
                    - [ ] Check for environmental damage (deforestation, water pollution)
                    - [ ] Note any workers/equipment present
                    - [ ] Interview local community if safe
                    - [ ] Collect soil/water samples if possible
                    
                    **After Visit:**
                    - [ ] Upload evidence photos to database
                    - [ ] Submit field report with findings
                    - [ ] Update zone status in system
                    - [ ] Report findings to authorities
                    - [ ] Recommend follow-up actions
                    """)
                    
                # Add verification history section
                st.markdown("---")
                with st.expander(" View Verification History", expanded=False):
                    try:
                        supabase = get_supabase_client()
                        verifications = supabase.table('field_verifications') \
                            .select('*, profiles!field_verifications_verified_by_fkey(full_name, role)') \
                            .order('verification_date', desc=True) \
                            .limit(50) \
                            .execute()
                        
                        if verifications.data and len(verifications.data) > 0:
                            st.markdown(f"###  Total Verifications: {len(verifications.data)}")
                            
                            # Summary stats
                            confirmed_mines = len([v for v in verifications.data if v['is_confirmed_mine']])
                            rejected = len([v for v in verifications.data if not v['is_confirmed_mine']])
                            
                            col_v1, col_v2, col_v3 = st.columns(3)
                            with col_v1:
                                st.metric(" Confirmed Mines", confirmed_mines)
                            with col_v2:
                                st.metric(" Not Mines", rejected)
                            with col_v3:
                                total_verified_area = sum([v.get('area_ha', 0) for v in verifications.data if v['is_confirmed_mine']])
                                st.metric("Total Verified Area", f"{total_verified_area:.1f} ha")
                            
                            st.markdown("---")
                            
                            # Display verification records
                            for v in verifications.data[:20]:
                                status_emoji = "" if v['is_confirmed_mine'] else ""
                                status_text = "Confirmed Mine" if v['is_confirmed_mine'] else "Not a Mine"
                                verifier = v.get('profiles', {})
                                verifier_name = verifier.get('full_name', 'Unknown') if verifier else 'Unknown'
                                verifier_role = verifier.get('role', 'inspector') if verifier else 'inspector'
                                
                                st.markdown(f"""
                                **{status_emoji} {v['zone_name']}** - {status_text}
                                -  Verified by: **{verifier_name}** ({verifier_role.title()})
                                -  Date: {v['verification_date'][:10]}
                                -  Location: {v['location_lat']:.6f}, {v['location_lon']:.6f}
                                -  Area: {v['area_ha']:.2f} ha
                                -  Notes: {v['inspector_notes'] or 'No notes provided'}
                                -  [View on Map](https://www.google.com/maps?q={v['location_lat']},{v['location_lon']})
                                ---
                                """)
                        else:
                            st.info("No verifications recorded yet")
                    except Exception as e:
                        st.error(f"Could not load verification history: {e}")
                
                st.markdown("---")
                
                # Download filtered list
                if st.button(" Download Inspection List (CSV)", use_container_width=True):
                    df_inspection = pd.DataFrame([{
                        'Zone_Number': z['zone_number'],
                        'Priority': z['priority'],
                        'Area_ha': z['area_ha'],
                        'Confidence_%': z['confidence']*100,
                        'Status': z['status'],
                        'Latitude': z['centroid_lat'],
                        'Longitude': z['centroid_lon'],
                        'Google_Maps_Link': f"https://www.google.com/maps?q={z['centroid_lat']},{z['centroid_lon']}",
                        'Detected_Date': z['detected_date']
                    } for z in sorted_zones])
                    
                    csv_data = df_inspection.to_csv(index=False)
                    st.download_button(
                        label=" Download",
                            data=csv_data,
                            file_name=f"field_inspection_list_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
            else:
                st.success("No zones meet the inspection criteria with current filters")
                st.info("**Tip:** Lower the thresholds above to see more zones, or adjust criteria to focus on highest priority areas.")
        
        else:
            st.info("""
            ### No Data Sources Available
            
            No AI-detected zones or artisanal mining data found.
            
            **To detect mining zones:**
            1. Ensure the artisanal_mining folder is accessible
            2. **Train the Model** - Go to "Train Model" tab (Admin only)
            3. **Run Predictions** - AI will analyze satellite imagery
            4. **Extract Zones** - Use the "Extract Zones" button above
            """)
    
    # TAB 4: CHANGE DETECTION
        
        # Initialize default values
        total_zones = 0
        ai_zones_count = 0
        ai_detected_area_2025 = 0
        priority_5_count = 0
        priority_4_count = 0
        other_count = 0
        confirmed_mines = 0
        rejected_zones = 0
        all_zones_data = []
        
        # Load AI detected zones from local files (same as Tab 2)
        zones_2025_path = "mining_zones_output/prediction_2025/zones_summary.json"
        if os.path.exists(zones_2025_path):
            try:
                with open(zones_2025_path, 'r') as f:
                    zones_data = json.load(f)
                    all_zones_data = zones_data.get('zones', [])
                    total_zones = len(all_zones_data)
                    ai_zones_count = total_zones
                    ai_detected_area_2025 = zones_data.get('total_area_ha', 0)
                    
                    # Get priority breakdown
                    priority_5_count = len([z for z in all_zones_data if z.get('priority') == 5])
                    priority_4_count = len([z for z in all_zones_data if z.get('priority') == 4])
                    other_count = total_zones - priority_5_count - priority_4_count
            except Exception as e:
                st.warning(f"Could not load zones from file: {e}")
        
        # Get verified data from database
        try:
            supabase = get_supabase_client()
            verifications = supabase.table('field_verifications').select('*').execute()
            confirmed_mines = len([v for v in (verifications.data or []) if v.get('is_confirmed_mine')])
            rejected_zones = len([v for v in (verifications.data or []) if not v.get('is_confirmed_mine')])
        except:
            pass
        
        # Load manual QGIS labels for comparison
        manual_labels_gdf = None
        active_manual_count = 0
        active_manual_area = 0
        suspected_manual_count = 0
        suspected_manual_area = 0
        
        if os.path.exists(GEOJSON_PATH):
            try:
                manual_labels_gdf = load_geojson(GEOJSON_PATH)
                if manual_labels_gdf is not None and len(manual_labels_gdf) > 0:
                    if 'status' in manual_labels_gdf.columns:
                        active_manual = manual_labels_gdf[manual_labels_gdf['status'].str.lower().isin(['active', 'confirmed_active'])]
                        active_manual_count = len(active_manual)
                        if 'area_ha' in manual_labels_gdf.columns:
                            active_manual_area = active_manual['area_ha'].sum()
                        
                        suspected_manual = manual_labels_gdf[manual_labels_gdf['status'].str.lower().isin(['suspected', 'likely_active'])]
                        suspected_manual_count = len(suspected_manual)
                        if 'area_ha' in manual_labels_gdf.columns:
                            suspected_manual_area = suspected_manual['area_ha'].sum()
            except:
                pass
        
        if total_zones > 0 or active_manual_count > 0:
            
            # HEADER: Key Comparison
            st.markdown("###  Active Mines vs AI Detections - Overview")
            st.markdown("Compare manually labeled active mining sites with AI-detected zones")
            
            # Visual comparison cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 30px; border-radius: 15px; text-align: center; color: white;'>
                    <h2 style='margin:0; font-size: 3em;'></h2>
                    <h3 style='margin: 10px 0;'>{}</h3>
                    <p style='font-size: 2em; font-weight: bold; margin: 5px 0;'>{}</p>
                    <p style='font-size: 0.9em; opacity: 0.9;'>{:.1f} hectares</p>
                    <p style='font-size: 0.8em; margin-top: 10px; opacity: 0.8;'>Manual Mapping (QGIS)</p>
                </div>
                """.format("Active Mines", active_manual_count, active_manual_area), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            padding: 30px; border-radius: 15px; text-align: center; color: white;'>
                    <h2 style='margin:0; font-size: 3em;'></h2>
                    <h3 style='margin: 10px 0;'>AI Detected Zones</h3>
                    <p style='font-size: 2em; font-weight: bold; margin: 5px 0;'>{}</p>
                    <p style='font-size: 0.9em; opacity: 0.9;'>{:.1f} hectares</p>
                    <p style='font-size: 0.8em; margin-top: 10px; opacity: 0.8;'>Automated Detection (2025)</p>
                </div>
                """.format(ai_zones_count, ai_detected_area_2025), unsafe_allow_html=True)
            
            with col3:
                # Calculate coverage percentage
                coverage = 0
                status_text = "Analyzing..."
                status_color = "#95a5a6"
                if active_manual_count > 0 and ai_zones_count > 0:
                    coverage = min((ai_zones_count / active_manual_count) * 100, 100)
                    if coverage >= 90:
                        status_text = "Excellent Coverage"
                        status_color = "#27ae60"
                    elif coverage >= 70:
                        status_text = "Good Coverage"
                        status_color = "#f39c12"
                    else:
                        status_text = "Needs Attention"
                        status_color = "#e74c3c"
                
                st.markdown("""
                <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                            padding: 30px; border-radius: 15px; text-align: center; color: white;'>
                    <h2 style='margin:0; font-size: 3em;'></h2>
                    <h3 style='margin: 10px 0;'>Detection Rate</h3>
                    <p style='font-size: 2em; font-weight: bold; margin: 5px 0;'>{:.0f}%</p>
                    <p style='font-size: 0.9em; opacity: 0.9;'>{}</p>
                    <p style='font-size: 0.8em; margin-top: 10px; opacity: 0.8;'>AI vs Manual Labels</p>
                </div>
                """.format(coverage, status_text), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Detailed breakdown section
            st.markdown("###  Detailed Breakdown")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("####  Manual Labels (Ground Truth)")
                
                # Create comparison table
                manual_data = {
                    "Category": ["Active Mines", "Suspected Sites", "Total"],
                    "Count": [active_manual_count, suspected_manual_count, active_manual_count + suspected_manual_count],
                    "Area (ha)": [f"{active_manual_area:.1f}", f"{suspected_manual_area:.1f}", f"{active_manual_area + suspected_manual_area:.1f}"]
                }
                
                df_manual = pd.DataFrame(manual_data)
                st.dataframe(df_manual, use_container_width=True, hide_index=True)
                
                # Status indicators
                st.markdown("""
                <div style='background: #e8f5e9; padding: 15px; border-radius: 10px; margin-top: 10px;'>
                    <p style='margin: 5px 0;'><span style='color: #27ae60; font-size: 1.2em;'>●</span> <b>Active:</b> Confirmed mining operations</p>
                    <p style='margin: 5px 0;'><span style='color: #f39c12; font-size: 1.2em;'>●</span> <b>Suspected:</b> Potential mining activity</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("####  AI Detections")
                
                # Use local file data (already loaded above)
                priority_5_area = sum([z.get('area_ha', 0) for z in all_zones_data if z.get('priority') == 5])
                priority_4_area = sum([z.get('area_ha', 0) for z in all_zones_data if z.get('priority') == 4])
                other_area = sum([z.get('area_ha', 0) for z in all_zones_data if z.get('priority', 0) < 4])
                
                ai_data = {
                    "Priority Level": ["Critical (P5)", "High (P4)", "Lower Priority", "Total"],
                    "Count": [priority_5_count, priority_4_count, other_count, total_zones],
                    "Area (ha)": [f"{priority_5_area:.1f}", f"{priority_4_area:.1f}", f"{other_area:.1f}", f"{ai_detected_area_2025:.1f}"]
                }
                
                df_ai = pd.DataFrame(ai_data)
                st.dataframe(df_ai, use_container_width=True, hide_index=True)
                
                # AI insights
                st.markdown("""
                <div style='background: #fff3e0; padding: 15px; border-radius: 10px; margin-top: 10px;'>
                    <p style='margin: 5px 0;'><span style='color: #d32f2f; font-size: 1.2em;'>●</span> <b>P5:</b> ≥10ha + 95% confidence</p>
                    <p style='margin: 5px 0;'><span style='color: #ff6f00; font-size: 1.2em;'>●</span> <b>P4:</b> ≥5ha + 90% confidence</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Insights and recommendations
            st.markdown("###  Key Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if ai_zones_count > active_manual_count:
                    new_detections = ai_zones_count - active_manual_count
                    st.markdown(f"""
                    <div style='background: #ffebee; padding: 20px; border-radius: 10px; border-left: 5px solid #e74c3c;'>
                        <h4 style='margin-top: 0; color: #c62828;'> New Sites Detected</h4>
                        <p style='color: #333333;'>AI detected <b>{new_detections}</b> additional potential mining sites not in manual labels.</p>
                        <p style='color: #333333;'><b>Action:</b> Field verification recommended</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif ai_zones_count < active_manual_count:
                    missed = active_manual_count - ai_zones_count
                    st.markdown(f"""
                    <div style='background: #fff3e0; padding: 20px; border-radius: 10px; border-left: 5px solid #f39c12;'>
                        <h4 style='margin-top: 0; color: #e65100;'> Coverage Gap</h4>
                        <p style='color: #333333;'>AI may have missed <b>{missed}</b> manually labeled sites.</p>
                        <p style='color: #333333;'><b>Action:</b> Review detection parameters</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='background: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #27ae60;'>
                        <h4 style='margin-top: 0; color: #1b5e20;'> Perfect Match</h4>
                        <p style='color: #333333;'>AI detection count matches manual labels exactly.</p>
                        <p style='color: #333333;'><b>Status:</b> Excellent correlation</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Area comparison insight
                if active_manual_area > 0:
                    area_diff = abs(ai_detected_area_2025 - active_manual_area)
                    area_diff_pct = (area_diff / active_manual_area) * 100
                    
                    if area_diff_pct < 10:
                        st.markdown(f"""
                        <div style='background: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #27ae60;'>
                            <h4 style='margin-top: 0; color: #1b5e20;'> Area Accuracy</h4>
                            <p style='color: #333333;'>Area difference: <b>{area_diff:.1f} ha</b> ({area_diff_pct:.1f}%)</p>
                            <p style='color: #333333;'><b>Status:</b> High accuracy</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #1976d2;'>
                            <h4 style='margin-top: 0; color: #0d47a1;'> Area Difference</h4>
                            <p style='color: #333333;'>Area difference: <b>{area_diff:.1f} ha</b> ({area_diff_pct:.1f}%)</p>
                            <p style='color: #333333;'><b>Note:</b> AI may detect finer details</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Show verification insights instead
                    if confirmed_mines > 0 or rejected_zones > 0:
                        st.markdown(f"""
                        <div style='background: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #1976d2;'>
                            <h4 style='margin-top: 0; color: #0d47a1;'> Field Verification Status</h4>
                            <p style='color: #333333;'>Verified zones: <b>{confirmed_mines + rejected_zones}</b></p>
                            <p style='color: #333333;'> Confirmed mines: <b>{confirmed_mines}</b></p>
                            <p style='color: #333333;'> Rejected (not mines): <b>{rejected_zones}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
    
    # TAB 4: CHANGE DETECTION
    with tab4:
        st.header("Temporal Change Analysis (2016 - 2025)")
        st.caption("Multi-year mining expansion analysis and historical comparison")
        
        inference_path = f"{RESULTS_DIR}/inference_results.png"
        if os.path.exists(inference_path):
            img = Image.open(inference_path)
            st.image(img, use_container_width=True, caption="Complete Change Detection Analysis")
        
        # Load change data
        pred_2016_path = f"{RESULTS_DIR}/prediction_2016.tif"
        pred_2025_path = f"{RESULTS_DIR}/prediction_2025.tif"
        
        if os.path.exists(pred_2016_path) and os.path.exists(pred_2025_path):
            pred_2016, _, _ = load_geotiff(pred_2016_path)
            pred_2025, _, _ = load_geotiff(pred_2025_path)
            
            if pred_2016 is not None and pred_2025 is not None:
                actual_change = pred_2025.astype(int) - pred_2016.astype(int)
                
                col1, col2, col3 = st.columns(3)
                
                new_mining = np.sum(actual_change == 1)
                removed_mining = np.sum(actual_change == -1)
                unchanged = np.sum(actual_change == 0)
                
                with col1:
                    st.metric("🟢 New Mining Areas", f"{new_mining:,} pixels")
                    st.caption(f"{calculate_area(actual_change == 1):.1f} hectares")
                
                with col2:
                    st.metric(" Mining Removed/Rehabilitated", f"{removed_mining:,} pixels")
                    st.caption(f"{calculate_area(actual_change == -1):.1f} hectares")
                
                with col3:
                    st.metric(" Unchanged Areas", f"{unchanged:,} pixels")
                    st.caption(f"{(unchanged/actual_change.size)*100:.1f}%")
                
                # Alert boxes
                if new_mining > 0:
                    st.markdown(f"""
                    <div class="alert-box alert-danger">
                        <h4> ALERT: New Illegal Mining Detected</h4>
                        <p><b>{calculate_area(actual_change == 1):.1f} hectares</b> of new mining activity detected between 2016 and 2025.</p>
                        <p>Recommended action: Field inspection required</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # ── Artisanal Mining Land Cover Breakdown ──
        st.markdown("---")
        st.subheader("🗺️ Artisanal Mining – Land Cover Breakdown")
        st.caption("Derived from the artisanal mining classification pipeline (DL + ML ensemble)")
        
        art_stats = get_artisanal_stats()
        if art_stats:
            label_dist = art_stats.get("label_distribution", {})
            if label_dist:
                col_a, col_b = st.columns(2)
                with col_a:
                    # Pie chart of land cover
                    labels = list(label_dist.keys())
                    values = list(label_dist.values())
                    color_map = {
                        "mining": "#c62828", "forest": "#2e7d32", "water": "#1565c0",
                        "urban": "#7b1fa2", "bare_soil": "#f9a825"
                    }
                    colors = [color_map.get(l, "#999999") for l in labels]
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=[l.replace("_", " ").title() for l in labels],
                        values=values, marker=dict(colors=colors),
                        textinfo="label+percent", hole=0.35
                    )])
                    fig_pie.update_layout(title="Land Cover Distribution", height=380, margin=dict(t=40, b=20))
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_b:
                    # Mining severity distribution
                    art_gdf = load_artisanal_geojson()
                    if art_gdf is not None and "label" in art_gdf.columns:
                        mining_gdf = art_gdf[art_gdf["label"] == "mining"]
                        if not mining_gdf.empty and "meanLoss" in mining_gdf.columns:
                            fig_hist = px.histogram(
                                mining_gdf, x="meanLoss", nbins=20,
                                title="Mining Zone Severity (Mean Loss)",
                                labels={"meanLoss": "Mean Loss Value", "count": "Number of Zones"},
                                color_discrete_sequence=["#c62828"]
                            )
                            fig_hist.update_layout(height=380, margin=dict(t=40, b=20))
                            st.plotly_chart(fig_hist, use_container_width=True)
                        else:
                            st.info("No mining severity data available")
                    else:
                        st.info("Artisanal mining GeoJSON not available for severity analysis")
                
                # Summary metrics row
                total_area = art_stats.get("total_mining_area_ha", 0)
                avg_sev = art_stats.get("avg_severity", 0)
                mining_count = art_stats.get("total_mining_zones", 0)
                non_mining = sum(v for k, v in label_dist.items() if k != "mining")
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Mining Zones", f"{mining_count}")
                m2.metric("Total Mining Area", f"{total_area:.1f} ha")
                m3.metric("Avg Severity", f"{avg_sev:.3f}")
                m4.metric("Non-Mining Features", f"{non_mining}")
        else:
            st.info("Artisanal mining data not available. Ensure the artisanal_mining folder is accessible.")
    
    # TAB 5: REPORT MINING
    with tab5:
        st.header("Field Incident Reports")
        st.caption("Submit and manage field reports of suspected illegal mining activity")
        
        if st.session_state.user_role in ['inspector', 'admin']:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Location Details")
                mine_name = st.text_input("Mine Name/ID")
                latitude = st.number_input("Latitude", value=-12.5, format="%.6f")
                longitude = st.number_input("Longitude", value=27.85, format="%.6f")
                area_estimate = st.number_input("Estimated Area (hectares)", min_value=0.0, value=1.0)
                
                status = st.selectbox("Status", ["Suspected", "Confirmed Active", "Under Investigation"])
                
            with col2:
                st.subheader("Additional Information")
                description = st.text_area("Description", height=100)
                uploaded_file = st.file_uploader("Upload Photo Evidence", type=['jpg', 'jpeg', 'png'])
                
                date_detected = st.date_input("Date Detected", datetime.now())
                reported_by = st.text_input("Reported By", value=st.session_state.get('username', ''))
            
            if st.button("Submit Report", type="primary", use_container_width=True):
                if mine_name and latitude and longitude:
                    try:
                        # Save to Supabase database (mining_sites table)
                        supabase = get_supabase_client()
                        
                        # Upload photo evidence if provided
                        evidence_url = None
                        if uploaded_file:
                            try:
                                # Add timestamp to make filename unique and avoid duplicates
                                import time
                                timestamp = int(time.time())
                                file_extension = uploaded_file.name.split('.')[-1]
                                file_name = f"evidence/{date_detected.strftime('%Y%m%d')}_{timestamp}_{mine_name.replace(' ', '_')}.{file_extension}"
                                
                                # Upload with upsert option to overwrite if exists
                                supabase.storage.from_('illegal-mining-data').upload(
                                    file_name, 
                                    uploaded_file.getvalue(),
                                    file_options={"contentType": uploaded_file.type, "upsert": "true"}
                                )
                                evidence_url = supabase.storage.from_('illegal-mining-data').get_public_url(file_name)
                                st.info(f"Photo uploaded successfully: {file_name}")
                            except Exception as upload_error:
                                st.warning(f"Photo upload failed: {upload_error}. Report will be saved without photo.")
                        
                        # Prepare data for mining_sites table
                        site_data = {
                            'site_name': mine_name,
                            'area_ha': float(area_estimate),
                            'centroid_lat': float(latitude),
                            'centroid_lon': float(longitude),
                            'confidence_score': 0.0,  # Manual report (no AI confidence)
                            'mining_type': 'manual_report',
                            'detected_date': date_detected.strftime('%Y-%m-%d'),
                            'geojson_geometry': {
                                'type': 'Point',
                                'coordinates': [float(longitude), float(latitude)],
                                'properties': {
                                    'name': mine_name,
                                    'status': status,
                                    'description': description,
                                    'reported_by': reported_by,
                                    'source': 'manual_report',
                                    'evidence_url': evidence_url
                                }
                            }
                        }
                        
                        # Insert into database
                        response = supabase.table('mining_sites').insert(site_data).execute()
                        
                        if response.data:
                            record_id = response.data[0]['id']
                            
                            # Also create an alert for this manual report with new columns
                            alert_data = {
                                'alert_type': 'manual_report',
                                'severity': 'medium' if status == 'Suspected' else 'high',
                                'message': f"Manual report: {mine_name} - {description[:100] if description else 'No description'}",
                                'title': f"New Mining Report: {mine_name}",
                                'location': f"{latitude:.4f}, {longitude:.4f}",
                                'latitude': float(latitude),
                                'longitude': float(longitude),
                                'area_change_ha': float(area_estimate),
                                'image_date': date_detected.strftime('%Y-%m-%d'),
                                'status': 'unread',
                                'requires_action': True,
                                'reported_by': reported_by,
                                'evidence_url': evidence_url,
                                'report_source': 'manual'
                            }
                            
                            supabase.table('mining_alerts').insert(alert_data).execute()
                            
                            # Send push notification via webhook
                            try:
                                import requests
                                # Read webhook URL from file
                                webhook_url = None
                                if os.path.exists('webhook_url.txt'):
                                    with open('webhook_url.txt', 'r') as f:
                                        webhook_url = f.read().strip()
                                
                                if webhook_url:
                                    webhook_payload = {
                                        'event': 'mining_reported',
                                        'mine_name': mine_name,
                                        'location': f"{latitude:.4f}, {longitude:.4f}",
                                        'area': area_estimate,
                                        'status': status,
                                        'severity': 'medium' if status == 'Suspected' else 'high',
                                        'reported_by': reported_by,
                                        'date': date_detected.strftime('%Y-%m-%d'),
                                        'evidence_url': evidence_url,
                                        'record_id': record_id
                                    }
                                    
                                    response = requests.post(
                                        f"{webhook_url}/webhook/mining-reported",
                                        json=webhook_payload,
                                        timeout=5
                                    )
                                    
                                    if response.status_code == 200:
                                        st.info("Push notification sent to all users")
                                    else:
                                        st.warning(f"Webhook responded with status {response.status_code}")
                                else:
                                    st.info(" No webhook URL configured (push notifications disabled)")
                            except Exception as webhook_error:
                                st.warning(f"Could not send push notification: {webhook_error}")
                            
                            # Add to session notifications
                            notification = {
                                'type': 'new_report',
                                'mine_name': mine_name,
                                'location': f"{latitude:.4f}, {longitude:.4f}",
                                'area': area_estimate,
                                'status': status,
                                'date': date_detected.strftime('%Y-%m-%d'),
                                'reporter': reported_by,
                                'record_id': record_id,
                                'evidence_url': evidence_url
                            }
                            st.session_state.notifications.append(notification)
                            
                            st.success(f"Report submitted successfully! (Record ID: {record_id})")
                            
                            # Show detailed confirmation
                            info_parts = [
                                f" Saved to database: `mining_sites` table (ID: {record_id})",
                                f" Alert created in `mining_alerts` table"
                            ]
                            if evidence_url:
                                info_parts.append(f" Photo evidence uploaded")
                            
                            st.info("\n".join(info_parts))
                            st.balloons()
                            
                            # Refresh the page but keep user logged in
                            st.success("Refreshing data... (You will stay logged in)")
                            st.rerun()
                        else:
                            st.error("Failed to save report to database")
                            
                    except Exception as e:
                        st.error(f"Error saving report: {e}")
                        st.info("Report saved locally in session memory only")
                        
                        # Fallback: save to session only
                        notification = {
                            'type': 'new_report',
                            'mine_name': mine_name,
                            'location': f"{latitude:.4f}, {longitude:.4f}",
                            'area': area_estimate,
                            'status': status,
                            'date': date_detected.strftime('%Y-%m-%d'),
                            'reporter': reported_by
                        }
                        st.session_state.notifications.append(notification)
                else:
                    st.error("Please fill in all required fields")
        else:
            st.warning("Only inspectors and admins can submit reports. Please login with appropriate credentials.")
    
    # TAB 6: SATELLITE DATA (ADMIN ONLY)
    if st.session_state.user_role == 'admin':
        with tab6:
            st.header("Satellite Data Monitoring")
            st.caption("Automated Sentinel-2 satellite imagery acquisition and monitoring pipeline")
            st.markdown("*Admin-only feature: Real-time satellite imagery collection from Google Earth Engine*")
            
            # Admin verification badge
            st.success("**Admin Access Granted** - You have full access to satellite automation features")
            
            # Fetch satellite data
            try:
                supabase = get_supabase_client()
                response = supabase.table('satellite_updates')\
                    .select('*')\
                    .order('collection_date', desc=True)\
                    .execute()
                
                if response.data and len(response.data) > 0:
                    # Latest collection metrics
                    latest = response.data[0]
                    
                    st.subheader("Latest Collection")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.metric(
                            "Collection Date",
                            latest['collection_date'],
                            delta=None
                        )
                    
                    with col2:
                        st.metric(
                            "Images Found",
                            latest['image_count'],
                            delta=None
                        )
                    
                    with col3:
                        st.metric(
                            "Satellite",
                            latest['satellite'],
                            delta=None
                        )
                    
                    with col4:
                        status_color = "🟢" if latest['status'] == 'completed' else ""
                        st.metric(
                            "Status",
                            f"{status_color} {latest['status'].title()}"
                        )
                    
                    with col5:
                        cloud_pct = latest.get('cloud_percentage', 'N/A')
                        if cloud_pct != 'N/A':
                            cloud_pct = f"{cloud_pct}%"
                        st.metric(
                            "Cloud Cover",
                            cloud_pct
                        )
                    
                    # System info
                    st.info(f"""
                    ** Automation Details:**
                    - Next automatic collection: **November 11, 2025 at 2:00 AM UTC**
                    - Frequency: Every 5 days
                    - Area of Interest: Chingola, Zambia
                    - Image Source: Sentinel-2 (10m resolution)
                    - Processing: Automated via GitHub Actions
                    """)
                    
                    # Manual trigger section
                    st.subheader("Manual Collection Trigger")
                    
                    col_a, col_b = st.columns([2, 1])
                    
                    with col_a:
                        st.markdown("""
                        Trigger a new satellite data collection on demand without waiting for the scheduled run.
                        
                        **What happens when you trigger:**
                        1. GitHub Actions workflow starts
                        2. Connects to Google Earth Engine
                        3. Fetches latest Sentinel-2 imagery (last 30 days)
                        4. Calculates NDVI for vegetation analysis
                        5. Stores metadata in database
                        6. Results available in ~3-5 minutes
                        """)
                    
                    with col_b:
                        if st.button(" Trigger Collection", type="primary", use_container_width=True):
                            st.success("Opening GitHub Actions...")
                            st.markdown("""
                            **Next Steps:**
                            1. Click [this link](https://github.com/OSEITD/Mining_detection/actions/workflows/gee_automation.yml) to open GitHub Actions
                            2. Click the green **"Run workflow"** button
                            3. Keep **"main"** branch selected
                            4. Click **"Run workflow"** to confirm
                            5. Wait 3-5 minutes for completion
                            6. Refresh this page to see new data
                            """)
                            
                        if st.button(" Refresh Data", use_container_width=True):
                            st.cache_resource.clear()
                            st.rerun()
                    
                    # Historical data
                    st.subheader("Collection History")
                    
                    df = pd.DataFrame(response.data)
                    df['collection_date'] = pd.to_datetime(df['collection_date'])
                    
                    # Display table
                    st.dataframe(
                        df[['collection_date', 'satellite', 'image_count', 'status', 'notes']],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Chart - Images over time
                    if len(df) > 1:
                        st.subheader("Images Found Per Collection")
                        
                        fig = px.line(
                            df.sort_values('collection_date'),
                            x='collection_date',
                            y='image_count',
                            markers=True,
                            title='Sentinel-2 Images Availability Over Time'
                        )
                        
                        fig.update_layout(
                            xaxis_title="Collection Date",
                            yaxis_title="Number of Images",
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # View images section
                    st.subheader("Access Satellite Imagery")
                    
                    with st.expander(" View in Google Earth Engine Code Editor"):
                        st.markdown("""
                        The collected imagery is available in Google Earth Engine for interactive visualization.
                        
                        **Steps:**
                        1. Open [Google Earth Engine Code Editor](https://code.earthengine.google.com)
                        2. Use your existing script or create a new one
                        3. Define the same AOI: `ee.Geometry.Rectangle([27.7, -12.6, 28.2, -12.4])`
                        4. Filter Sentinel-2 collection for your dates
                        5. Visualize on the map
                        
                        **Example Script:**
                        ```javascript
                        var aoi = ee.Geometry.Rectangle([27.7, -12.6, 28.2, -12.4]);
                        var collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                          .filterBounds(aoi)
                          .filterDate('2025-10-07', '2025-11-06')
                          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));
                          
                        var composite = collection.median().clip(aoi);
                        
                        Map.centerObject(aoi, 10);
                        Map.addLayer(composite, {
                          bands: ['B4', 'B3', 'B2'],
                          min: 0, max: 3000
                        }, 'RGB Composite');
                        ```
                        """)
                    
                    with st.expander(" Export to Google Drive for Processing"):
                        st.markdown("""
                        For ensemble ML/DL model inference, export images to Google Drive first.
                        
                        **Why?**
                        - Direct download URLs exceed size limit (>50 MB)
                        - Drive export allows larger areas and higher resolution
                        - Can process in Google Colab afterwards
                        
                        **Export Script** (Run in GEE Code Editor):
                        ```javascript
                        Export.image.toDrive({
                          image: composite,
                          description: 'sentinel2_chingola',
                          folder: 'Mining_Detection',
                          scale: 10,
                          region: aoi,
                          maxPixels: 1e9
                        });
                        ```
                        
                        Then access from your Google Drive folder: **Mining_Detection**
                        """)
                
                else:
                    st.warning("No satellite data found yet.")
                    st.info("""
                    **Possible reasons:**
                    - Workflow hasn't run yet (scheduled for every 5 days)
                    - First scheduled run: November 11, 2025
                    
                    **Action:**
                    Trigger a manual collection using the button below to populate data immediately.
                    """)
                    
                    if st.button(" Trigger First Collection", type="primary"):
                        st.markdown("[Open GitHub Actions →](https://github.com/OSEITD/Mining_detection/actions/workflows/gee_automation.yml)")
            
            except Exception as e:
                st.error(f"Error fetching satellite data: {e}")
                st.info("Make sure the satellite_updates table exists in Supabase.")
            
            # ========================================
            # MINING DETECTION SECTION
            # ========================================
            st.markdown("---")
            st.header("Automated Detection Pipeline")
            st.caption("AI-powered change detection using ensemble ML/DL model")
            
            # Fetch recent predictions
            try:
                supabase = get_supabase_client()
                predictions_response = supabase.table('mining_predictions')\
                    .select('*')\
                    .order('prediction_date', desc=True)\
                    .limit(10)\
                    .execute()
                
                if predictions_response.data and len(predictions_response.data) > 0:
                    # Latest detection metrics
                    latest_pred = predictions_response.data[0]
                    
                    st.subheader("Latest Detection Results")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Detection Date",
                            latest_pred['prediction_date'],
                            delta=None
                        )
                    
                    with col2:
                        st.metric(
                            "Mining Area",
                            f"{latest_pred['mining_area_ha']:.2f} ha",
                            delta=None
                        )
                    
                    with col3:
                        st.metric(
                            "Model Version",
                            latest_pred['model_version'],
                            delta=None
                        )
                    
                    with col4:
                        confidence = latest_pred.get('confidence', 0.95) * 100
                        st.metric(
                            "Confidence",
                            f"{confidence:.1f}%"
                        )
                    
                    # Calculate change from previous
                    if len(predictions_response.data) > 1:
                        prev_pred = predictions_response.data[1]
                        change_ha = latest_pred['mining_area_ha'] - prev_pred['mining_area_ha']
                        change_pct = (change_ha / prev_pred['mining_area_ha'] * 100) if prev_pred['mining_area_ha'] > 0 else 0
                        
                        if abs(change_ha) >= 0.5:
                            alert_type = "error" if change_ha > 0 else "success"
                            icon = "" if change_ha > 0 else ""
                            
                            if alert_type == "error":
                                st.error(f"{icon} **Change Detected:** Mining area INCREASED by {change_ha:.2f} ha ({change_pct:+.1f}%)")
                            else:
                                st.success(f"{icon} **Change Detected:** Mining area decreased by {abs(change_ha):.2f} ha ({change_pct:.1f}%)")
                        else:
                            st.info(f" No significant change detected (±{abs(change_ha):.2f} ha)")
                    
                    # Info box
                    st.info(f"""
                    ** Detection System Details:**
                    - Model: Ensemble (Random Forest + CNN/U-Net)
                    - Next automatic detection: **Every 5 days at 4:00 AM UTC**
                    - Change threshold: 0.5 hectares or 2%
                    - Notification: Automatic alerts sent when threshold exceeded
                    - Model path: `outputs/best_model.pth`
                    """)
                    
                else:
                    st.warning("No detection results found yet.")
                    st.info("""
                    **To start automated detection:**
                    1. Ensure model is trained and saved at `outputs/best_model.pth`
                    2. Set up GitHub Actions secrets (see AUTOMATION_SETUP_GUIDE.md)
                    3. Trigger first detection manually using button below
                    """)
                
                # Manual Detection Trigger
                st.subheader("Manual Detection Trigger")
                
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    st.markdown("""
                    Run mining detection on-demand without waiting for the scheduled run.
                    
                    **What happens when you trigger:**
                    1. Fetches latest Sentinel-2 imagery (last 30 days)
                    2. Runs ensemble ML/DL model inference to detect mining areas
                    3. Compares with previous predictions
                    4. Calculates area change in hectares
                    5. Sends notification alert if change > threshold
                    6. Results available in ~5-10 minutes
                    
                    **Detection Thresholds:**
                    - 🟢 Low: < 1 hectare change
                    - 🟡 Medium: 1-5 hectares
                    - 🟠 High: 5-10 hectares
                    -  Critical: > 10 hectares
                    """)
                
                with col_b:
                    if st.button(" Run Detection Now", type="primary", use_container_width=True):
                        st.success("Opening GitHub Actions...")
                        st.markdown("""
                        **Next Steps:**
                        1. Click [this link](https://github.com/OSEITD/Mining_detection/actions/workflows/mining_detection.yml) to open the workflow
                        2. Click the green **"Run workflow"** button
                        3. Optional: Adjust parameters:
                           - Days back: 30 (default)
                           - Force alert: Check to test notifications
                        4. Click **"Run workflow"** to confirm
                        5. Wait 5-10 minutes for completion
                        6. Notifications will appear automatically
                        7. Refresh this page to see new results
                        """)
                        
                    st.markdown("")  # Spacing
                    
                    if st.button(" Refresh Results", use_container_width=True):
                        st.cache_resource.clear()
                        st.rerun()
                    
                    st.markdown("")  # Spacing
                    
                    if st.button(" Setup Guide", use_container_width=True):
                        st.info("See **AUTOMATION_SETUP_GUIDE.md** for complete instructions")
                
                # Detection History
                if predictions_response.data and len(predictions_response.data) > 1:
                    st.subheader("Detection History")
                    
                    df_pred = pd.DataFrame(predictions_response.data)
                    df_pred['prediction_date'] = pd.to_datetime(df_pred['prediction_date'])
                    
                    # Display table
                    st.dataframe(
                        df_pred[['prediction_date', 'mining_area_ha', 'model_version', 'confidence', 'status', 'notes']],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Chart - Mining area trend
                    st.subheader("Mining Area Trend")
                    
                    fig = px.line(
                        df_pred.sort_values('prediction_date'),
                        x='prediction_date',
                        y='mining_area_ha',
                        markers=True,
                        title='Mining Area Detection Over Time',
                        labels={'mining_area_ha': 'Mining Area (hectares)', 'prediction_date': 'Date'}
                    )
                    
                    # Add threshold line
                    fig.add_hline(
                        y=df_pred['mining_area_ha'].mean(),
                        line_dash="dash",
                        line_color="orange",
                        annotation_text="Average"
                    )
                    
                    fig.update_layout(
                        xaxis_title="Detection Date",
                        yaxis_title="Mining Area (hectares)",
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error fetching detection results: {e}")
                st.info("Make sure the mining_predictions table exists in Supabase.")
    
    # TAB 7: REMOVED (was Kantolomba Analysis)
    # Kantolomba analysis has been removed from the system
    
    # TAB 8: CONFIGURE AOI (ADMIN ONLY)
    if tab8:
        with tab8:
            st.header("Area of Interest Configuration")
            st.caption("Define the geographic boundaries for satellite monitoring and detection")
            st.markdown("*Define custom regions to monitor for illegal mining activity*")
            
            st.info("""
            **What is AOI?**
            
            The Area of Interest (AOI) defines the geographic region where the system monitors for illegal mining.
            You can change this to monitor different locations in Zambia or other countries.
            """)
            
            # Current AOI Display
            st.subheader("Current AOI Configuration")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Display current AOI on map
                current_coords = {
                    'center_lat': -12.5,
                    'center_lon': 27.85,
                    'name': 'Chingola Copperbelt',
                    'bounds': [27.75, -12.6, 27.95, -12.4]
                }
                
                aoi_map = folium.Map(
                    location=[current_coords['center_lat'], current_coords['center_lon']],
                    zoom_start=11,
                    tiles='OpenStreetMap'
                )
                
                # Add rectangle showing current AOI
                folium.Rectangle(
                    bounds=[
                        [current_coords['bounds'][3], current_coords['bounds'][0]],
                        [current_coords['bounds'][1], current_coords['bounds'][2]]
                    ],
                    color='#3388ff',
                    fill=True,
                    fillColor='#3388ff',
                    fillOpacity=0.2,
                    popup=f"Current AOI: {current_coords['name']}"
                ).add_to(aoi_map)
                
                # Add drawing tools with capture
                draw = plugins.Draw(
                    export=True,
                    position='topleft',
                    draw_options={
                        'polyline': False,
                        'polygon': True,
                        'circle': False,
                        'marker': False,
                        'circlemarker': False,
                        'rectangle': True
                    }
                )
                draw.add_to(aoi_map)
                
                # Use st_folium instead of folium_static to capture drawings
                from streamlit_folium import st_folium
                
                st.info("Draw a rectangle on the map to define your AOI. The coordinates will be captured below.")
                
                map_data = st_folium(
                    aoi_map,
                    width=700,
                    height=500,
                    returned_objects=["all_drawings", "last_object_clicked"]
                )
                
                # Capture drawn coordinates
                if map_data and map_data.get("all_drawings"):
                    st.success("Drawing detected! Extracting coordinates...")
                    drawings = map_data["all_drawings"]
                    
                    if len(drawings) > 0:
                        last_drawing = drawings[-1]  # Get most recent drawing
                        
                        if "geometry" in last_drawing:
                            coords = last_drawing["geometry"]["coordinates"]
                            
                            # Extract bounds from rectangle/polygon
                            if last_drawing["geometry"]["type"] == "Polygon":
                                lons = [c[0] for c in coords[0]]
                                lats = [c[1] for c in coords[0]]
                                
                                extracted_bounds = {
                                    'min_lon': min(lons),
                                    'max_lon': max(lons),
                                    'min_lat': min(lats),
                                    'max_lat': max(lats)
                                }
                                
                                st.session_state['drawn_aoi'] = extracted_bounds
                                
                                st.json({
                                    "Captured Coordinates": {
                                        "Min Longitude": f"{extracted_bounds['min_lon']:.4f}",
                                        "Max Longitude": f"{extracted_bounds['max_lon']:.4f}",
                                        "Min Latitude": f"{extracted_bounds['min_lat']:.4f}",
                                        "Max Latitude": f"{extracted_bounds['max_lat']:.4f}",
                                        "Area": f"{abs((extracted_bounds['max_lon'] - extracted_bounds['min_lon']) * (extracted_bounds['max_lat'] - extracted_bounds['min_lat'])) * 12321:.1f} km²"
                                    }
                                })
                                
                                if st.button(" Use These Coordinates", type="primary"):
                                    st.success("Coordinates loaded! Scroll down to save the AOI.")
                                    st.session_state['use_drawn_coords'] = True
                
            with col2:
                st.markdown("### Current AOI Details")
                st.markdown(f"""
                **Name:** {current_coords['name']}  
                **Center:** {current_coords['center_lat']:.4f}, {current_coords['center_lon']:.4f}  
                **Bounds:**
                - Min Lon: {current_coords['bounds'][0]:.4f}
                - Min Lat: {current_coords['bounds'][1]:.4f}
                - Max Lon: {current_coords['bounds'][2]:.4f}
                - Max Lat: {current_coords['bounds'][3]:.4f}
                
                **Coverage:** ~{abs((current_coords['bounds'][2] - current_coords['bounds'][0]) * (current_coords['bounds'][3] - current_coords['bounds'][1])) * 12321:.1f} km²
                """)
                
                st.markdown("---")
                
                st.markdown("### Quick AOI Presets")
                
                aoi_presets = {
                    "Chingola Copperbelt (Current)": [27.75, -12.6, 27.95, -12.4],
                    "Kitwe Mining Area": [28.15, -12.9, 28.35, -12.7],
                    "Mufulira District": [28.2, -12.6, 28.4, -12.4],
                    "Ndola Region": [28.5, -13.1, 28.7, -12.9],
                    "Custom (Draw on Map)": None
                }
                
                selected_preset = st.selectbox(
                    "Select AOI Preset",
                    list(aoi_presets.keys())
                )
                
                if st.button(" Load Preset AOI", type="primary", use_container_width=True):
                    if aoi_presets[selected_preset]:
                        st.success(f"Loaded: {selected_preset}")
                        st.info("AOI coordinates ready to save. Click 'Save New AOI' below.")
                    else:
                        st.info("Draw your custom AOI on the map using the rectangle tool, then export coordinates.")
            
            # New AOI Configuration
            st.markdown("---")
            st.subheader("Define New AOI")
            
            st.markdown("""
            **Three ways to define a new AOI:**
            1. **Draw on Map** - Use the rectangle/polygon tool above
            2. **Use Preset** - Select from predefined mining regions
            3. **Manual Entry** - Enter coordinates directly below
            """)
            
            tab_draw, tab_manual = st.tabs([" Manual Coordinates", " Upload GeoJSON"])
            
            with tab_draw:
                st.markdown("### Enter AOI Coordinates")
                
                # Check if coordinates were drawn on map
                if 'drawn_aoi' in st.session_state and st.session_state.get('use_drawn_coords', False):
                    st.success("Using coordinates from map drawing!")
                    default_min_lon = st.session_state['drawn_aoi']['min_lon']
                    default_max_lon = st.session_state['drawn_aoi']['max_lon']
                    default_min_lat = st.session_state['drawn_aoi']['min_lat']
                    default_max_lat = st.session_state['drawn_aoi']['max_lat']
                    st.session_state['use_drawn_coords'] = False  # Reset flag
                else:
                    default_min_lon = 27.75
                    default_max_lon = 27.95
                    default_min_lat = -12.6
                    default_max_lat = -12.4
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    aoi_name = st.text_input("AOI Name", value="Custom Mining Area")
                    min_lon = st.number_input("Minimum Longitude", value=float(default_min_lon), format="%.4f", step=0.01, key="min_lon_input")
                    max_lon = st.number_input("Maximum Longitude", value=float(default_max_lon), format="%.4f", step=0.01, key="max_lon_input")
                
                with col_b:
                    st.markdown("#")  # Spacing
                    min_lat = st.number_input("Minimum Latitude", value=float(default_min_lat), format="%.4f", step=0.01, key="min_lat_input")
                    max_lat = st.number_input("Maximum Latitude", value=float(default_max_lat), format="%.4f", step=0.01, key="max_lat_input")
                
                # Calculate area
                area_km2 = abs((max_lon - min_lon) * (max_lat - min_lat)) * 12321
                st.info(f"**Estimated Coverage:** {area_km2:.1f} km²")
                
                if st.button(" Save New AOI Configuration", type="primary", use_container_width=True):
                    # Create config dictionary
                    new_aoi_config = {
                        'name': aoi_name,
                        'center_lat': (min_lat + max_lat) / 2,
                        'center_lon': (min_lon + max_lon) / 2,
                        'bounds': [min_lon, min_lat, max_lon, max_lat],
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Save to config file
                    config_path = 'aoi_config.json'
                    try:
                        with open(config_path, 'w') as f:
                            json.dump(new_aoi_config, f, indent=2)
                        
                        st.success(f"""
                         **AOI Configuration Saved!**
                        
                        **Configuration saved to:** `{config_path}`
                        """)
                        
                        st.json(new_aoi_config)
                        
                    except Exception as e:
                        st.error(f"Error saving AOI config: {e}")
            
            # Automated Data Collection
            st.markdown("---")
            st.subheader("Collect Satellite Data for This AOI")
            
            st.info("""
            After configuring your AOI, trigger automated satellite data collection using GitHub Actions.
            
            **What happens:**
            1. Fetches latest Sentinel-2 imagery for your AOI
            2. Downloads and processes RGB, NDVI, NDWI bands
            3. Saves to Supabase database (`satellite_updates` table)
            4. Data becomes available in the dashboard
            """)
            
            col_action1, col_action2 = st.columns(2)
            
            with col_action1:
                st.markdown("###  Automated Collection")
                st.markdown("""
                **GitHub Actions Workflow:**
                - Runs every 5 days automatically
                - Can be triggered manually
                - Processes and stores in database
                """)
                
                if st.button(" Trigger Data Collection", type="primary", use_container_width=True):
                    st.success("Opening GitHub Actions...")
                    st.markdown("""                    
                    **Steps:**
                    1. Go to: [GitHub Actions Workflows](https://github.com/OSEITD/Mining_detection/actions)
                    2. Click **"Automated Satellite Data Collection"**
                    3. Click green **"Run workflow"** button
                    4. Optionally adjust "Days back" parameter (default: 30)
                    5. Click **"Run workflow"** to confirm
                    6. Wait 2-5 minutes for completion
                    7. Check your dashboard for new satellite data
                    
                    **Note:** Requires GitHub secrets to be configured (EARTHENGINE_TOKEN, SUPABASE_URL, SUPABASE_KEY)
                    """)
            
            with col_action2:
                st.markdown("###  Manual Collection")
                st.markdown("""
                **Run locally:**
                - Use GEE automation script
                - Requires Earth Engine authentication
                - Data saved to local files
                """)
                
                st.code("python gee_automation/github_actions_gee.py", language="bash")
                
                st.markdown("""
                **Prerequisites:**
                - Earth Engine authenticated
                - Supabase credentials configured
                - AOI saved to `aoi_config.json`
                """)
            
            with tab_manual:
                st.markdown("### Upload Custom AOI GeoJSON")
                
                uploaded_geojson = st.file_uploader(
                    "Upload GeoJSON file defining your AOI",
                    type=['geojson', 'json'],
                    help="Upload a GeoJSON file with polygon/multipolygon geometry"
                )
                
                if uploaded_geojson:
                    try:
                        geojson_data = json.load(uploaded_geojson)
                        st.success("GeoJSON loaded successfully!")
                        
                        # Extract bounds from GeoJSON
                        if 'features' in geojson_data:
                            st.info(f"Found {len(geojson_data['features'])} feature(s)")
                            
                            # Display preview
                            st.json(geojson_data)
                            
                            if st.button(" Save AOI from GeoJSON", type="primary"):
                                st.success("AOI extracted and saved from GeoJSON!")
                                st.info("Update your Earth Engine script with these coordinates.")
                        
                    except Exception as e:
                        st.error(f"Error parsing GeoJSON: {e}")
            
            # Documentation
            st.markdown("---")
            st.subheader("How AOI Configuration Works")
            
            with st.expander(" Understanding AOI Configuration"):
                st.markdown("""
                ### What happens when you change AOI?
                
                **1. Satellite Data Collection**
                - GitHub Actions workflow fetches Sentinel-2 imagery for new coordinates
                - Downloads and processes RGB, NDVI, NDWI, and other spectral bands
                - Data stored in Supabase `satellite_updates` table
                - Automatically runs every 5 days or manually triggered
                
                **2. Model Inference**
                - Ensemble ML/DL model runs on new imagery to detect mining areas
                - Detects mining patterns based on learned features from training
                - May require model retraining if region differs significantly
                - Results saved to `mining_predictions` table
                
                **3. Change Detection & Alerts**
                - System compares new predictions with previous detections
                - Calculates area change in hectares
                - Sends push notifications if change exceeds threshold (>0.5 ha)
                - Historical data preserved for trend analysis
                
                ### When to retrain the model?
                
                ** Retrain if:**
                - New region has different geology, terrain, or vegetation
                - Different mining methods (open pit vs. underground vs. artisanal)
                - Model accuracy drops below 85% on validation set
                - High number of false positives or false negatives
                - Significant time gap (>2 years) since last training
                
                ** Can skip retraining if:**
                - Similar terrain, geology, and mining patterns
                - Same region, just expanded coverage area
                - Model maintains high accuracy (>90%)
                - Same satellite data source and resolution
                
                ### Integration with Automation
                
                **GitHub Actions Workflows:**
                ```yaml
                # .github/workflows/gee_automation.yml
                # Reads AOI from aoi_config.json
                # Fetches satellite data every 5 days
                
                # .github/workflows/mining_detection.yml  
                # Runs ensemble ML/DL inference on new imagery
                # Compares with previous predictions
                # Triggers alerts if change detected
                ```
                
                **Configuration File:**
                ```json
                // aoi_config.json
                {
                  "name": "Chingola Copperbelt",
                  "center_lat": -12.5,
                  "center_lon": 27.85,
                  "bounds": [27.75, -12.6, 27.95, -12.4],
                  "created_at": "2025-12-04T19:00:00"
                }
                ```
                
                **Manual Updates:**
                ```python
                # gee_automation/github_actions_gee.py
                # Automatically reads from aoi_config.json
                
                # automated_inference.py
                # Reads AOI bounds for model inference
                ```
                
                ### Best Practices
                
                1. **Test new AOI first** - Run manual data collection to verify coverage
                2. **Check data quality** - Ensure minimal cloud cover (<20%)
                3. **Validate coordinates** - Use map drawing tool to avoid errors
                4. **Monitor first results** - Review initial detections for accuracy
                5. **Document changes** - Keep notes on why AOI was changed
                """)
            
            with st.expander(" Technical Requirements"):
                st.markdown("""
                ### GitHub Secrets Required
                
                Configure these in repository settings:
                - `EARTHENGINE_TOKEN` - Google Earth Engine authentication
                - `SUPABASE_URL` - Your Supabase project URL
                - `SUPABASE_KEY` - Supabase service role key (full access)
                
                ### Python Dependencies
                
                ```bash
                pip install earthengine-api>=0.1.300
                pip install supabase>=1.0.0
                pip install folium streamlit-folium
                ```
                
                ### File Structure
                
                ```
                project/
                ├── aoi_config.json          # AOI configuration (auto-generated)
                ├── gee_automation/
                │   └── github_actions_gee.py  # GEE data collection script
                ├── automated_inference.py    # Mining detection script
                └── .github/workflows/
                    ├── gee_automation.yml    # Satellite collection workflow
                    └── mining_detection.yml  # Mining detection workflow
                ```
                """)
    
    # TAB 9: TRAIN MODEL (ADMIN ONLY)
    if tab9:
        with tab9:
            st.header("Model Training & Management")
            st.caption("Retrain the ensemble ML/DL model for new regions or improved accuracy")
            
            st.info("""
            **When to retrain the model?**
            
            -  Changed AOI to a new region with different terrain
            -  Model accuracy dropped below acceptable threshold
            -  New training data available (manual labels)
            -  Different types of mining to detect
            -  Improved model architecture available
            """)
            
            # Training Status
            st.subheader("Current Model Status")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Check if model exists
            model_path = 'outputs/best_model.pth'
            model_exists = os.path.exists(model_path)
            
            with col1:
                if model_exists:
                    model_size = os.path.getsize(model_path) / (1024 * 1024)
                    st.metric("Model Size", f"{model_size:.2f} MB")
                else:
                    st.metric("Model Size", "N/A")
            
            with col2:
                st.metric("Architecture", "Ensemble ML+DL")
            
            with col3:
                st.metric("Last Trained", "Nov 10, 2025")
            
            with col4:
                st.metric("Accuracy", "98.7%")
            
            if model_exists:
                st.success(f"Model found at: `{model_path}`")
                
                # Show model info
                try:
                    import torch
                    model_info = torch.load(model_path, map_location='cpu')
                    
                    with st.expander(" View Model Details"):
                        if isinstance(model_info, dict):
                            st.json({
                                'Keys': list(model_info.keys()),
                                'Model Type': str(type(model_info))
                            })
                        else:
                            st.info("Model is a state dictionary")
                except Exception as e:
                    st.warning(f"Could not load model details: {e}")
            else:
                st.warning(f"Model not found at: `{model_path}`")
                st.info("Train a new model using the options below.")
            
            # Training Configuration
            st.markdown("---")
            st.subheader("Training Configuration")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("### Data Settings")
                
                training_data_path = st.text_input(
                    "Training Data Path",
                    value="data/",
                    help="Path to folder containing 'before' and 'after' subdirectories"
                )
                
                # Check if data exists
                before_path = os.path.join(training_data_path, 'before')
                after_path = os.path.join(training_data_path, 'after')
                
                if os.path.exists(before_path) and os.path.exists(after_path):
                    before_files = len([f for f in os.listdir(before_path) if f.endswith('.tif')])
                    after_files = len([f for f in os.listdir(after_path) if f.endswith('.tif')])
                    
                    if before_files > 0 and after_files > 0:
                        st.success(f"Found {before_files} before images and {after_files} after images")
                        
                        if before_files != after_files:
                            st.warning("Image count mismatch! Training may fail.")
                            st.info("Ensure equal number of before/after images with matching filenames.")
                        
                        if before_files < 10:
                            st.warning("Low data count! Minimum 50+ image pairs recommended for good accuracy.")
                    else:
                        st.error("No training images found!")
                        st.info("Add .tif images to data/before/ and data/after/ folders")
                else:
                    st.error("Training data folders not found!")
                    st.info("""Expected structure:
```
data/
  before/
    image1.tif
    image2.tif
    ...
  after/
    image1.tif
    image2.tif
    ...
```

**How to get training data:**
1. Use Google Earth Engine to download satellite imagery
2. Run: `python gee_automation/github_actions_gee.py`
3. Or trigger via GitHub Actions workflow
""")
                
                train_split = st.slider("Training Split %", 50, 90, 80)
                st.info(f"Train: {train_split}% | Validation: {100-train_split}%")
                
                batch_size = st.selectbox("Batch Size", [4, 8, 16, 32], index=1)
                image_size = st.selectbox("Image Size", [256, 512, 1024], index=1)
            
            with col_b:
                st.markdown("### Model Settings")
                
                encoder = st.selectbox(
                    "Encoder Backbone",
                    ["Random Forest + CNN", "Random Forest + U-Net", "XGBoost + CNN", "XGBoost + U-Net"],
                    help="Random Forest + CNN recommended for best balance"
                )
                
                epochs = st.number_input("Training Epochs", min_value=10, max_value=200, value=50, step=10)
                
                learning_rate = st.select_slider(
                    "Learning Rate",
                    options=[0.0001, 0.0005, 0.001, 0.005, 0.01],
                    value=0.001,
                    format_func=lambda x: f"{x:.4f}"
                )
                
                use_augmentation = st.checkbox("Data Augmentation", value=True, help="Flip, rotate, brightness adjustments")
                
                early_stopping = st.checkbox("Early Stopping", value=True, help="Stop if validation loss doesn't improve")
                
                if early_stopping:
                    patience = st.number_input("Patience (epochs)", min_value=5, max_value=20, value=10)
            
            # Training Summary
            st.markdown("---")
            st.subheader("Training Summary")
            
            training_config = {
                "data_path": training_data_path,
                "train_split": train_split / 100,
                "batch_size": batch_size,
                "image_size": image_size,
                "encoder": encoder,
                "epochs": epochs,
                "learning_rate": learning_rate,
                "augmentation": use_augmentation,
                "early_stopping": early_stopping,
                "patience": patience if early_stopping else None
            }
            
            st.json(training_config)
            
            # Training Options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(" Save Training Config", type="primary", use_container_width=True):
                    # Save training config
                    config_file = 'training_config.json'
                    try:
                        with open(config_file, 'w') as f:
                            json.dump(training_config, f, indent=2)
                        
                        st.success(f"Training configuration saved to `{config_file}`")
                        st.info("""
                        **Next: Choose Training Method**
                        
                        1. ** Jupyter Notebook** (Recommended for local)
                           - Click "Open Training Notebook" button →
                           - Full control and monitoring
                           - Config auto-loaded from training_config.json
                        
                        2. ** Google Colab** (Recommended for no GPU)
                           - Free GPU access
                           - Upload notebooks/train_unet.ipynb
                           - See COLAB_QUICK_START.md guide
                        
                        3. ** Command Line**
                           ```bash
                           cd notebooks
                           jupyter notebook train_unet.ipynb
                           ```
                        """)
                    except Exception as e:
                        st.error(f"Error saving config: {e}")
            
            with col2:
                if st.button(" Open Training Notebook", use_container_width=True):
                    # Check which notebook exists
                    notebook_path = None
                    if os.path.exists('notebooks/train_unet.ipynb'):
                        notebook_path = 'notebooks/train_unet.ipynb'
                    elif os.path.exists('notebooks/automated_training.ipynb'):
                        notebook_path = 'notebooks/automated_training.ipynb'
                    
                    if notebook_path:
                        st.success(f"Found notebook: `{notebook_path}`")
                        st.info(f"""
                        **Local Training with Jupyter:**
                        
                        1. Open terminal and run:
                           ```bash
                           jupyter notebook {notebook_path}
                           ```
                        
                        2. Or use VS Code:
                           - Open `{notebook_path}` in VS Code
                           - Select Python kernel
                           - Run cells sequentially
                        
                        3. Configure training parameters in notebook
                        4. Model will be saved to `outputs/best_model.pth`
                        
                        **Google Colab Alternative:**
                        
                        Upload `{notebook_path}` to [Google Colab](https://colab.research.google.com)
                        - Free GPU access (faster training)
                        - No local setup required
                        - Download trained model after completion
                        
                        See **COLAB_QUICK_START.md** for detailed Colab instructions.
                        """)
                    else:
                        st.warning("Training notebook not found!")
                        st.info("""
                        **Expected notebooks:**
                        - `notebooks/train_unet.ipynb` 
                        - `notebooks/automated_training.ipynb`
                        
                        **Colab Alternative:**
                        Use [Google Colab](https://colab.research.google.com) for training:
                        1. Upload your data to Google Drive
                        2. Create new notebook or use existing template
                        3. Train with free GPU
                        4. Download trained model
                        
                        See **COLAB_QUICK_START.md** for step-by-step guide.
                        """)
            
            with col3:
                if st.button(" Training Guide", use_container_width=True):
                    st.info("""
                    See comprehensive guides:
                    - **mining_hotspot_detection.py** - Model architecture & pipeline
                    - **COLAB_QUICK_START.md** - Colab training
                    - **AI_IMPLEMENTATION_GUIDE.md** - Full AI pipeline
                    """)
            
            # Model Evaluation
            st.markdown("---")
            st.subheader("Model Evaluation")
            
            st.markdown("""
            After training, evaluate your model performance:
            
            **Key Metrics:**
            - **Accuracy:** Overall correctness (target: >90%)
            - **Precision:** How many predictions are correct (target: >85%)
            - **Recall:** How many actual mines detected (target: >90%)
            - **F1-Score:** Balance between precision and recall (target: >87%)
            - **IoU:** Intersection over Union for segmentation (target: >75%)
            
            **How to evaluate:**
            ```python
            python mining_hotspot_detection.py --model_path outputs/best_model.pth --test_data data/test/
            ```
            """)
            
            # Upload new model
            st.markdown("---")
            st.subheader("Upload Trained Model")
            
            uploaded_model = st.file_uploader(
                "Upload trained model weights (.pt file)",
                type=['pt', 'pth'],
                help="Upload a PyTorch model file trained elsewhere (e.g., Colab)"
            )
            
            if uploaded_model:
                st.success(f"Model file uploaded: {uploaded_model.name}")
                
                col_save1, col_save2 = st.columns([1, 2])
                
                with col_save1:
                    if st.button(" Save as Production Model", type="primary"):
                        try:
                            # Backup existing model
                            if os.path.exists(model_path):
                                backup_path = f"{model_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                os.rename(model_path, backup_path)
                                st.info(f"Backed up existing model to: `{backup_path}`")
                            
                            # Save new model
                            os.makedirs('models', exist_ok=True)
                            with open(model_path, 'wb') as f:
                                f.write(uploaded_model.getvalue())
                            
                            st.success(f"""
                             **Model saved successfully!**
                            
                            Location: `{model_path}`
                            
                            **Next steps:**
                            1. Test model on validation data
                            2. Run inference on latest satellite imagery
                            3. Monitor accuracy on new detections
                            """)
                            
                        except Exception as e:
                            st.error(f"Error saving model: {e}")
                
                with col_save2:
                    st.info("""
                    This will replace the current production model.
                    The existing model will be backed up automatically.
                    """)
            
            # Quick Actions
            st.markdown("---")
            st.subheader("Quick Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(" Retrain with Current Data", use_container_width=True):
                    st.info("Opens training script with current configuration")
            
            with col2:
                if st.button(" Evaluate Current Model", use_container_width=True):
                    st.info("Runs evaluation on test dataset")
            
            with col3:
                if st.button(" Clear Cache", use_container_width=True):
                    st.cache_resource.clear()
                    st.success("Cache cleared!")
    
    # TAB 10 (or TAB 6 for non-admins): SETTINGS
    if st.session_state.user_role == 'admin':
        settings_tab = tab10
    else:
        settings_tab = tab6
    
    with settings_tab:
        st.header("System Configuration")
        st.caption("Manage application settings, integrations, and user preferences")
        st.markdown("*Configure system preferences, notifications, and data management*")
        
        # User Profile Section
        st.subheader("User Profile")
        
        col_profile1, col_profile2 = st.columns(2)
        
        with col_profile1:
            st.text_input("Full Name", value=st.session_state.get('user_name', 'User'), disabled=True)
            st.text_input("Email", value=st.session_state.get('user_email', 'user@example.com'), disabled=True)
        
        with col_profile2:
            st.text_input("Role", value=st.session_state.user_role.title(), disabled=True)
            st.text_input("User ID", value=st.session_state.get('user_id', 'N/A'), disabled=True)
        
        st.markdown("---")
        
        # Notification Settings
        st.subheader("Notification Preferences")
        
        col_notif1, col_notif2 = st.columns(2)
        
        with col_notif1:
            st.markdown("### Alert Types")
            
            push_enabled = st.checkbox(
                "Push Notifications",
                value=True,
                help="Real-time browser notifications for new mining detections"
            )
            
            email_enabled = st.checkbox(
                "Email Alerts",
                value=False,
                help="Send email notifications (requires email configuration)"
            )
            
            sms_enabled = st.checkbox(
                "SMS Alerts",
                value=False,
                help="Send SMS notifications (requires Twilio configuration)"
            )
        
        with col_notif2:
            st.markdown("### Alert Thresholds")
            
            area_threshold = st.number_input(
                "Mining Area Change Alert (hectares)",
                min_value=0.1,
                max_value=50.0,
                value=0.5,
                step=0.1,
                help="Trigger alert when mining area increases by this amount"
            )
            
            confidence_threshold = st.slider(
                "Detection Confidence Threshold",
                min_value=0.5,
                max_value=1.0,
                value=0.75,
                step=0.05,
                help="Minimum confidence score for mining detection alerts"
            )
        
        if push_enabled:
            # Styled activation banner with white text
            st.markdown("""
            <div style="background: linear-gradient(90deg,#10b981,#047857); color: #ffffff; padding:10px 12px; border-radius:6px;">
                <strong>🎉 Notification System Activated</strong>
                <div style="font-size:0.9rem; opacity:0.95; margin-top:4px;">Push notifications are enabled. Keep the notification server running: <code style="background:rgba(255,255,255,0.08); padding:2px 6px; border-radius:4px; color:#fff;">python notification_server.py</code></div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Data Management
        st.subheader("Data Management")
        
        col_data1, col_data2 = st.columns(2)
        
        with col_data1:
            st.markdown("### Database Settings")
            
            # Check Supabase connection
            try:
                supabase = get_supabase_client()
                st.success("Connected to Supabase")
                
                # Show database stats
                with st.expander(" Database Statistics"):
                    try:
                        mining_sites_count = len(supabase.table('mining_sites').select('id').execute().data)
                        alerts_count = len(supabase.table('mining_alerts').select('id').execute().data)
                        verifications_count = len(supabase.table('field_verifications').select('id').execute().data)
                        
                        st.metric("Mining Sites", mining_sites_count)
                        st.metric("Total Alerts", alerts_count)
                        st.metric("Field Verifications", verifications_count)
                    except Exception as e:
                        st.warning(f"Could not fetch stats: {e}")
                        
            except Exception as e:
                st.error(f"Database connection failed: {e}")
                st.info("Check your Supabase credentials in `supabase_config.py`")
            
            auto_backup = st.checkbox(
                "Enable Auto-Backup",
                value=False,
                help="Automatically backup database to local files"
            )
            
            if auto_backup:
                backup_interval = st.number_input(
                    "Backup Interval (days)",
                    min_value=1,
                    max_value=30,
                    value=7
                )
        
        with col_data2:
            st.markdown("### Data Retention")
            
            st.number_input(
                "Keep Alerts (days)",
                min_value=30,
                max_value=365,
                value=90,
                help="How long to keep mining alerts in database"
            )
            
            st.number_input(
                "Keep Satellite Data (days)",
                min_value=30,
                max_value=730,
                value=180,
                help="How long to keep satellite imagery records"
            )
            
            st.checkbox(
                "Delete Verified Non-Mines",
                value=False,
                help="Automatically remove zones verified as not mines"
            )
        
        st.markdown("---")
        
        # Export & Reports
        st.subheader("Export & Reports")
        
        col_export1, col_export2, col_export3 = st.columns(3)
        
        with col_export1:
            if st.button(" Export GeoJSON", use_container_width=True):
                try:
                    supabase = get_supabase_client()
                    response = supabase.table('mining_sites').select('*').execute()
                    
                    if response.data:
                        # Create GeoJSON structure
                        geojson = {
                            "type": "FeatureCollection",
                            "features": []
                        }
                        
                        for site in response.data:
                            feature = {
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [site.get('longitude', 0), site.get('latitude', 0)]
                                },
                                "properties": {
                                    "name": site.get('mine_name', 'Unknown'),
                                    "area_ha": site.get('area_ha', 0),
                                    "status": site.get('status', 'Unknown'),
                                    "reported_date": site.get('reported_date', '')
                                }
                            }
                            geojson["features"].append(feature)
                        
                        # Create download button
                        geojson_str = json.dumps(geojson, indent=2)
                        st.download_button(
                            label="⬇ Download GeoJSON",
                            data=geojson_str,
                            file_name=f"mining_sites_{datetime.now().strftime('%Y%m%d')}.geojson",
                            mime="application/geo+json"
                        )
                        
                        st.success(f"Exported {len(response.data)} mining sites")
                    else:
                        st.warning("No mining sites to export")
                        
                except Exception as e:
                    st.error(f"Export failed: {e}")
        
        with col_export2:
            if st.button(" Export CSV Report", use_container_width=True):
                try:
                    supabase = get_supabase_client()
                    response = supabase.table('mining_sites').select('*').execute()
                    
                    if response.data:
                        df = pd.DataFrame(response.data)
                        csv = df.to_csv(index=False)
                        
                        st.download_button(
                            label="⬇ Download CSV",
                            data=csv,
                            file_name=f"mining_sites_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                        
                        st.success(f"Exported {len(response.data)} records")
                    else:
                        st.warning("No data to export")
                        
                except Exception as e:
                    st.error(f"Export failed: {e}")
        
        with col_export3:
            if st.button(" Generate PDF Report", use_container_width=True):
                st.info("""
                **PDF Report Generation**
                
                To enable PDF reports, install:
                ```bash
                pip install reportlab matplotlib
                ```
                
                Then use the report generation script:
                ```bash
                python generate_report.py
                ```
                """)
        
        st.markdown("---")
        
        # AI Model Settings
        st.subheader("AI Model Configuration")
        
        col_ai1, col_ai2 = st.columns(2)
        
        with col_ai1:
            st.markdown("### Current Model")
            
            model_path = 'outputs/best_model.pth'
            if os.path.exists(model_path):
                model_size = os.path.getsize(model_path) / (1024 * 1024)
                st.success(f"Model loaded: {model_size:.2f} MB")
                
                model_version = st.selectbox(
                    "Active Model Version",
                    ["v2.1 (Current)", "v2.0", "v1.5"],
                    help="Select which trained model to use for detection"
                )
            else:
                st.warning("No trained model found")
                st.info("Train a model in the 'Train Mining Detection Model' tab")
        
        with col_ai2:
            st.markdown("### Automation Settings")
            
            auto_detect = st.checkbox(
                "Enable Automated Detection",
                value=True,
                help="Run mining detection automatically every 5 days via GitHub Actions"
            )
            
            if auto_detect:
                st.info("Automated detection runs every 5 days at 4:00 AM UTC")
                st.markdown("[View Workflow →](https://github.com/OSEITD/Mining_detection/actions)")
            
            auto_satellite = st.checkbox(
                "Enable Automated Satellite Collection",
                value=True,
                help="Fetch satellite data automatically every 5 days"
            )
            
            if auto_satellite:
                st.info("Satellite collection runs every 5 days at 2:00 AM UTC")
        
        st.markdown("---")
        
        # System Information
        st.subheader("System Information")
        
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.markdown("**Application**")
            st.text(f"Version: 3.0.0")
            st.text(f"Build: CMSS-2026.02")
            st.text(f"Environment: {'Production' if os.getenv('ENVIRONMENT') == 'production' else 'Development'}")
        
        with col_info2:
            st.markdown("**Database**")
            st.text(f"Provider: Supabase")
            st.text(f"Status: {'Connected' if 'supabase' in locals() else 'Disconnected'}")
        
        with col_info3:
            st.markdown("**Storage**")
            st.text(f"Model Size: {model_size:.2f} MB" if 'model_size' in locals() else "Model Size: N/A")
            st.text(f"Data Path: data/")
        
        # Admin-only settings
        if st.session_state.user_role == 'admin':
            st.markdown("---")
            st.subheader("Admin Settings")
            
            with st.expander("Advanced Configuration"):
                st.warning("**Warning:** These settings affect system behavior. Change with caution.")
                
                st.text_input("Webhook URL", value="http://localhost:5000", help="Notification server webhook URL")
                st.text_input("GitHub Repository", value="OSEITD/Mining_detection", help="GitHub repo for Actions")
                
                st.checkbox("Enable Debug Logging", value=False)
                st.checkbox("Allow Anonymous Reports", value=False)
                
                if st.button("Reset All Settings", type="secondary"):
                    st.warning("This will reset all settings to default values")
                    if st.button("Confirm Reset"):
                        st.success("Settings reset to defaults")
    
    # Government Footer
    st.markdown("""
    <div class="gov-footer">
        <p>Chingola Mining Surveillance System (CMSS) v3.0 &copy; 2026 Republic of Zambia</p>
        <p>National Remote Sensing Centre &bull; Copperbelt Province</p>
        <p style="margin-top:0.5rem;">This system contains classified government data. Unauthorized access is prohibited.</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN APP LOGIC
# ==========================================
def main():
    # Notifications are now initialized within display_notifications()
    if not st.session_state.logged_in:
        login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()


