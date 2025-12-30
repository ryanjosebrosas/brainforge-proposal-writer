# 🚀 Quick Start: Database Setup & RAG Ingestion

**Complete workflow from zero to working proposal writer in 15 minutes.**

---

## Prerequisites

- ✅ Converted case studies to markdown (with YAML frontmatter)
- ✅ Supabase account created
- ✅ OpenAI API key (or Ollama running locally)
- ✅ Environment variables configured in `.env`

---

## Step 1: Database Setup (5 minutes)

### Option A: Fresh Install (New Database)

**In Supabase SQL Editor:**

```sql
-- Just run this one file - it does everything!
-- Copy and paste: sql/schema.sql
```

**What it creates:**
- ✅ PGVector extension
- ✅ `documents` table with embeddings
- ✅ Vector similarity indexes
- ✅ `match_documents()` RPC function

### Option B: Reset Project Tables Only

**If you want to keep other Supabase tables but reset proposal writer data:**

```sql
-- Step 1: Reset project tables only
-- Copy and paste: sql/reset.sql

-- Step 2: Recreate tables
-- Copy and paste: sql/schema.sql
```

### Option C: Complete Database Wipe (Nuclear Option)

**If you want to delete EVERYTHING in Supabase and start from zero:**

```sql
-- Step 1: FULL RESET (⚠️⚠️⚠️ DELETES ALL TABLES)
-- Copy and paste: sql/reset_full.sql

-- Step 2: Recreate tables
-- Copy and paste: sql/schema.sql
```

### Verify Setup

```sql
-- Quick verification (should return 3 rows)
SELECT 'PGVector' as component, COUNT(*)::text as status FROM pg_extension WHERE extname = 'vector'
UNION ALL
SELECT 'documents table', COUNT(*)::text FROM information_schema.tables WHERE table_name = 'documents'
UNION ALL
SELECT 'match_documents', COUNT(*)::text FROM pg_proc WHERE proname = 'match_documents';
```

**Expected output:**
```
component          | status
-------------------|--------
PGVector          | 1
documents table   | 1
match_documents   | 1
```

---

## Step 2: Prepare Your Files (2 minutes)

### Directory Structure

```
Files/
├── Brainforge_AI_Capabilities.md          # AI/ML capability deck
├── Brainforge_Data_Capabilities.md        # Data/Analytics deck
├── ABC_Home_Case_Study.md                 # Case study 1
├── Amazon_Dashboard_Case_Study.md         # Case study 2
├── Healthcare_AI_Case_Study.md            # Case study 3
└── ... (more case studies)
```

### Check Your Files

**Verify frontmatter format:**

```bash
# On Windows
type Files\ABC_Home_Case_Study.md | findstr /C:"---" /C:"title:" /C:"industry:"

# On Linux/Mac
head -20 Files/ABC_Home_Case_Study.md | grep -E "^(---|title:|industry:|project_type:)"
```

**Should see:**
```yaml
---
title: "Project Name"
client: "Client Name"
industry: "E-commerce"
project_type: "AI_ML"
tech_stack: ["Python", "FastAPI"]
---
```

---

## Step 3: RAG Ingestion (5 minutes)

### Run the Ingestion Pipeline

```bash
# From project root
python RAG_Pipeline/Local_Files/main.py --directory "./Files"
```

### What You'll See

```
Starting RAG ingestion for directory: ./Files
Found 10 markdown files to process...

Processing: Brainforge_AI_Capabilities.md
  ✓ Extracted YAML frontmatter
  ✓ Created 8 chunks (400 chars each)
  ✓ Generated embeddings (1536 dims)
  ✓ Inserted 8 chunks into Supabase

Processing: ABC_Home_Case_Study.md
  ✓ Extracted YAML frontmatter
  ✓ Created 12 chunks
  ✓ Generated embeddings
  ✓ Inserted 12 chunks into Supabase

... (continues for all files)

✅ Ingestion complete!
Total files processed: 10
Total chunks created: 95
Total time: 3m 45s
```

### Verify Ingestion

**In Supabase SQL Editor:**

```sql
-- Count total documents
SELECT COUNT(*) as total_chunks FROM documents;

-- Count by file
SELECT
    metadata->>'file_title' as file,
    COUNT(*) as chunks
FROM documents
GROUP BY metadata->>'file_title'
ORDER BY chunks DESC;

-- Verify embeddings exist
SELECT COUNT(*) as chunks_with_embeddings
FROM documents
WHERE embedding IS NOT NULL;
```

---

## Step 4: Test RAG Search (3 minutes)

### Test Semantic Search

```sql
-- Test 1: Find AI-related projects
SELECT
    metadata->>'file_title' as title,
    metadata->>'project_type' as type,
    similarity
FROM match_documents(
    query_embedding := (
        SELECT embedding
        FROM documents
        WHERE metadata->>'file_title' ILIKE '%AI%'
        LIMIT 1
    ),
    match_count := 5
)
ORDER BY similarity DESC;
```

