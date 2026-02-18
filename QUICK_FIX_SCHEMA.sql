-- ============================================
-- QUICK FIX: Refresh Schema Cache & Verify Columns
-- ============================================
-- Run this in Supabase SQL Editor

-- Step 1: Reload PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Step 2: Verify columns exist in mining_alerts
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'mining_alerts'
  AND column_name IN ('reported_by', 'evidence_url', 'report_source', 'message', 'title')
ORDER BY column_name;

-- Step 3: If columns are missing, add them
DO $$
BEGIN
    -- Add reported_by if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mining_alerts' AND column_name = 'reported_by'
    ) THEN
        ALTER TABLE public.mining_alerts ADD COLUMN reported_by character varying;
        RAISE NOTICE 'Added column: reported_by';
    END IF;

    -- Add evidence_url if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mining_alerts' AND column_name = 'evidence_url'
    ) THEN
        ALTER TABLE public.mining_alerts ADD COLUMN evidence_url text;
        RAISE NOTICE 'Added column: evidence_url';
    END IF;

    -- Add report_source if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mining_alerts' AND column_name = 'report_source'
    ) THEN
        ALTER TABLE public.mining_alerts ADD COLUMN report_source character varying DEFAULT 'automated'::character varying;
        RAISE NOTICE 'Added column: report_source';
    END IF;
END $$;

-- Step 4: Create indexes
CREATE INDEX IF NOT EXISTS idx_mining_alerts_report_source ON public.mining_alerts(report_source);
CREATE INDEX IF NOT EXISTS idx_mining_alerts_reported_by ON public.mining_alerts(reported_by);

-- Step 5: Reload schema cache again
NOTIFY pgrst, 'reload schema';

-- Step 6: Final verification
SELECT 
    '✅ Schema updated and refreshed!' AS status,
    COUNT(*) AS total_columns
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'mining_alerts';

-- Step 7: Show all columns in mining_alerts
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'mining_alerts'
ORDER BY ordinal_position;
