# 🚀 Deployment Guide - Brainforge Proposal Writer

Complete guide for deploying the Brainforge Proposal Writer to production environments.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [API Keys & Services](#api-keys--services)
5. [Initial Data Load](#initial-data-load)
6. [Deployment Options](#deployment-options)
7. [Production Configuration](#production-configuration)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Security Best Practices](#security-best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before deploying to production:

### Code Readiness
- [ ] All unit tests passing (`python -m pytest tests/`)
- [ ] Environment variables documented in `.env.example`
- [ ] No hardcoded API keys or secrets in code
- [ ] All TODO/FIXME items resolved
- [ ] Git repository is up to date

### Data Readiness
- [ ] At least 10-15 case studies prepared (50+ recommended)
- [ ] Case studies have valid YAML frontmatter
- [ ] Metrics validated and accurate
- [ ] RAG ingestion pipeline tested locally

### Service Accounts
- [ ] Supabase project created and configured
- [ ] OpenAI API account (or alternative LLM provider)
- [ ] Brave Search API account (optional but recommended)
- [ ] Email/notification service configured (if needed)

### Documentation
- [ ] README.md reviewed
- [ ] USER_GUIDE.md accessible to team
- [ ] DATA_PREPARATION.md shared with content team
- [ ] Admin credentials documented securely

---

## Environment Setup

### 1. Python Environment

**Requirements:**
- Python 3.11 or higher
- pip 23.0 or higher
- Virtual environment tool (venv, conda, poetry)

**Installation:**
```bash
# Clone repository
git clone <your-repo-url>
cd "Pydantic AI for Proposal Writer"

# Create virtual environment
python -m venv venv

# Activate
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

**Critical Variables:**

```bash
# ===== LLM Configuration (REQUIRED) =====
LLM_PROVIDER=openai                      # or azure_openai, anthropic, ollama
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-proj-...                  # Your actual API key
LLM_CHOICE=gpt-4o-mini                   # Model name

# Vision model for image analysis
VISION_LLM_CHOICE=gpt-4o-mini

# ===== Embedding Configuration (REQUIRED) =====
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=sk-proj-...            # Can be same as LLM_API_KEY
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# ===== Supabase (REQUIRED) =====
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...          # Service role key, NOT anon key

# ===== Brave Search (OPTIONAL but recommended) =====
BRAVE_API_KEY=BSA...                     # Get from https://api.search.brave.com

# ===== Memory (OPTIONAL) =====
DATABASE_URL=postgresql://postgres.pooler:password@aws-0-region.pooler.supabase.com:6543/postgres

# ===== Alternative Search (OPTIONAL) =====
SEARXNG_BASE_URL=http://localhost:8081   # If using SearXNG instead of Brave
```

### 3. Verify Configuration

```bash
# Test imports
python -c "from agent import agent; print('✓ Agent loaded')"

# Test database connection
python -c "from clients import get_agent_clients; embedding_client, supabase = get_agent_clients(); print('✓ Clients connected')"

# Count registered tools
python -c "from agent import agent; print(f'✓ {len(agent._function_tools)} tools registered')"
```

---

## Database Configuration

### Supabase Setup

#### Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Create new project
3. Choose region closest to your users
4. Set strong database password (save in password manager)
5. Wait for project initialization (~2 minutes)

#### Step 2: Enable PGVector Extension

In Supabase SQL Editor, run:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

#### Step 3: Create Documents Table

```sql
-- Create documents table for RAG
CREATE TABLE documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL,
    embedding VECTOR(1536),  -- For OpenAI text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for metadata queries
CREATE INDEX idx_documents_metadata ON documents USING GIN (metadata);
```

**For Ollama embeddings (768 dimensions):**
```sql
-- Change embedding dimension
ALTER TABLE documents
ALTER COLUMN embedding TYPE VECTOR(768);
```

#### Step 4: Create RPC Function for Similarity Search

```sql
-- Function to match documents by embedding similarity
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding VECTOR(1536),
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
```

#### Step 5: Create Tables for Structured Data (Optional)

If using SQL query tool for structured data:

```sql
-- Table metadata for document schemas
CREATE TABLE document_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    file_id TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    schema JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for document rows
CREATE TABLE document_rows (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    dataset_id TEXT NOT NULL,
    row_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (dataset_id) REFERENCES document_metadata(file_id)
);

CREATE INDEX idx_document_rows_dataset ON document_rows(dataset_id);
CREATE INDEX idx_document_rows_data ON document_rows USING GIN (row_data);
```

#### Step 6: Optional - Mem0 Memory Tables

If using Mem0 for long-term memory:

```sql
-- Mem0 creates its own tables automatically
-- Just ensure DATABASE_URL points to your Supabase pooler connection string
```

#### Step 7: Get API Credentials

1. Navigate to Project Settings → API
2. Copy **Project URL** → `SUPABASE_URL`
3. Copy **service_role secret** → `SUPABASE_SERVICE_KEY`
   - ⚠️ Never use the `anon` key for backend operations

---

## API Keys & Services

### OpenAI API

1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `.env` as `LLM_API_KEY` and `EMBEDDING_API_KEY`
4. Set usage limits in OpenAI dashboard (recommended)

**Estimated Costs:**
- Proposal generation: ~$0.05-$0.20 per proposal (with gpt-4o-mini)
- Embeddings: ~$0.001 per case study
- Monthly (100 proposals): ~$10-$20

### Brave Search API

1. Go to https://brave.com/search/api/
2. Sign up for free tier (2,000 queries/month)
3. Navigate to https://api.search.brave.com/app/keys
4. Create new API key
5. Copy to `.env` as `BRAVE_API_KEY`

**Limits:**
- Free: 2,000 queries/month
- Paid: Starting at $5/month for 20,000 queries

### Alternative LLM Providers

**Anthropic Claude:**
```bash
LLM_PROVIDER=anthropic
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_API_KEY=sk-ant-...
LLM_CHOICE=claude-sonnet-4.5
```

**Azure OpenAI:**
```bash
LLM_PROVIDER=azure_openai
LLM_BASE_URL=https://your-resource.openai.azure.com/
LLM_API_KEY=your-azure-key
LLM_CHOICE=gpt-4o
```

**Ollama (Local):**
```bash
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_CHOICE=qwen2.5:14b-instruct-8k
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL_CHOICE=nomic-embed-text
```

---

## Initial Data Load

### Step 1: Prepare Case Studies

Follow [DATA_PREPARATION.md](DATA_PREPARATION.md) to:
1. Convert case studies to markdown
2. Add YAML frontmatter
3. Place in `Files/` directory

### Step 2: Run RAG Ingestion

```bash
# From project root
python RAG_Pipeline/Local_Files/main.py --directory "./Files"
```

**Monitor progress:**
```
Processing: ABC_Home_Workflow_Automation.md
  ✓ Extracted text (1,247 chars)
  ✓ Created 4 chunks
  ✓ Generated embeddings
  ✓ Inserted into Supabase

Processed: 1/15 files
Estimated time remaining: 3 minutes
```

### Step 3: Verify Data Load

**Check Supabase:**
```sql
-- Count documents
SELECT COUNT(*) FROM documents;

-- Sample metadata
SELECT metadata->>'file_title', metadata->>'industry', metadata->>'tech_stack'
FROM documents
LIMIT 10;

-- Verify embeddings
SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL;
```

**Test RAG search:**
```python
from clients import get_agent_clients
from tools import get_embedding
import asyncio

async def test_rag():
    embedding_client, supabase = get_agent_clients()
    query = "e-commerce analytics dashboard"
    embedding = await get_embedding(query, embedding_client)
    results = supabase.rpc('match_documents', {
        'query_embedding': embedding,
        'match_count': 3
    }).execute()
    print(f"Found {len(results.data)} matches")
    for doc in results.data:
        print(f"- {doc['metadata']['file_title']} (similarity: {doc['similarity']:.3f})")

asyncio.run(test_rag())
```

---

## Deployment Options

### Option 1: Streamlit Cloud (Easiest)

**Pros:** Zero infrastructure, free tier available, easy SSL
**Cons:** Limited to Streamlit apps, may have cold starts

**Steps:**
1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect GitHub account
4. Select repository and branch
5. Set `streamlit_ui.py` as main file
6. Add environment variables in "Advanced settings"
7. Deploy!

**Environment Variables in Streamlit Cloud:**
- Click "Advanced settings" → "Secrets"
- Paste your `.env` contents in TOML format:
```toml
LLM_PROVIDER = "openai"
LLM_API_KEY = "sk-proj-..."
SUPABASE_URL = "https://..."
# ... etc
```

### Option 2: Docker (Recommended for Production)

**Pros:** Consistent environment, easy scaling, works anywhere
**Cons:** Requires Docker knowledge

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "streamlit_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  proposal-writer:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Deploy:**
```bash
docker-compose up -d
```

### Option 3: Traditional VPS (AWS, DigitalOcean, etc.)

**For Ubuntu 22.04:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Clone repository
git clone <your-repo>
cd "Pydantic AI for Proposal Writer"

# Create venv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment
cp .env.example .env
nano .env  # Edit with your keys

# Run with systemd (see below)
```

**systemd service (`/etc/systemd/system/proposal-writer.service`):**
```ini
[Unit]
Description=Brainforge Proposal Writer
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/proposal-writer
Environment="PATH=/var/www/proposal-writer/venv/bin"
ExecStart=/var/www/proposal-writer/venv/bin/streamlit run streamlit_ui.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable proposal-writer
sudo systemctl start proposal-writer
sudo systemctl status proposal-writer
```

### Option 4: Kubernetes (Enterprise)

**For large-scale deployments:**

See `kubernetes/` directory for:
- Deployment manifests
- Service definitions
- Ingress configuration
- Secret management

---

## Production Configuration

### Streamlit Production Settings

Create ``.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Environment-Specific Variables

**Development:**
```bash
LLM_CHOICE=gpt-4o-mini  # Cheaper
BRAVE_API_KEY=          # Optional
```

**Production:**
```bash
LLM_CHOICE=gpt-4o       # Better quality
BRAVE_API_KEY=BSA...    # Required for best results
```

### Logging Configuration

Add to `streamlit_ui.py`:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proposal_writer.log'),
        logging.StreamHandler()
    ]
)
```

---

## Monitoring & Maintenance

### Health Checks

**Endpoint:** `http://your-domain:8501/_stcore/health`

**Monitor:**
- Streamlit process running
- Supabase connection
- API key validity
- Disk space for logs

### Usage Metrics

Track:
- Proposals generated per day
- Average quality scores
- API costs (OpenAI dashboard)
- RAG search performance
- User satisfaction

### Regular Maintenance

**Weekly:**
- [ ] Review generated proposals for quality
- [ ] Check error logs
- [ ] Monitor API costs

**Monthly:**
- [ ] Update case studies (add new projects)
- [ ] Re-run RAG ingestion for new data
- [ ] Review and update prompt.py if needed
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`

**Quarterly:**
- [ ] Full data audit (case study accuracy)
- [ ] Performance optimization
- [ ] Security audit
- [ ] Backup Supabase database

### Backup Strategy

**Supabase Backups:**
- Automatic daily backups (Pro plan)
- Manual backups via Supabase dashboard
- Export `documents` table weekly:
```bash
# Using Supabase CLI
supabase db dump -f backup.sql
```

**Case Studies:**
- Keep `Files/` directory in version control
- Separate backup in Google Drive or S3
- Document conversion scripts backed up

---

## Security Best Practices

### API Key Security

✅ **DO:**
- Store keys in `.env` file (never commit)
- Use environment-specific keys (dev vs prod)
- Rotate keys quarterly
- Set OpenAI usage limits
- Use read-only keys where possible

❌ **DON'T:**
- Hardcode keys in code
- Share keys via email/Slack
- Use same key across environments
- Commit `.env` to git

### Supabase Security

**Row Level Security (RLS):**
```sql
-- Enable RLS on documents table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy for service key only
CREATE POLICY "Service role full access"
ON documents
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);
```

**API Security:**
- Use service_role key for backend only
- Never expose service key to frontend
- Set up database roles with minimal permissions

### Network Security

**Firewall rules:**
- Allow only ports 22 (SSH), 443 (HTTPS), 8501 (Streamlit)
- Restrict SSH to specific IPs
- Use fail2ban for brute force protection

**SSL/TLS:**
- Use Let's Encrypt for free SSL
- Force HTTPS redirects
- Use HSTS headers

### Data Privacy

**Client Data:**
- Anonymize client names if needed
- Remove sensitive metrics before case study ingestion
- GDPR compliance for EU clients
- Regular data audits

---

## Troubleshooting

### Deployment Issues

**"Module not found" errors:**
```bash
pip install --upgrade -r requirements.txt
```

**"Port already in use":**
```bash
# Kill process on port 8501
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux
sudo lsof -t -i:8501 | xargs kill -9
```

**"Supabase connection failed":**
- Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
- Verify Supabase project is active
- Test connection: `psql $DATABASE_URL`

### Runtime Issues

**"No results from RAG":**
- Verify documents table has data: `SELECT COUNT(*) FROM documents;`
- Check embeddings exist: `SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL;`
- Re-run ingestion if needed

**"Quality scores always low":**
- Add more case studies (need 50+ for best results)
- Ensure case studies have metrics in YAML
- Enable Brave API for company research

**"API rate limit errors":**
- Check OpenAI usage dashboard
- Implement request throttling
- Upgrade API plan if needed

---

## Post-Deployment Checklist

After deployment:

- [ ] Test both modes (Upwork + Outreach)
- [ ] Generate 3-5 test proposals
- [ ] Verify quality scores ≥8/10
- [ ] Check Brave API integration
- [ ] Test RAG matching with different queries
- [ ] Verify all environment variables work
- [ ] Set up monitoring/alerts
- [ ] Document admin credentials
- [ ] Train team on USER_GUIDE.md
- [ ] Schedule regular maintenance

---

## Support & Resources

- **README:** [README.md](README.md)
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **Data Prep:** [DATA_PREPARATION.md](DATA_PREPARATION.md)
- **Dev Guide:** [CLAUDE.md](CLAUDE.md)

**External Resources:**
- [Streamlit Docs](https://docs.streamlit.io/)
- [Supabase Docs](https://supabase.com/docs)
- [PydanticAI Docs](https://ai.pydantic.dev/)
- [OpenAI API Docs](https://platform.openai.com/docs)

---

**Ready for Production! 🚀**
