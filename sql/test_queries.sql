-- ============================================================
-- Brainforge Proposal Writer - Test & Verification Queries
-- ============================================================
-- Run these queries to verify your database setup and test RAG functionality
-- ============================================================


-- ============================================================
-- 1. SETUP VERIFICATION
-- ============================================================

-- Check if PGVector extension is enabled
SELECT
    extname AS extension_name,
    extversion AS version
FROM pg_extension
WHERE extname = 'vector';
-- Expected: 1 row with extname='vector'


-- Check if documents table exists and view structure
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'documents'
ORDER BY ordinal_position;
-- Expected: 5 columns (id, content, metadata, embedding, created_at)


-- Check if match_documents function exists
SELECT
    proname AS function_name,
    pronargs AS num_arguments
FROM pg_proc
WHERE proname = 'match_documents';
-- Expected: 1 row with function_name='match_documents'


-- List all indexes on documents table
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'documents'
ORDER BY indexname;
-- Expected: At least 3 indexes (embedding_cosine, metadata, created_at)


-- ============================================================
-- 2. DATA VERIFICATION (After RAG Ingestion)
-- ============================================================

-- Count total documents
SELECT COUNT(*) AS total_documents FROM documents;
-- Expected: > 0 after running RAG ingestion


-- Count documents with embeddings
SELECT COUNT(*) AS documents_with_embeddings
FROM documents
WHERE embedding IS NOT NULL;
-- Expected: Should equal total_documents


-- View sample document metadata
SELECT
    metadata->>'file_title' AS title,
    metadata->>'industry' AS industry,
    metadata->>'project_type' AS project_type,
    metadata->'tech_stack' AS technologies
FROM documents
LIMIT 5;
-- Expected: Returns case study metadata


-- Count documents by industry
SELECT
    metadata->>'industry' AS industry,
    COUNT(*) AS document_count
FROM documents
GROUP BY metadata->>'industry'
ORDER BY document_count DESC;
-- Expected: Breakdown by industry


-- Count documents by project type
SELECT
    metadata->>'project_type' AS project_type,
    COUNT(*) AS document_count
FROM documents
GROUP BY metadata->>'project_type'
ORDER BY document_count DESC;
-- Expected: Breakdown by project type


-- List all unique technologies in tech_stack
SELECT DISTINCT
    jsonb_array_elements_text(metadata->'tech_stack') AS technology,
    COUNT(*) AS usage_count
FROM documents
WHERE metadata ? 'tech_stack'
GROUP BY technology
ORDER BY usage_count DESC;
-- Expected: List of all technologies used across case studies


-- ============================================================
-- 3. METADATA FILTERING TESTS
-- ============================================================

-- Find all E-commerce projects
SELECT
    metadata->>'file_title' AS title,
    metadata->>'client' AS client,
    metadata->>'project_type' AS type
FROM documents
WHERE metadata->>'industry' = 'E-commerce'
LIMIT 10;


-- Find all projects using Python
SELECT DISTINCT
    metadata->>'file_title' AS title,
    metadata->>'industry' AS industry
FROM documents
WHERE metadata->'tech_stack' ? 'Python'
LIMIT 10;


-- Find AI/ML projects in Healthcare
SELECT DISTINCT
    metadata->>'file_title' AS title,
    metadata->>'client' AS client
FROM documents
WHERE metadata->>'industry' = 'Healthcare'
  AND metadata->>'project_type' = 'AI_ML'
LIMIT 10;


-- Find projects using specific tech stack combination
SELECT DISTINCT
    metadata->>'file_title' AS title,
    metadata->'tech_stack' AS technologies
FROM documents
WHERE metadata->'tech_stack' ?& ARRAY['Python', 'PostgreSQL']
LIMIT 10;


-- ============================================================
-- 4. RAG SEMANTIC SEARCH TESTS
-- ============================================================

-- IMPORTANT: These queries require actual embeddings in the database
-- They will fail if you haven't run RAG ingestion yet


-- Test 1: Find documents similar to a random existing document
-- (This tests that vector search is working)
SELECT
    d1.metadata->>'file_title' AS similar_to,
    d2.metadata->>'file_title' AS found_document,
    1 - (d1.embedding <=> d2.embedding) AS similarity_score
FROM documents d1
CROSS JOIN LATERAL (
    SELECT *
    FROM documents d2
    WHERE d2.id != d1.id
    ORDER BY d1.embedding <=> d2.embedding
    LIMIT 3
) d2
WHERE d1.id = (SELECT id FROM documents LIMIT 1)
ORDER BY similarity_score DESC;
-- Expected: 3 most similar documents to the first document


-- Test 2: Use match_documents function (the way RAG pipeline calls it)
-- Note: This uses a sample embedding from your existing data
SELECT
    metadata->>'file_title' AS title,
    metadata->>'industry' AS industry,
    metadata->>'project_type' AS type,
    similarity
