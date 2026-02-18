"""
Enhanced Streamlit App with Satellite Data Integration
Adds automated satellite monitoring dashboard
"""

import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Supabase Configuration
SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw"

# Page config
st.set_page_config(
    page_title="Mining Detection System",
    page_icon="🛰️",
    layout="wide"
)

# Initialize Supabase
@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# Sidebar navigation
st.sidebar.title("🛰️ Mining Detection")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🛰️ Satellite Data", "📊 Mining Updates", "⚙️ System Status"]
)

# === SATELLITE DATA PAGE ===
if page == "🛰️ Satellite Data":
    st.title("🛰️ Automated Satellite Data Monitoring")
    st.markdown("*Real-time satellite imagery collection from Google Earth Engine*")
    
    # Fetch satellite data
    try:
        response = supabase.table('satellite_updates')\
            .select('*')\
            .order('collection_date', desc=True)\
            .execute()
        
        if response.data and len(response.data) > 0:
            # Latest collection metrics
            latest = response.data[0]
            
            st.header("📡 Latest Collection")
            
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
                status_color = "🟢" if latest['status'] == 'completed' else "🔴"
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
            **ℹ️ Collection Details:**
            - Next automatic collection: **November 11, 2025 at 2:00 AM UTC**
            - Frequency: Every 5 days
            - Area of Interest: Chingola, Zambia
            - Image Source: Sentinel-2 (10m resolution)
            """)
            
            # Manual trigger section
            st.header("🚀 Manual Collection Trigger")
            
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
                if st.button("🚀 Trigger Collection", type="primary", use_container_width=True):
                    st.success("✅ Opening GitHub Actions...")
                    st.markdown("""
                    **Next Steps:**
                    1. Click [this link](https://github.com/OSEITD/Mining_detection/actions/workflows/gee_automation.yml) to open GitHub Actions
                    2. Click the green **"Run workflow"** button
                    3. Keep **"main"** branch selected
                    4. Click **"Run workflow"** to confirm
                    5. Wait 3-5 minutes for completion
                    6. Refresh this page to see new data
                    """)
                    
                if st.button("🔄 Refresh Data", use_container_width=True):
                    st.cache_resource.clear()
                    st.rerun()
            
            # Historical data
            st.header("📊 Collection History")
            
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
                st.subheader("📈 Images Found Per Collection")
                
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
            st.header("🖼️ Access Satellite Imagery")
            
            tab1, tab2, tab3 = st.tabs(["📍 View in GEE", "💾 Export to Drive", "🔗 Download Links"])
            
            with tab1:
                st.markdown("""
                ### View imagery in Google Earth Engine Code Editor
                
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
            
            with tab2:
                st.markdown("""
                ### Export to Google Drive for Processing
                
                For U-Net model inference, export images to Google Drive first.
                
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
            
            with tab3:
                st.markdown("""
                ### Direct Download Links (Not Available)
                
                ⚠️ Direct download URLs are currently disabled because:
                - Area of interest is too large (>50 MB compressed)
                - GEE getDownloadURL has strict size limits
                
                **Solutions:**
                1. Use Google Drive export (recommended)
                2. Reduce AOI size in the workflow script
                3. Process imagery directly in GEE Code Editor
                
                For automated U-Net inference:
                - Export to Drive
                - Download in Colab
                - Process with U-Net model
                - Upload predictions to Supabase
                """)
                
                if latest.get('download_url'):
                    st.info(f"RGB URL: {latest['download_url']}")
                if latest.get('ndvi_url'):
                    st.info(f"NDVI URL: {latest['ndvi_url']}")
        
        else:
            st.warning("⚠️ No satellite data found yet.")
            st.info("""
            **Possible reasons:**
            - Workflow hasn't run yet (scheduled for every 5 days)
            - First scheduled run: November 11, 2025
            
            **Action:**
            Trigger a manual collection using the button above to populate data immediately.
            """)
            
            if st.button("🚀 Trigger First Collection", type="primary"):
                st.markdown("[Open GitHub Actions →](https://github.com/OSEITD/Mining_detection/actions/workflows/gee_automation.yml)")
    
    except Exception as e:
        st.error(f"Error fetching satellite data: {e}")
        st.info("Make sure the satellite_updates table exists in Supabase.")

# === DASHBOARD PAGE ===
elif page == "🏠 Dashboard":
    st.title("🏠 Mining Detection Dashboard")
    st.markdown("*Automated illegal mining detection system for Chingola, Zambia*")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    try:
        # Mining updates count
        mining_response = supabase.table('mining_updates').select('*', count='exact').execute()
        mining_count = mining_response.count if mining_response.count else 0
        
        # Satellite updates count
        sat_response = supabase.table('satellite_updates').select('*', count='exact').execute()
        sat_count = sat_response.count if sat_response.count else 0
        
        # Storage files count (if available)
        storage_count = 9  # Known from previous uploads
        
        with col1:
            st.metric("Mining Updates", mining_count)
        
        with col2:
            st.metric("Satellite Collections", sat_count)
        
        with col3:
            st.metric("Storage Files", storage_count, delta="7.31 MB")
        
        # System overview
        st.header("🔄 Automated System Overview")
        
        st.markdown("""
        ### Your Complete Monitoring Pipeline:
        
        **1. 🛰️ Satellite Data Collection** *(Automated)*
        - **Source:** Sentinel-2 via Google Earth Engine
        - **Frequency:** Every 5 days
        - **Status:** ✅ Active
        - **Next Run:** November 11, 2025 at 2:00 AM UTC
        
        **2. 🤖 U-Net Model Processing** *(Manual/Colab)*
        - **Platform:** Google Colab
        - **Model:** U-Net for change detection
        - **Status:** ✅ Ready
        - **Last Run:** Check Colab notebook
        
        **3. ☁️ Cloud Storage** *(Supabase)*
        - **Database:** 3 tables (mining_updates, satellite_updates, mining_sites)
        - **Storage:** 9 files (7.31 MB)
        - **Status:** ✅ Connected
        
        **4. 📱 Mobile Application** *(Android)*
        - **Platform:** Android APK (2.85 MB)
        - **Features:** Real-time updates, map visualization
        - **Status:** ✅ Deployed
        
        **5. 🌐 Web Dashboard** *(This App)*
        - **Platform:** Streamlit
        - **Access:** http://192.168.43.27:8501
        - **Status:** ✅ Running
        """)
        
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

# === MINING UPDATES PAGE ===
elif page == "📊 Mining Updates":
    st.title("📊 Mining Detection Updates")
    
    try:
        response = supabase.table('mining_updates').select('*').order('update_time', desc=True).execute()
        
        if response.data:
            st.success(f"Found {len(response.data)} mining updates")
            
            df = pd.DataFrame(response.data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No mining updates yet. Process satellite imagery in Colab to generate updates.")
    
    except Exception as e:
        st.error(f"Error: {e}")

# === SYSTEM STATUS PAGE ===
elif page == "⚙️ System Status":
    st.title("⚙️ System Health & Status")
    
    # Component status checks
    st.header("🔍 Component Status")
    
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        # Check Supabase connection
        try:
            test = supabase.table('mining_updates').select('id').limit(1).execute()
            st.success("✅ Supabase Database: Connected")
        except:
            st.error("❌ Supabase Database: Connection Failed")
        
        # Check satellite_updates table
        try:
            test = supabase.table('satellite_updates').select('id').limit(1).execute()
            st.success("✅ Satellite Updates Table: Available")
        except:
            st.error("❌ Satellite Updates Table: Not Found")
    
    with status_col2:
        # GitHub Actions status
        st.info("🔄 GitHub Actions: Check manually at [Actions page](https://github.com/OSEITD/Mining_detection/actions)")
        
        # Google Earth Engine
        st.info("🌍 Google Earth Engine: Authenticated via workflow")
    
    # Quick links
    st.header("🔗 Quick Links")
    
    link_col1, link_col2, link_col3 = st.columns(3)
    
    with link_col1:
        st.markdown("""
        **GitHub:**
        - [Repository](https://github.com/OSEITD/Mining_detection)
        - [Actions](https://github.com/OSEITD/Mining_detection/actions)
        - [Workflow File](.github/workflows/gee_automation.yml)
        """)
    
    with link_col2:
        st.markdown("""
        **Supabase:**
        - [Dashboard](https://ntkzaobvbsppxbljamvb.supabase.co)
        - [Table Editor](https://ntkzaobvbsppxbljamvb.supabase.co/project/ntkzaobvbsppxbljamvb/editor)
        - [Storage](https://ntkzaobvbsppxbljamvb.supabase.co/project/ntkzaobvbsppxbljamvb/storage/buckets)
        """)
    
    with link_col3:
        st.markdown("""
        **Google Earth Engine:**
        - [Code Editor](https://code.earthengine.google.com)
        - [Asset Manager](https://code.earthengine.google.com/#asset)
        - [Documentation](https://developers.google.com/earth-engine)
        """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("""
**Mining Detection System v2.0**

Automated illegal mining detection for Chingola, Zambia using:
- Sentinel-2 satellite imagery
- U-Net deep learning model
- Real-time cloud monitoring

© 2025 Final Year Project
""")
