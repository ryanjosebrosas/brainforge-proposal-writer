# SQL Schema Files

This directory contains SQL schemas for setting up the Brainforge Proposal Writer database in Supabase.

## Files

### `schema.sql`
**Complete database setup** - Run this first to set up the entire database structure.

**What it creates:**
- `documents` table - Stores case study chunks with vector embeddings
- `match_documents()` RPC function - Semantic search function
- Indexes for performance (ivfflat for vectors, GIN for metadata)
- Optional: `document_metadata` and `document_rows` tables for structured data

**Usage:**
1. Open Supabase SQL Editor
2. Copy entire contents of `schema.sql`
3. Paste and execute
4. Verify with test queries at bottom of file

## Embedding Dimensions

**IMPORTANT:** The schema defaults to **1536 dimensions** (OpenAI text-embedding-3-small).

### If using OpenAI embeddings:
✅ No changes needed - use `schema.sql` as-is

### If using Ollama embeddings (nomic-embed-text):
⚠️ Change VECTOR(1536) to VECTOR(768) in two places:
1. Line 21: `embedding VECTOR(768)`
2. Line 55: `query_embedding VECTOR(768)`

## Post-Setup Verification

After running the schema, verify with:

```sql
-- 1. Check PGVector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 2. Check documents table
\d documents

-- 3. Check function exists
SELECT proname FROM pg_proc WHERE proname = 'match_documents';

-- 4. Verify indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'documents';
```

Expected output:
- Extension: `vector` with version
- Table: 5 columns (id, content, metadata, embedding, created_at)
- Function: `match_documents`
- Indexes: 3 indexes (embedding_cosine, metadata, created_at)

## Troubleshooting

### "Extension vector does not exist"
- Enable PGVector in Supabase: Database → Extensions → Search for "vector" → Enable

### "Column embedding has wrong type"
- Check your embedding model:
  - OpenAI: VECTOR(1536)
  - Ollama nomic-embed-text: VECTOR(768)
- Drop and recreate table if dimensions are wrong

### "Function match_documents already exists"
- Use `CREATE OR REPLACE FUNCTION` (already in schema.sql)
- Or drop first: `DROP FUNCTION IF EXISTS match_documents;`

## Next Steps

After setting up the database:

1. **Configure environment** (`.env`):
   ```bash
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_SERVICE_KEY=eyJhbGc...
   EMBEDDING_API_KEY=sk-...
   EMBEDDING_MODEL_CHOICE=text-embedding-3-small
   ```

2. **Prepare case studies** (see `../DATA_PREPARATION.md`)

3. **Run RAG ingestion**:
   ```bash
   python RAG_Pipeline/Local_Files/main.py --directory "./Files"
   ```

4. **Test the setup**:
   ```bash
   streamlit run streamlit_ui.py
   ```

## Schema Diagram

```
┌─────────────────────────────────────┐
│           documents                 │
├─────────────────────────────────────┤
│ id (UUID, PK)                      │
│ content (TEXT)                      │
│ metadata (JSONB)                    │
│   ├─ file_id                        │
│   ├─ file_title                     │
│   ├─ industry                       │
│   ├─ project_type                   │
│   ├─ tech_stack []                  │
│   └─ chunk_index                    │
│ embedding (VECTOR(1536))            │
│ created_at (TIMESTAMPTZ)            │
└─────────────────────────────────────┘
           ↓
    match_documents(query_embedding, match_count, filter)
           ↓
    Returns ranked results by similarity
```

## References

- **Main Documentation:** `../DEPLOYMENT.md` (Database Configuration section)
- **Data Format:** `../DATA_PREPARATION.md`
- **PGVector Docs:** https://github.com/pgvector/pgvector
- **Supabase Docs:** https://supabase.com/docs/guides/database/extensions/pgvector