FROM match_documents(
    query_embedding := (SELECT embedding FROM documents LIMIT 1),
    match_count := 5
)
ORDER BY similarity DESC;
-- Expected: 5 most similar documents


-- Test 3: Semantic search with metadata filter (industry = 'E-commerce')
SELECT
    metadata->>'file_title' AS title,
    metadata->>'project_type' AS type,
    similarity
FROM match_documents(
    query_embedding := (SELECT embedding FROM documents LIMIT 1),
    match_count := 5,
    filter := '{"industry": "E-commerce"}'::JSONB
)
ORDER BY similarity DESC;
-- Expected: 5 E-commerce projects similar to query


-- ============================================================
-- 5. PERFORMANCE TESTS
-- ============================================================

-- Check index usage for vector search
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM documents
ORDER BY embedding <=> (SELECT embedding FROM documents LIMIT 1)
LIMIT 5;
-- Expected: Should show "Index Scan using idx_documents_embedding_cosine"


-- Check index usage for metadata filter
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM documents
WHERE metadata->>'industry' = 'E-commerce';
-- Expected: Should show "Bitmap Index Scan on idx_documents_metadata" or similar


-- ============================================================
-- 6. DATA QUALITY CHECKS
-- ============================================================

-- Find documents missing key metadata fields
SELECT
    id,
    metadata->>'file_title' AS title
FROM documents
WHERE NOT (
    metadata ? 'file_id' AND
    metadata ? 'file_title' AND
    metadata ? 'industry' AND
    metadata ? 'project_type'
)
LIMIT 10;
-- Expected: Empty result (all documents should have required metadata)


-- Find documents with empty tech_stack
SELECT
    metadata->>'file_title' AS title,
    metadata->'tech_stack' AS tech_stack
FROM documents
WHERE metadata->'tech_stack' = '[]'::JSONB
   OR NOT (metadata ? 'tech_stack')
LIMIT 10;
-- Expected: Minimal results (most case studies should list technologies)


-- Check for duplicate file_ids (should be none)
SELECT
    metadata->>'file_id' AS file_id,
    COUNT(*) AS chunk_count
FROM documents
GROUP BY metadata->>'file_id'
HAVING COUNT(*) > 20  -- Adjust threshold based on expected chunk count
ORDER BY chunk_count DESC;
-- Expected: Normal chunk counts (typically 3-10 per document)


-- ============================================================
-- 7. CLEANUP & MAINTENANCE QUERIES
-- ============================================================

-- Delete documents for a specific file (useful for re-ingestion)
-- CAUTION: This will permanently delete data!
-- DELETE FROM documents
-- WHERE metadata->>'file_id' = 'your-file-id-here';


-- Delete all documents from a specific client
-- CAUTION: This will permanently delete data!
-- DELETE FROM documents
-- WHERE metadata->>'client' = 'Client Name Here';


-- Vacuum table to reclaim space after deletions
-- VACUUM ANALYZE documents;


-- Rebuild vector index (if search performance degrades)
-- REINDEX INDEX idx_documents_embedding_cosine;


-- ============================================================
-- 8. SAMPLE DATA QUERIES (For Testing UI)
-- ============================================================

-- Get a random case study for testing
SELECT
    metadata->>'file_title' AS title,
    metadata->>'client' AS client,
    metadata->>'industry' AS industry,
    metadata->>'project_type' AS project_type,
    metadata->'tech_stack' AS technologies,
    content AS sample_content
FROM documents
WHERE metadata ? 'file_title'
ORDER BY RANDOM()
LIMIT 1;


-- Simulate proposal writer search (multi-technology filter)
SELECT DISTINCT ON (metadata->>'file_id')
    metadata->>'file_title' AS project,
    metadata->>'industry' AS industry,
    metadata->'tech_stack' AS tech_stack,
    1 - (embedding <=> (SELECT embedding FROM documents LIMIT 1)) AS relevance
FROM documents
WHERE metadata->'tech_stack' ?| ARRAY['Python', 'Tableau', 'Snowflake']
ORDER BY metadata->>'file_id', relevance DESC
LIMIT 5;


-- ============================================================
-- NOTES
-- ============================================================
--
-- Vector Search Operators:
--   <=>  : Cosine distance (use with ORDER BY for similarity search)
--   <->  : L2 distance
--   <#>  : Inner product
--
-- JSONB Operators:
--   ->   : Get JSON object field
--   ->>  : Get JSON object field as text
--   ?    : Does key exist?
--   ?&   : Do all keys exist? (AND)
--   ?|   : Do any keys exist? (OR)
--   @>   : Contains (for filtering with match_documents)
--
-- After running these queries, you should have confidence that:
-- ✅ Database schema is correct
-- ✅ PGVector is working
-- ✅ Documents are properly ingested
-- ✅ Metadata filters work
-- ✅ Semantic search returns relevant results
-- ✅ Indexes are being used for performance
--
-- ============================================================
