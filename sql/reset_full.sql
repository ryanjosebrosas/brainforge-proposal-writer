-- ============================================================
-- Brainforge Proposal Writer - FULL DATABASE RESET
-- ============================================================
-- ⚠️ ⚠️ ⚠️ NUCLEAR OPTION - DELETES EVERYTHING ⚠️ ⚠️ ⚠️
--
-- This script will DELETE ALL TABLES, FUNCTIONS, VIEWS, AND DATA
-- from your entire Supabase public schema.
--
-- Use this when you want a completely clean slate.
--
-- ⚠️ THIS CANNOT BE UNDONE - ALL DATA WILL BE LOST
-- ============================================================

-- ============================================================
-- Step 1: Drop ALL Functions in Public Schema
-- ============================================================

DO $$
DECLARE
    func_name text;
BEGIN
    FOR func_name IN
        SELECT
            'DROP FUNCTION IF EXISTS ' ||
            ns.nspname || '.' || p.proname ||
            '(' || pg_get_function_identity_arguments(p.oid) || ') CASCADE;'
        FROM pg_proc p
        JOIN pg_namespace ns ON p.pronamespace = ns.oid
        WHERE ns.nspname = 'public'
    LOOP
        EXECUTE func_name;
        RAISE NOTICE 'Dropped function: %', func_name;
    END LOOP;
END$$;

COMMENT ON SCHEMA public IS 'Step 1/6: Dropped all functions';


-- ============================================================
-- Step 2: Drop ALL Views in Public Schema
-- ============================================================

DO $$
DECLARE
    view_name text;
BEGIN
    FOR view_name IN
        SELECT
            'DROP VIEW IF EXISTS ' ||
            schemaname || '.' || viewname || ' CASCADE;'
        FROM pg_views
        WHERE schemaname = 'public'
    LOOP
        EXECUTE view_name;
        RAISE NOTICE 'Dropped view: %', view_name;
    END LOOP;
END$$;

COMMENT ON SCHEMA public IS 'Step 2/6: Dropped all views';


-- ============================================================
-- Step 3: Drop ALL Materialized Views in Public Schema
-- ============================================================

DO $$
DECLARE
    matview_name text;
BEGIN
    FOR matview_name IN
        SELECT
            'DROP MATERIALIZED VIEW IF EXISTS ' ||
            schemaname || '.' || matviewname || ' CASCADE;'
        FROM pg_matviews
        WHERE schemaname = 'public'
    LOOP
        EXECUTE matview_name;
        RAISE NOTICE 'Dropped materialized view: %', matview_name;
    END LOOP;
END$$;

COMMENT ON SCHEMA public IS 'Step 3/6: Dropped all materialized views';


-- ============================================================
-- Step 4: Drop ALL Tables in Public Schema
-- ============================================================

DO $$
DECLARE
    table_name text;
BEGIN
    FOR table_name IN
        SELECT
            'DROP TABLE IF EXISTS ' ||
            schemaname || '.' || tablename || ' CASCADE;'
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE table_name;
        RAISE NOTICE 'Dropped table: %', table_name;
    END LOOP;
END$$;

COMMENT ON SCHEMA public IS 'Step 4/6: Dropped all tables';


-- ============================================================
-- Step 5: Drop ALL Sequences in Public Schema
-- ============================================================

DO $$
DECLARE
    seq_name text;
BEGIN
    FOR seq_name IN
        SELECT
            'DROP SEQUENCE IF EXISTS ' ||
            sequence_schema || '.' || sequence_name || ' CASCADE;'
        FROM information_schema.sequences
        WHERE sequence_schema = 'public'
    LOOP
        EXECUTE seq_name;
        RAISE NOTICE 'Dropped sequence: %', seq_name;
    END LOOP;
END$$;

COMMENT ON SCHEMA public IS 'Step 5/6: Dropped all sequences';


-- ============================================================
-- Step 6: Drop ALL Types (Enums, Composites) in Public Schema
-- ============================================================

