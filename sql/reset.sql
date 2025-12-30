-- ============================================================
-- Brainforge Proposal Writer - Database Reset Script
-- ============================================================
-- ⚠️ WARNING: This script will DELETE ALL DATA from your database!
-- Use this to completely reset your Supabase database to a clean state.
--
-- Use cases:
-- - Starting fresh with new case studies
-- - Fixing schema issues
-- - Clearing test data
-- - Switching embedding dimensions (1536 → 768 or vice versa)
--
-- Execute this BEFORE running schema.sql
-- ============================================================

-- ============================================================
-- Step 1: Drop All Functions
-- ============================================================

DROP FUNCTION IF EXISTS match_documents(vector, int, jsonb);
DROP FUNCTION IF EXISTS match_documents(vector(1536), int, jsonb);
DROP FUNCTION IF EXISTS match_documents(vector(768), int, jsonb);

COMMENT ON SCHEMA public IS 'Dropped match_documents function';


-- ============================================================
-- Step 2: Drop All Tables (Cascading)
-- ============================================================

-- Drop main documents table (this is the core RAG table)
DROP TABLE IF EXISTS documents CASCADE;

-- Drop optional structured data tables (if they exist)
DROP TABLE IF EXISTS document_rows CASCADE;
DROP TABLE IF EXISTS document_metadata CASCADE;

-- Drop Mem0 tables (if using Mem0 for memory)
DROP TABLE IF EXISTS memories CASCADE;
DROP TABLE IF EXISTS memory_embeddings CASCADE;

COMMENT ON SCHEMA public IS 'Dropped all tables';


-- ============================================================
-- Step 3: Drop All Indexes (Safety - should cascade with tables)
-- ============================================================

-- Vector indexes
DROP INDEX IF EXISTS idx_documents_embedding_cosine;
DROP INDEX IF EXISTS idx_documents_embedding_l2;
DROP INDEX IF EXISTS idx_documents_embedding_ip;

-- Metadata indexes
DROP INDEX IF EXISTS idx_documents_metadata;
DROP INDEX IF EXISTS idx_documents_created_at;

-- Structured data indexes
DROP INDEX IF EXISTS idx_document_rows_dataset;
DROP INDEX IF EXISTS idx_document_rows_data;

COMMENT ON SCHEMA public IS 'Dropped all indexes';


-- ============================================================
-- Step 4: Drop PGVector Extension (Optional)
-- ============================================================
-- ⚠️ CAUTION: Only drop if you want to completely remove vector support
-- Uncomment the line below if you need to reinstall PGVector

-- DROP EXTENSION IF EXISTS vector CASCADE;

-- COMMENT ON SCHEMA public IS 'Dropped PGVector extension';


-- ============================================================
-- Step 5: Verify Clean State
-- ============================================================

-- Check for remaining tables
SELECT
    tablename,
    schemaname
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('documents', 'document_metadata', 'document_rows', 'memories');

-- Expected result: 0 rows (all tables dropped)


-- Check for remaining functions
SELECT
    proname as function_name,
    pronargs as num_args
FROM pg_proc
WHERE proname = 'match_documents';

-- Expected result: 0 rows (function dropped)


-- Check for remaining indexes
SELECT
    indexname,
    tablename
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('documents', 'document_metadata', 'document_rows');

-- Expected result: 0 rows (all indexes dropped)


-- ============================================================
-- Step 6: Vacuum and Analyze
-- ============================================================

-- Reclaim storage space and update statistics
VACUUM FULL;
ANALYZE;

COMMENT ON SCHEMA public IS 'Database reset complete - ready for schema.sql';


-- ============================================================
-- Reset Complete! ✅
-- ============================================================
-- Your database is now in a clean state.
--
-- Next steps:
-- 1. Run schema.sql to recreate tables and indexes
-- 2. Verify setup with test_queries.sql (Section 1)
-- 3. Run RAG ingestion: python RAG_Pipeline/Local_Files/main.py --directory "./Files"
-- 4. Test search: Run test_queries.sql (Section 4)
--
-- Database state:
-- ✓ All tables dropped
-- ✓ All indexes dropped
-- ✓ All functions dropped
-- ✓ Storage reclaimed
-- ☐ Ready for schema.sql
-- ============================================================


-- ============================================================
-- Optional: Quick Reset Verification
-- ============================================================

-- Run this to confirm everything is clean:
-- Should return 0 tables, 0 functions, 0 indexes

SELECT
    'Tables' as object_type,
    COUNT(*) as count
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('documents', 'document_metadata', 'document_rows')

UNION ALL

SELECT
    'Functions' as object_type,
    COUNT(*) as count
FROM pg_proc
WHERE proname = 'match_documents'

UNION ALL

SELECT
    'Indexes' as object_type,
    COUNT(*) as count
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'documents';

-- Expected output:
-- object_type | count
-- ------------|------
-- Tables      |   0
-- Functions   |   0
-- Indexes     |   0
