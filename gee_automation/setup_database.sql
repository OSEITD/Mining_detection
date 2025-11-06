-- ============================================================
-- Supabase Database Setup for GEE Automation
-- ============================================================

-- Create satellite_updates table
CREATE TABLE IF NOT EXISTS satellite_updates (
  id BIGSERIAL PRIMARY KEY,
  collection_date TIMESTAMPTZ DEFAULT NOW(),
  satellite TEXT DEFAULT 'Sentinel-2',
  cloud_percentage DECIMAL(5,2),
  image_count INTEGER,
  download_url TEXT,
  ndvi_url TEXT,
  status TEXT DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_satellite_updates_date 
  ON satellite_updates(collection_date DESC);

CREATE INDEX IF NOT EXISTS idx_satellite_updates_status 
  ON satellite_updates(status);

-- Enable Row Level Security
ALTER TABLE satellite_updates ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read access (for mobile app)
DROP POLICY IF EXISTS "Allow public read access" ON satellite_updates;
CREATE POLICY "Allow public read access" 
  ON satellite_updates FOR SELECT 
  USING (true);

-- Policy: Allow authenticated inserts (for automation)
DROP POLICY IF EXISTS "Allow authenticated inserts" ON satellite_updates;
CREATE POLICY "Allow authenticated inserts" 
  ON satellite_updates FOR INSERT 
  WITH CHECK (true);

-- Policy: Allow authenticated updates
DROP POLICY IF EXISTS "Allow authenticated updates" ON satellite_updates;
CREATE POLICY "Allow authenticated updates" 
  ON satellite_updates FOR UPDATE 
  USING (true);

-- Add comments
COMMENT ON TABLE satellite_updates IS 'Stores metadata for automatically collected satellite imagery from Google Earth Engine';
COMMENT ON COLUMN satellite_updates.collection_date IS 'When the satellite data was collected';
COMMENT ON COLUMN satellite_updates.download_url IS 'Direct download URL for the satellite image (GeoTIFF)';
COMMENT ON COLUMN satellite_updates.ndvi_url IS 'Direct download URL for NDVI calculation (GeoTIFF)';

-- ============================================================
-- Verification Queries
-- ============================================================

-- Check if table was created
SELECT 
  table_name, 
  table_type 
FROM information_schema.tables 
WHERE table_name = 'satellite_updates';

-- View table structure
SELECT 
  column_name, 
  data_type, 
  is_nullable 
FROM information_schema.columns 
WHERE table_name = 'satellite_updates'
ORDER BY ordinal_position;

-- ============================================================
-- Test Queries
-- ============================================================

-- Get latest satellite update
SELECT * FROM satellite_updates 
ORDER BY collection_date DESC 
LIMIT 1;

-- Count total updates
SELECT COUNT(*) as total_updates FROM satellite_updates;

-- Get updates from last 30 days
SELECT 
  id,
  collection_date,
  satellite,
  status
FROM satellite_updates 
WHERE collection_date > NOW() - INTERVAL '30 days'
ORDER BY collection_date DESC;

-- ============================================================
-- SUCCESS!
-- ============================================================
-- Your satellite_updates table is ready for GEE automation!
-- Run the Python scripts to start collecting data.
-- ============================================================
