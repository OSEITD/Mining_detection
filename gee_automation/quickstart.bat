@echo off
echo ============================================================
echo GOOGLE EARTH ENGINE AUTOMATION - QUICK START
echo ============================================================
echo.

REM Check if in correct directory
if not exist "gee_automation\fetch_satellite_data.py" (
    echo ERROR: Please run this from the Project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
echo.
pip install -q earthengine-api geemap supabase geopandas rasterio

echo.
echo ============================================================
echo Step 2: Testing Earth Engine connection...
echo ============================================================
echo.

python -c "import ee; ee.Initialize(); print('Earth Engine: OK')" 2>nul

if errorlevel 1 (
    echo.
    echo Earth Engine NOT authenticated yet.
    echo.
    echo PLEASE RUN:
    echo    earthengine authenticate
    echo.
    echo Then re-run this script.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Step 3: Running GEE automation test...
echo ============================================================
echo.

cd gee_automation
python gee_to_supabase.py

echo.
echo ============================================================
echo TEST COMPLETE!
echo ============================================================
echo.
echo Next steps:
echo 1. Check Supabase dashboard for new satellite_updates record
echo 2. Set up GitHub Actions for automatic scheduling
echo 3. See README.md for detailed documentation
echo.

pause
