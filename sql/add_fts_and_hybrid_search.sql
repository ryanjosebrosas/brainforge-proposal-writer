-- ============================================
-- Add Full-Text Search (FTS) to RAG Pipeline
-- ============================================

-- 1. Add tsvector column for full-text search
ALTER TABLE documents ADD COLUMN IF NOT EXISTS tsv tsvector;

-- 2. Create GIN index for fast FTS queries
DROP INDEX IF EXISTS documents_tsv_idx;
CREATE INDEX documents_tsv_idx ON documents USING GIN(tsv);

-- 3. Auto-update trigger (keeps tsvector in sync with content)
CREATE OR REPLACE FUNCTION documents_tsv_trigger() RETURNS trigger AS $$
BEGIN
  NEW.tsv := to_tsvector('english', NEW.content);
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS documents_tsv_update ON documents;
CREATE TRIGGER documents_tsv_update BEFORE INSERT OR UPDATE ON documents
FOR EACH ROW EXECUTE FUNCTION documents_tsv_trigger();

-- 4. Populate existing rows
UPDATE documents SET tsv = to_tsvector('english', content);

-- ============================================
-- Hybrid Search Function (Vector + FTS + RRF)
-- ============================================

CREATE OR REPLACE FUNCTION search_hybrid_rag(
  query_text TEXT,
  query_embedding VECTOR(1536),
  match_count INT DEFAULT 5,
  industry_filter TEXT DEFAULT NULL,
  project_type_filter TEXT DEFAULT NULL,
  tech_filter TEXT DEFAULT NULL,
  section_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  chunk_metadata JSONB,
  frontmatter JSONB,
  sections JSONB,
  vector_score FLOAT,
  fts_score FLOAT,
  combined_score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH vector_results AS (
    -- Vector search with rank
    SELECT
      d.id,
      ROW_NUMBER() OVER (ORDER BY d.embedding <=> query_embedding) as rank,
      1 - (d.embedding <=> query_embedding) as score
    FROM documents d
    JOIN document_metadata m ON d.metadata->>'file_id' = m.file_id
    WHERE
      (industry_filter IS NULL OR m.schema->'frontmatter'->>'industry' = industry_filter)
      AND (project_type_filter IS NULL OR m.schema->'frontmatter'->>'project_type' = project_type_filter)
      AND (tech_filter IS NULL OR m.schema->'frontmatter'->'tech_stack' ? tech_filter)
      AND (section_filter IS NULL OR d.metadata->>'section' = section_filter)
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count * 3
  ),
  fts_results AS (
    -- Full-text search with rank
    SELECT
      d.id,
      ROW_NUMBER() OVER (ORDER BY ts_rank_cd(d.tsv, websearch_to_tsquery('english', query_text)) DESC) as rank,
      ts_rank_cd(d.tsv, websearch_to_tsquery('english', query_text)) as score
    FROM documents d
    JOIN document_metadata m ON d.metadata->>'file_id' = m.file_id
    WHERE
      d.tsv @@ websearch_to_tsquery('english', query_text)
      AND (industry_filter IS NULL OR m.schema->'frontmatter'->>'industry' = industry_filter)
      AND (project_type_filter IS NULL OR m.schema->'frontmatter'->>'project_type' = project_type_filter)
      AND (tech_filter IS NULL OR m.schema->'frontmatter'->'tech_stack' ? tech_filter)
      AND (section_filter IS NULL OR d.metadata->>'section' = section_filter)
    ORDER BY score DESC
    LIMIT match_count * 3
  )
  SELECT
    d.id,
    d.content,
    d.metadata as chunk_metadata,
    m.schema->'frontmatter' as frontmatter,
    m.schema->'sections' as sections,
    COALESCE(v.score, 0)::DOUBLE PRECISION as vector_score,
    COALESCE(f.score, 0)::DOUBLE PRECISION as fts_score,
    -- RRF formula: sum(1/(constant + rank))
    -- Vector weight: 1.0, FTS weight: 1.2 (slightly prefer exact matches)
    (COALESCE(1.0/(60 + v.rank), 0) * 1.0 +
     COALESCE(1.0/(60 + f.rank), 0) * 1.2)::DOUBLE PRECISION as combined_score
  FROM documents d
  JOIN document_metadata m ON d.metadata->>'file_id' = m.file_id
  LEFT JOIN vector_results v ON d.id = v.id
  LEFT JOIN fts_results f ON d.id = f.id
  WHERE v.id IS NOT NULL OR f.id IS NOT NULL
  ORDER BY combined_score DESC
  LIMIT match_count;
END;
$$;

-- ============================================
-- Get Full Case Study by File ID
-- ============================================

CREATE OR REPLACE FUNCTION get_case_study_full(
  case_study_file_id TEXT
)
RETURNS TABLE (
  file_id TEXT,
  file_name TEXT,
  frontmatter JSONB,
  sections JSONB,
  total_sections INT,
  chunks JSONB,
  metrics JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    m.file_id,
    m.file_name,
    m.schema->'frontmatter' as frontmatter,
    m.schema->'sections' as sections,
    (m.schema->>'total_sections')::INT as total_sections,
    jsonb_agg(
      jsonb_build_object(
        'section', d.metadata->>'section',
        'content', d.content,
        'chunk_index', d.metadata->>'chunk_index'
      ) ORDER BY (d.metadata->>'chunk_index')::INT
    ) as chunks,
    (
      SELECT jsonb_agg(row_data)
      FROM document_rows
      WHERE dataset_id = m.file_id
    ) as metrics
  FROM document_metadata m
  LEFT JOIN documents d ON d.metadata->>'file_id' = m.file_id
  WHERE m.file_id = case_study_file_id
  GROUP BY m.file_id, m.file_name, m.schema;
END;
$$;

-- ============================================
-- Get Metrics by Filter
-- ============================================

CREATE OR REPLACE FUNCTION get_metrics_by_filter(
  min_value INT DEFAULT NULL,
  metric_type_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
  file_id TEXT,
  file_name TEXT,
  project_title TEXT,
  industry TEXT,
  metric_name TEXT,
  metric_value TEXT,
  metric_unit TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    m.file_id,
    m.file_name,
    m.schema->'frontmatter'->>'title' as project_title,
    m.schema->'frontmatter'->>'industry' as industry,
    r.row_data->>'metric_name' as metric_name,
    r.row_data->>'value' as metric_value,
    r.row_data->>'unit' as metric_unit
  FROM document_metadata m
  JOIN document_rows r ON r.dataset_id = m.file_id
  WHERE
    (min_value IS NULL OR (r.row_data->>'value' ~ '^[0-9]+$' AND (r.row_data->>'value')::INT >= min_value))
    AND (metric_type_filter IS NULL OR r.row_data->>'type' ILIKE '%' || metric_type_filter || '%')
  ORDER BY
    CASE WHEN r.row_data->>'value' ~ '^[0-9]+$'
         THEN (r.row_data->>'value')::INT
         ELSE 0
    END DESC;
END;
$$;

-- ============================================
-- Test Queries
-- ============================================

-- Test FTS
SELECT COUNT(*) FROM documents WHERE tsv @@ to_tsquery('english', 'snowflake');

-- Test hybrid search
SELECT
  chunk_metadata->>'section',
  frontmatter->>'title',
  vector_score,
  fts_score,
  combined_score
FROM search_hybrid_rag(
  query_text := 'Snowflake data warehouse',
  query_embedding := (SELECT embedding FROM documents LIMIT 1),
  match_count := 5
);

-- Test get full case study
SELECT * FROM get_case_study_full(
  case_study_file_id := (SELECT file_id FROM document_metadata LIMIT 1)
);

-- Test metrics filter
SELECT * FROM get_metrics_by_filter(
  min_value := 80
);
