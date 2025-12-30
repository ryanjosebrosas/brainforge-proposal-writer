# Deploying Brainforge Proposal Writer to Replit

This guide walks you through deploying the Streamlit proposal writer application on Replit.

## 🚀 Quick Setup (5 minutes)

### 1. Import to Replit

1. Go to [Replit](https://replit.com)
2. Click **"Create Repl"**
3. Choose **"Import from GitHub"**
4. Paste your repository URL
5. Replit will auto-detect the `.replit` configuration

### 2. Configure Environment Secrets

Click the **🔒 Secrets** tab (lock icon in left sidebar) and add these variables:

#### Required Secrets

```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-openai-api-key-here
LLM_CHOICE=gpt-4o-mini

# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your-openai-api-key-here
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# Supabase (Required for RAG)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-supabase-service-key
```

#### Optional Secrets

```bash
# Brave Search (for company research - highly recommended)
BRAVE_API_KEY=your-brave-api-key

# Memory (optional)
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### 3. Install Dependencies

Replit will automatically install from `requirements.txt` on first run. If needed, manually run:

```bash
pip install -r requirements.txt
```

### 4. Set Up Supabase Database

Before running, ensure your Supabase database is set up:

1. Go to your Supabase project SQL Editor
2. Run the schema from `sql/schema.sql`
3. Run the hybrid search migration: `sql/add_fts_and_hybrid_search.sql`
4. Verify tables exist: `documents`, `document_metadata`, `document_rows`

### 5. Ingest Case Studies (One-time Setup)

**Important:** This step must be done locally (NOT on Replit) before deployment:

```bash
# On your local machine:
python RAG_Pipeline/Local_Files/batch_ingest.py "brainforge md files/case study"
python RAG_Pipeline/Local_Files/batch_ingest.py "brainforge md files/deck"
```

This uploads your case studies and capability decks to Supabase. You only need to do this once.

### 6. Run the App

Click the **▶️ Run** button at the top of Replit. The Streamlit app will launch at:

```
https://your-repl-name.your-username.repl.co
```

---

## 🔧 Configuration Details

### .replit File

The `.replit` file is already configured with:
- **Run command:** `streamlit run streamlit_ui.py --server.port 8501 --server.address 0.0.0.0`
- **Port forwarding:** 8501 → 80 (external)
- **Deployment target:** Cloud Run (auto-scaling)

### replit.nix File

Specifies Python 3.11 environment with required system dependencies.

### Environment Variables

All secrets are loaded from Replit Secrets (encrypted storage) via `python-dotenv` in `clients.py`.

---

## 🧪 Testing the Deployment

Once running, test both modes:

### Upwork Proposal Mode
1. Select "Upwork Proposal" mode
2. Paste a sample job posting (e.g., looking for data analyst with Snowflake experience)
3. Click "Generate Proposal"
4. Verify:
   - Company research runs (if company mentioned and Brave API key set)
   - Relevant case studies retrieved
   - Quality score ≥8/10
   - Generation time <5 minutes

### Outreach Email Mode
1. Select "Outreach Email" mode
2. Enter company name + context
3. Click "Generate Email"
4. Verify:
   - Company intelligence gathered
   - Industry-relevant projects referenced
   - Word count 100-200
   - Quality score ≥8/10

---

## 🐛 Troubleshooting

### "No module named 'X'"
**Solution:** Click **Shell** tab and run `pip install -r requirements.txt`

### "Unable to connect to Supabase"
**Solution:**
- Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in Secrets
- Verify URL format: `https://xxxxx.supabase.co` (no trailing slash)
- Test connection in Shell: `python -c "from clients import get_agent_clients; get_agent_clients()"`

### "No results found for company research"
**Solution:**
- Add `BRAVE_API_KEY` to Secrets (get free key at https://brave.com/search/api/)
- Or: The agent will skip research and proceed with RAG search only

### "No matching projects found"
**Solution:**
- Ensure case studies are ingested (see Step 5)
- Check Supabase `documents` table has data
- Run query: `SELECT COUNT(*) FROM documents;` (should be >0)

### Port 8501 already in use
**Solution:** Replit handles port management automatically. Just restart the Repl.

---

## 📊 Performance Expectations

- **First Run:** 30-60 seconds (cold start + dependency loading)
- **Subsequent Runs:** <10 seconds
- **Proposal Generation:** 2-5 minutes (depends on LLM speed)
- **Memory Usage:** ~200-300 MB

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Use Replit Secrets only
2. **Use service role key for Supabase** - Not anon key (required for RPC functions)
3. **Keep Brave API key private** - Has usage limits
4. **Rotate keys periodically** - Especially if shared access

---

## 🚀 Production Deployment (Optional)

For production use beyond Replit:

1. **Always-On Repl:**
   - Upgrade to Replit Hacker plan ($7/month)
   - Enable "Always On" in Repl settings
   - Prevents cold starts

2. **Custom Domain:**
   - Go to Repl settings → Domains
   - Add custom domain (e.g., `proposals.brainforge.com`)
   - Update DNS records as instructed

3. **Monitoring:**
   - Check logs via Replit Console
   - Monitor Supabase usage dashboard
   - Track API usage (OpenAI, Brave)

---

## 📝 Updating the Deployment

### To update code:
1. Push changes to GitHub
2. In Replit, go to Version Control tab
3. Click "Pull" to sync latest changes
4. Restart the Repl

### To add new case studies:
1. Add markdown files to `brainforge md files/case study/`
2. Run ingestion locally: `python RAG_Pipeline/Local_Files/batch_ingest.py "brainforge md files/case study"`
3. New studies automatically available in Replit app (no restart needed)

---

## 🆘 Support

- **Documentation:** See `README.md`, `USER_GUIDE.md`, `DEPLOYMENT.md`
- **Issues:** Check existing GitHub issues or create a new one
- **Logs:** Click Shell tab → Run `streamlit run streamlit_ui.py` to see verbose output

---

**Last Updated:** 2025-12-29
**Tested on:** Replit Python 3.11, Streamlit 1.44.1
**Status:** ✅ Production Ready