**Expected:** Returns 5 most similar documents with similarity scores (0.7-0.95)

### Test Metadata Filtering

```sql
-- Test 2: Find all e-commerce projects
SELECT DISTINCT
    metadata->>'file_title' as project,
    metadata->>'industry' as industry,
    metadata->>'project_type' as type
FROM documents
WHERE metadata->>'industry' = 'E-commerce';
```

**Expected:** Returns all e-commerce case studies

### Test Technology Search

```sql
-- Test 3: Find projects using Python
SELECT DISTINCT
    metadata->>'file_title' as project,
    metadata->'tech_stack' as technologies
FROM documents
WHERE metadata->'tech_stack' ? 'Python'
LIMIT 10;
```

**Expected:** Returns projects with Python in tech_stack

---

## Step 5: Test the Proposal Writer (3 minutes)

### Launch Streamlit

```bash
streamlit run streamlit_ui.py
```

### Generate a Test Proposal

**Paste this sample job posting:**

```
We're looking for an AI developer to build a customer support chatbot
for our e-commerce platform. Must have experience with OpenAI, Python,
and FastAPI. Our company sells sustainable home products.

Requirements:
- Build conversational AI agent
- Integrate with existing CRM
- Handle 100+ conversations/day
- Response time <2 seconds

Budget: $8,000-$12,000
```

### What Should Happen

**The agent will:**
1. ✅ Parse job posting (AI, chatbot, e-commerce)
2. ✅ Search for "AI capabilities deck"
3. ✅ Search for AI/chatbot case studies
4. ✅ Retrieve 1 deck + 2-3 case studies
5. ✅ Generate proposal with specific metrics
6. ✅ Score quality (should be ≥8/10)

**Output should include:**
- Reference to AI capabilities deck
- 2-3 specific case study examples
- Metrics like "85% automation" or "90% error reduction"
- Quality score ≥8/10

---

## 🎯 Success Checklist

After completing all steps, verify:

### Database
- [ ] PGVector extension enabled
- [ ] `documents` table exists with data
- [ ] Embeddings column populated (all rows have vectors)
- [ ] Metadata contains frontmatter fields
- [ ] `match_documents()` function works

### Files
- [ ] 10-15+ case studies in `Files/` directory
- [ ] All files have valid YAML frontmatter
- [ ] At least 1 AI deck + 1 Data deck
- [ ] Files follow naming convention

### RAG Pipeline
- [ ] Ingestion completed without errors
- [ ] Total chunks ≥50 (from 10-15 files)
- [ ] Semantic search returns relevant results
- [ ] Metadata filtering works

### Proposal Writer
- [ ] Streamlit UI loads without errors
- [ ] Can generate proposal for AI job
- [ ] Can generate proposal for Data job
- [ ] Quality scores ≥8/10
- [ ] References specific case studies

---

## 🐛 Troubleshooting

### Issue: "PGVector extension not found"

**Solution:**
```sql
-- In Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue: "No results from RAG search"

**Verify data exists:**
```sql
SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL;
```

**If 0 rows:** Re-run ingestion pipeline

### Issue: "Quality scores always <8"

**Possible causes:**
- Not enough case studies (need 10+ minimum)
- Missing metrics in frontmatter
- Brave API not configured (company research disabled)

**Fix:**
1. Add more case studies with metrics
2. Check `.env` has `BRAVE_API_KEY`
3. Verify frontmatter has `key_metrics` field

### Issue: "Embeddings dimension mismatch"

**Error:** `vector has 768 dimensions but expected 1536`

**Fix:** You're using Ollama but schema expects OpenAI dimensions

**Reset and fix:**
```sql
-- Run reset.sql first
-- Then edit schema.sql line 21 and 55:
-- Change VECTOR(1536) to VECTOR(768)
-- Then run schema.sql
```

---

## 📚 Next Steps

After successful setup:

1. **Add more case studies** - Aim for 50+ for best results
2. **Test different job types** - AI vs Data/BI proposals
3. **Review quality scores** - Iterate on frontmatter if scores low
4. **Deploy to production** - See `DEPLOYMENT.md`
5. **Set up monitoring** - Track usage and quality over time

---

## 🆘 Need Help?

**Documentation:**
- `sql/README.md` - SQL setup details
- `DATA_PREPARATION.md` - Case study formatting
- `USER_GUIDE.md` - Using the proposal writer
- `DEPLOYMENT.md` - Production deployment

**Common Issues:**
- Check `sql/test_queries.sql` for debugging queries
- Review logs: `python RAG_Pipeline/Local_Files/main.py` output
- Verify `.env` file has all required variables

---

## 🎉 You're Done!

Your proposal writer is now fully operational! Start generating high-quality, personalized proposals in under 5 minutes.

**Time to first proposal:** ~15 minutes
**Quality score target:** ≥8/10
**Case studies needed:** 10-15 minimum, 50+ recommended