DO $$
DECLARE
    type_name text;
BEGIN
    FOR type_name IN
        SELECT
            'DROP TYPE IF EXISTS ' ||
            n.nspname || '.' || t.typname || ' CASCADE;'
        FROM pg_type t
        JOIN pg_namespace n ON t.typnamespace = n.oid
        WHERE n.nspname = 'public'
          AND t.typtype IN ('e', 'c')  -- e=enum, c=composite
    LOOP
        EXECUTE type_name;
        RAISE NOTICE 'Dropped type: %', type_name;
    END LOOP;
END$$;

COMMENT ON SCHEMA public IS 'Step 6/6: Dropped all custom types';


-- ============================================================
-- Step 7: Vacuum and Analyze
-- ============================================================

VACUUM FULL;
ANALYZE;

COMMENT ON SCHEMA public IS 'Full reset complete - public schema is empty';


-- ============================================================
-- Verification: Check What's Left
-- ============================================================

-- Count remaining objects (should all be 0)
SELECT
    'Tables' as object_type,
    COUNT(*) as count
FROM pg_tables
WHERE schemaname = 'public'

UNION ALL

SELECT
    'Views' as object_type,
    COUNT(*) as count
FROM pg_views
WHERE schemaname = 'public'

UNION ALL

SELECT
    'Functions' as object_type,
    COUNT(*) as count
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'

UNION ALL

SELECT
    'Sequences' as object_type,
    COUNT(*) as count
FROM information_schema.sequences
WHERE sequence_schema = 'public'

UNION ALL

SELECT
    'Custom Types' as object_type,
    COUNT(*) as count
FROM pg_type t
JOIN pg_namespace n ON t.typnamespace = n.oid
WHERE n.nspname = 'public'
  AND t.typtype IN ('e', 'c');

-- Expected output: All counts should be 0


-- ============================================================
-- RESET COMPLETE ✅
-- ============================================================
--
-- Your Supabase public schema is now completely empty.
--
-- ⚠️ IMPORTANT: Extensions are NOT dropped
-- If you want to drop PGVector extension too, run:
-- DROP EXTENSION IF EXISTS vector CASCADE;
--
-- Next steps:
-- 1. Run schema.sql to recreate your tables
-- 2. Verify setup with test_queries.sql
-- 3. Run RAG ingestion
--
-- Database state:
-- ✓ All tables dropped
-- ✓ All functions dropped
-- ✓ All views dropped
-- ✓ All sequences dropped
-- ✓ All custom types dropped
-- ✓ Storage reclaimed (VACUUM FULL)
-- ☐ Extensions intact (PGVector still available)
-- ☐ Ready for schema.sql
-- ============================================================


-- ============================================================
-- Optional: Also Drop Extensions (Uncomment if needed)
-- ============================================================

-- ⚠️ WARNING: This will remove PGVector completely
-- Only uncomment if you want to reinstall it from scratch

-- DROP EXTENSION IF EXISTS vector CASCADE;
-- DROP EXTENSION IF EXISTS pg_stat_statements CASCADE;
-- DROP EXTENSION IF EXISTS pgcrypto CASCADE;
-- DROP EXTENSION IF EXISTS uuid-ossp CASCADE;

-- COMMENT ON SCHEMA public IS 'Full reset complete - all extensions dropped';


-- ============================================================
-- Nuclear Option: Drop and Recreate Public Schema
-- ============================================================

-- ⚠️ ⚠️ ⚠️ MOST EXTREME OPTION - RECREATES ENTIRE SCHEMA ⚠️ ⚠️ ⚠️
-- Only uncomment if the above methods don't work

-- DROP SCHEMA IF EXISTS public CASCADE;
-- CREATE SCHEMA public;
-- GRANT ALL ON SCHEMA public TO postgres;
-- GRANT ALL ON SCHEMA public TO public;

-- COMMENT ON SCHEMA public IS 'Public schema recreated from scratch';
