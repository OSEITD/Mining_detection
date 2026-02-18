#!/usr/bin/env python3
"""
collect_area_data.py — small wrapper to invoke the Earth Engine download helper
This prevents "script not found" runtime errors from the Streamlit UI.
"""
import sys

try:
    # call the main automation entrypoint from gee_automation
    from gee_automation import fetch_satellite_data
except Exception as e:
    print("ERROR: unable to import gee_automation.fetch_satellite_data:", e)
    sys.exit(2)

if __name__ == "__main__":
    # forward to fetch_satellite_data.main()
    try:
        fetch_satellite_data.main()
    except Exception as e:
        print("ERROR running fetch_satellite_data.main():", e)
        sys.exit(3)
