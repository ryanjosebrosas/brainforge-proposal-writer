-- ============================================================
-- Brainforge Proposal Writer - Supabase Database Schema
-- ============================================================
-- This schema sets up the complete database structure for the
-- RAG Pipeline and Proposal Writer application.
--
-- Execute this in your Supabase SQL Editor to set up the database.
-- ============================================================

-- ============================================================
-- 1. Enable PGVector Extension
-- ============================================================
-- Required for vector similarity search (semantic search)
CREATE EXTENSION IF NOT EXISTS vector;


-- ============================================================
-- 2. Create Documents Table (Core RAG Storage)
-- ============================================================
-- Stores text chunks from case studies with embeddings for semantic search
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL,
    embedding VECTOR(1536),  -- For OpenAI text-embedding-3-small (1536 dimensions)
                            -- Change to VECTOR(768) if using Ollama nomic-embed-text
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add helpful comment to the table
COMMENT ON TABLE documents IS 'Stores document chunks with embeddings for RAG semantic search';
COMMENT ON COLUMN documents.content IS 'Text content of the chunk (typically 400 characters)';
COMMENT ON COLUMN documents.metadata IS 'JSONB containing file_id, file_title, industry, project_type, tech_stack, etc.';
COMMENT ON COLUMN documents.embedding IS 'Vector embedding for semantic search (1536 dims for OpenAI, 768 for Ollama)';


-- ============================================================
-- 3. Create Indexes for Performance
-- ============================================================

-- Index for vector similarity search (CRITICAL for RAG performance)
CREATE INDEX IF NOT EXISTS idx_documents_embedding_cosine
ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for metadata queries (filter by industry, tech_stack, project_type)
CREATE INDEX IF NOT EXISTS idx_documents_metadata
ON documents
USING GIN (metadata);

-- Index for created_at (helpful for chronological queries)
CREATE INDEX IF NOT EXISTS idx_documents_created_at
ON documents (created_at DESC);


-- ============================================================
-- 4. Create RPC Function for Similarity Search
-- ============================================================
-- This function is called by the RAG pipeline to find relevant documents
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding VECTOR(1536),  -- Change to VECTOR(768) for Ollama
  match_count INT DEFAULT 4,
  filter JSONB DEFAULT '{}'::JSONB
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE
    CASE
      WHEN filter = '{}'::JSONB THEN TRUE
      ELSE documents.metadata @> filter
    END
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION match_documents IS 'Find documents by vector similarity with optional metadata filtering';


-- ============================================================
-- 5. Optional Tables for Structured Data (SQL Query Tool)
-- ============================================================
-- Only needed if you're using the execute_sql_query tool for structured data

-- Table metadata for document schemas
CREATE TABLE IF NOT EXISTS document_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    file_id TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    schema JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE document_metadata IS 'Metadata and schema definitions for structured documents (CSVs, Excel files)';

-- Table for document rows
CREATE TABLE IF NOT EXISTS document_rows (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    dataset_id TEXT NOT NULL,
    row_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (dataset_id) REFERENCES document_metadata(file_id) ON DELETE CASCADE
);

COMMENT ON TABLE document_rows IS 'Individual rows from structured documents stored as JSONB';

-- Indexes for structured data queries
CREATE INDEX IF NOT EXISTS idx_document_rows_dataset
ON document_rows(dataset_id);

CREATE INDEX IF NOT EXISTS idx_document_rows_data
ON document_rows
USING GIN (row_data);


-- ============================================================
-- 6. Row Level Security (RLS) - OPTIONAL
-- ============================================================
-- Uncomment if you need RLS for multi-tenant applications

-- Enable RLS on documents table
-- ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy for service key only
-- CREATE POLICY "Service role full access"
-- ON documents
-- FOR ALL
-- TO service_role
-- USING (true)
-- WITH CHECK (true);


-- ============================================================
-- 7. Verification Queries
-- ============================================================
-- Run these after executing the schema to verify everything is set up correctly

-- Check that PGVector extension is enabled
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check that documents table exists
-- SELECT COUNT(*) FROM documents;

-- Check that match_documents function exists
-- SELECT proname, prosrc FROM pg_proc WHERE proname = 'match_documents';

-- Sample query to test vector search (will fail until you have data)
-- SELECT id, metadata->>'file_title' as title, similarity
-- FROM match_documents(
--   query_embedding := (SELECT embedding FROM documents LIMIT 1),
--   match_count := 5
-- );


-- ============================================================
-- Setup Complete! 🎉
-- ============================================================
-- Next steps:
-- 1. Verify environment variables in .env:
--    - SUPABASE_URL
--    - SUPABASE_SERVICE_KEY
--    - EMBEDDING_API_KEY
-- 2. Prepare case studies (see DATA_PREPARATION.md)
-- 3. Run RAG ingestion: python RAG_Pipeline/Local_Files/main.py --directory "./Files"
-- 4. Test the proposal writer: streamlit run streamlit_ui.py
-- ============================================================
