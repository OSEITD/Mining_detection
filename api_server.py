"""
FastAPI Backend for Chingola Mining Monitor Mobile App
Provides REST API endpoints for mining sites, statistics, and field reports
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import geopandas as gpd
import pandas as pd
from datetime import datetime
import json
import os

app = FastAPI(
    title="Chingola Mining Monitor API",
    description="API for AI-powered illegal mining detection system",
    version="1.0.0"
)

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your mobile app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class MiningSite(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    status: str
    area: float
    detectionDate: str

class MiningStats(BaseModel):
    totalSites: int
    activeMines: int
    abandoned: int
    totalArea: float
    alerts: int

class FieldReport(BaseModel):
    location: str
    coordinates: dict
    description: str
    photo: Optional[str] = None
    timestamp: str

# Load GeoJSON data
GEOJSON_PATH = "data/lable/chingola_mines.geojson"

def load_mining_sites():
    """Load mining sites from GeoJSON"""
    try:
        gdf = gpd.read_file(GEOJSON_PATH)
        sites = []
        
        for idx, row in gdf.iterrows():
            # Get centroid coordinates
            centroid = row.geometry.centroid
            
            # Handle null values
            status = row.get('status', 'Unknown')
            if status is None or pd.isna(status):
                status = 'Unknown'
            
            area = row.get('area_ha', 0.0)
            if area is None or pd.isna(area):
                area = 0.0
            
            site = {
                "id": str(idx + 1),
                "name": row.get('name', f'Site {idx + 1}'),
                "latitude": centroid.y,
                "longitude": centroid.x,
                "status": str(status).title(),
                "area": float(area),
                "detectionDate": row.get('detected', '2025-01-01')
            }
            sites.append(site)
        
        return sites
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return []

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Chingola Mining Monitor API",
        "version": "1.0.0",
        "endpoints": {
            "mining_sites": "/api/mining-sites",
            "stats": "/api/stats",
            "field_reports": "/api/field-reports"
        }
    }

@app.get("/api/mining-sites", response_model=List[MiningSite])
async def get_mining_sites():
    """Get all mining sites"""
    sites = load_mining_sites()
    if not sites:
        raise HTTPException(status_code=404, detail="No mining sites found")
    return sites

@app.get("/api/stats", response_model=MiningStats)
async def get_stats():
    """Get mining statistics"""
    sites = load_mining_sites()
    
    if not sites:
        return MiningStats(
            totalSites=0,
            activeMines=0,
            abandoned=0,
            totalArea=0.0,
            alerts=0
        )
    
    df = pd.DataFrame(sites)
    
    stats = MiningStats(
        totalSites=len(df),
        activeMines=len(df[df['status'] == 'Active']),
        abandoned=len(df[df['status'] == 'Abandoned']),
        totalArea=round(df['area'].sum(), 1),
        alerts=len(df[df['status'] == 'Active'])
    )
    
    return stats

@app.post("/api/field-reports")
async def submit_field_report(report: FieldReport):
    """Submit a field report from mobile app"""
    try:
        # Save report to JSON file
        reports_file = "field_reports.json"
        
        # Load existing reports
        if os.path.exists(reports_file):
            with open(reports_file, 'r') as f:
                reports = json.load(f)
        else:
            reports = []
        
        # Add new report
        report_data = report.dict()
        report_data['id'] = len(reports) + 1
        reports.append(report_data)
        
        # Save updated reports
        with open(reports_file, 'w') as f:
            json.dump(reports, f, indent=2)
        
        return {
            "success": True,
            "message": "Field report submitted successfully",
            "reportId": report_data['id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/field-reports")
async def get_field_reports():
    """Get all field reports"""
    reports_file = "field_reports.json"
    
    if not os.path.exists(reports_file):
        return []
    
    with open(reports_file, 'r') as f:
        reports = json.load(f)
    
    return reports

if __name__ == "__main__":
    import uvicorn
    print("Starting Chingola Mining Monitor API Server...")
    print("API will be available at: http://0.0.0.0:5000")
    print("Access from mobile: http://<YOUR_IP>:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)
