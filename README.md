# 🎯 Brainforge Proposal & Outreach Writer

AI-powered proposal generation system that reduces proposal writing time from 30-60 minutes to under 5 minutes while maintaining quality scores of 8/10 or higher.

![Status](https://img.shields.io/badge/status-MVP-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Tests](https://img.shields.io/badge/tests-23%2F23%20passing-brightgreen)

---

## 📊 Overview

**What it does:** Generates personalized Upwork proposals and outreach emails using AI-powered research, RAG-based case study matching, and quality assurance.

**Who it's for:** Brainforge BD/sales team members who need to respond to job postings and create outreach emails quickly without sacrificing quality.

**Key Benefits:**
- ⏱️ **Time Savings:** 30-60 min → <5 min (10x faster)
- 📈 **Quality Assurance:** Enforced 8/10+ quality scores
- 🎯 **Personalization:** Company-specific context + relevant project examples
- 📊 **Metrics-Driven:** Automatically references specific project outcomes

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Supabase account (PostgreSQL + PGVector)
- OpenAI API key or Ollama (for LLM + embeddings)
- Brave Search API key (optional, for company research)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd "Pydantic AI for Proposal Writer"
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Set up Supabase database**
- Create a new Supabase project
- Enable PGVector extension
- Run SQL migrations in order:
  ```bash
  # Core schema (documents table)
  psql $DATABASE_URL -f sql/schema.sql

  # Template customization (NEW)
  psql $DATABASE_URL -f db_migrations/001_add_user_preferences.sql
  psql $DATABASE_URL -f db_migrations/002_seed_default_templates.sql
  ```
- Verify tables created: `documents`, `proposal_templates`, `tone_presets`, `user_preferences`, `content_restrictions`

6. **Prepare case study data**
- Convert case studies to markdown format
- Add YAML frontmatter with metadata
- Place in `Files/` directory
- Run RAG pipeline: `python RAG_Pipeline/Local_Files/main.py --directory "./Files"`

7. **Launch the application**
```bash
streamlit run streamlit_ui.py
```

Visit `http://localhost:8501` in your browser.

### 🎨 Configure Templates (Optional)

The system includes 3 templates and 4 tones by default. To customize:

1. **View Available Templates:**
   ```sql
   -- In Supabase SQL Editor
   SELECT name, template_type, description FROM proposal_templates;
   SELECT name, tone_type, description FROM tone_presets;
   ```

2. **Set User Preferences:**
   ```sql
   -- Insert user preference
   INSERT INTO user_preferences (user_id, template_id, tone_id)
   VALUES ('default_user', 'consultative-001', 'conversational-001');
   ```

3. **Add Content Restrictions:**
   ```sql
   -- Add forbidden phrases and required elements
   INSERT INTO content_restrictions (user_id, forbidden_phrases, required_elements, word_count_overrides)
   VALUES (
     'default_user',
     '["competitor_name", "guaranteed", "very *"]',
     '["Python", "experience"]',
     '{"upwork_proposal": {"min": 200, "max": 400}}'
   );
   ```

4. **Create Settings Page (Future):**
   - Navigate to Settings (once UI is built)
   - Select template and tone
   - Configure restrictions
   - Save preferences

For now, preferences are managed via SQL until the Settings UI is implemented.

### 🌐 Deploy to Replit (Alternative to Local Setup)

For cloud deployment on Replit:
1. Import this repository to Replit
2. Add secrets (API keys) via Replit Secrets tab
3. Click Run - Streamlit app launches automatically

**See [REPLIT_DEPLOYMENT.md](REPLIT_DEPLOYMENT.md) for complete deployment guide.**

---

## ⚡ Recent Updates

### PydanticAI 1.39.0 Upgrade (December 2024)

**Breaking Changes Fixed:**
- ✅ Upgraded from PydanticAI v0.0.53 → v1.39.0
- ✅ Fixed `AgentRunResult.data` → `AgentRunResult.output`
- ✅ Updated `result_type` → `output_type` parameter
- ✅ Changed OpenAI model initialization to use environment variables
- ✅ Fixed Pydantic schema generation for `Dict[str, Any]` types

**Impact:**
- All agent tools working correctly with latest PydanticAI API
- Improved stability and performance
- Better error handling and logging

**Migration Guide:**
If you're upgrading from an older version:
1. Update `requirements.txt`: `pip install -r requirements.txt`
2. Ensure environment variables are set (see Configuration section)
3. Restart Streamlit: `streamlit run streamlit_ui.py`

**Commits:**
- `1907b54` - Fix AgentRunResult.output attribute
- `4fd632c` - Preserve full file_id path in search results
- `5b214e5` - Update to PydanticAI 1.39.0 API changes
- `288cad8` - Use environment variables for OpenAI client
- `0422e8a` - Fix Pydantic schema for Any types

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT                                    │
│              (Job Posting or Outreach Context)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  1. PARSE & RESEARCH                             │
│  • Extract company name, technologies, requirements              │
│  • Research company via Brave Search (if mentioned)              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  2. INTELLIGENT SEARCH                           │
│                                                                   │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │  AI/ML Job?      │─────Yes─────▶│ AI Capabilities  │         │
│  │  (chatbot, AI)   │              │      Deck        │         │
│  └──────────────────┘              └──────────────────┘         │
│           │                                                      │
│          No                                                      │
│           ▼                                                      │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │ Data/BI Job?     │─────Yes─────▶│ Data Analytics   │         │
│  │ (Tableau, dbt)   │              │      Deck        │         │
│  └──────────────────┘              └──────────────────┘         │
│                                                                   │
│  PLUS: Search case studies with tech/industry filters            │
│  Result: 1 Deck + 3-4 Case Studies                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  3. RETRIEVE DETAILS                             │
│  • Get 1 capability deck (AI or Data based on context)           │
│  • Get 2-3 case studies (top matches by relevance)               │
│  • Extract metrics, results, testimonials                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  4. GENERATE PROPOSAL                            │
│  • Combine company research + deck + case studies                │
│  • Reference specific metrics (e.g., "90% error reduction")      │
│  • 150-300 words (proposals) or 100-200 words (emails)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  5. QUALITY REVIEW                               │
│  • Automated scoring (must be ≥8/10)                             │
│  • Check: metrics, personalization, structure, length            │
│  • Auto-revise if score <8                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 ✅ FINAL PROPOSAL                                │
│           (Copy-paste ready, quality ≥8/10)                      │
└─────────────────────────────────────────────────────────────────┘
```

**Time:** <5 minutes | **Quality:** ≥8/10 | **References:** 1 deck + 2-3 case studies

---

## 🎨 Features

### Dual-Mode Interface

#### 📝 Upwork Proposal Mode
Generate tailored 150-300 word proposals for Upwork job postings:
- Automatic company research (if mentioned in posting)
- Technology-based project matching
- Specific metrics and examples from past work
- Customizable templates and tones
- Professional tone with clear call-to-action

#### 📧 Outreach Email Mode
Create personalized 100-200 word cold outreach emails:
- Company intelligence gathering via Brave Search
- Industry-based project matching
- Pain point identification
- Customizable writing styles
- Calendly link integration

### 🎨 Template Customization (NEW)

#### Pre-defined Templates
Choose from 3 proposal structure variants:
- **Technical** - Deep technical focus with detailed solution architecture
- **Consultative** - Business-value driven with strategic insights
- **Quick Win** - Fast, results-focused highlighting quick delivery

#### Tone Presets
Select from 4 writing styles:
- **Professional** - Formal, polished tone for corporate communications
- **Conversational** - Friendly, approachable with natural language flow
- **Technical** - Technically precise with industry terminology
- **Friendly** - Warm, personable tone that builds rapport

#### Content Restrictions
Enforce organizational guidelines:
- **Forbidden Phrases** - Block competitor mentions, overpromising terms
- **Required Elements** - Enforce credential references, methodologies
- **Custom Word Counts** - Override default ranges per content type
- **Wildcard Support** - Pattern matching (e.g., "very *" blocks "very good", "very bad")

### 5 Specialized AI Tools

1. **research_company** - Brave Search API integration
   - Company industry, tech stack, recent news
   - Size estimation (startup/SMB/enterprise)
   - Key people and pain points

2. **search_relevant_projects** - Enhanced RAG search
   - Semantic search + metadata filters
   - Filter by: tech_stack, industry, project_type
   - Relevance scoring (0.0-1.0)

3. **get_project_details** - Selective case study retrieval
   - Full document reconstruction
   - Metrics extraction (percentages, dollar amounts, ratings)
   - Section filtering (context, challenge, solution, results)

4. **generate_content** - Template-based generation
   - Content type: upwork_proposal | outreach_email | rfp_response
   - Company research + project examples injection
   - Word count compliance
   - Personalization scoring

5. **review_and_score** - Quality assurance
   - Multi-criteria validation (personalization, specificity, relevance)
   - Weighted scoring: specificity (40%), personalization (30%), structure (20%), length (10%)
   - 8/10 minimum threshold enforcement
   - Auto-revision for low scores

---

## 📖 Usage

### Basic Workflow

1. **Select Mode:** Choose "Upwork Proposal" or "Outreach Email"

2. **Provide Input:**
   - **Upwork:** Paste the full job posting
   - **Outreach:** Enter company name and context

3. **Generate:** Click "Generate Proposal" or "Generate Email"

4. **Review:** Check quality score and generated content

5. **Iterate:** If quality score <8, agent auto-revises

6. **Copy & Send:** Use the copy button to grab final content

### Example: Upwork Proposal

**Input:**
```
Looking for a data analyst to help us migrate our e-commerce analytics
from Google Analytics to a modern data warehouse. Must have experience
with Snowflake, dbt, and Tableau. Our company is GreenLeaf Organics.
```

**Agent Workflow:**
1. Researches GreenLeaf Organics (industry, tech stack, pain points)
2. Searches case studies filtered by: `tech_stack=["Snowflake", "dbt", "Tableau"]`, `industry="E-commerce"`
3. Retrieves full details for top 2-3 matching projects
4. Generates 400-600 word proposal with specific metrics
5. Reviews and scores (must be ≥8/10)
6. Returns final proposal

**Output:** Personalized proposal mentioning GreenLeaf's business, referencing ABC Home case study with "90% error reduction" metric, highlighting relevant Snowflake + dbt experience.

---

## 🗂️ Project Structure

```
.
├── agent.py                 # PydanticAI agent + 10 tool registrations
├── tools.py                 # General tools (web search, RAG, SQL, vision)
├── proposal_tools.py        # 5 specialized proposal writer tools
├── proposal_schemas.py      # 7 Pydantic models for type safety
├── template_schemas.py      # 5 Pydantic models for templates (NEW)
├── template_manager.py      # Template CRUD + prompt customization (NEW)
├── restriction_validator.py # Content filtering engine (NEW)
├── prompt.py                # System prompt for proposal writer
├── clients.py               # Supabase, OpenAI, Mem0 client setup
├── streamlit_ui.py          # Dual-mode web interface
├── db_migrations/           # Database migrations (NEW)
│   ├── 001_add_user_preferences.sql
│   └── 002_seed_default_templates.sql
├── RAG_Pipeline/            # Document ingestion pipelines
│   ├── Local_Files/         # Local directory watcher
│   ├── Google_Drive/        # Google Drive watcher
│   └── common/              # Shared DB handler, text processor
├── Files/                   # Case study markdown files
├── tests/                   # Pytest test suite (23 tests)
│   ├── test_proposal_tools.py
│   ├── test_tools.py
│   └── conftest.py
├── .env.example             # Environment configuration template
├── requirements.txt         # Python dependencies
├── CLAUDE.md                # Development rules and patterns
├── USER_GUIDE.md            # Detailed usage instructions
├── DATA_PREPARATION.md      # Case study preparation guide
└── DEPLOYMENT.md            # Production deployment guide
```

---

## 🧪 Testing

### Run All Tests
```bash
# All proposal writer tests
python -m pytest tests/test_proposal_tools.py -v

# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Coverage
- **Proposal Tools:** 23/23 tests passing (100%)
- **Total Coverage:** 47 passing, 6 pre-existing failures in general tools

### Manual Testing
```bash
# Verify imports
python -c "from proposal_tools import *; print('✓ All tools imported')"

# Check schemas
python -c "from proposal_schemas import *; print('✓ All schemas valid')"

# Test agent setup
python -c "from agent import agent; print('✓ Agent configured with', len(agent._function_tools), 'tools')"
```

---

## 🔧 Configuration

### Environment Variables

Required variables in `.env`:

```bash
# LLM Configuration
LLM_PROVIDER=openai              # openai, azure_openai, anthropic, ollama
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_CHOICE=gpt-4o-mini

# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your-api-key
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# Brave Search (Optional but recommended for company research)
BRAVE_API_KEY=your-brave-key

# Memory (Optional)
DATABASE_URL=postgresql://user:pass@host:5432/db
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed configuration guide.

---

## 📚 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Detailed usage instructions, tips, troubleshooting
- **[DATA_PREPARATION.md](DATA_PREPARATION.md)** - Case study format, metadata schema, RAG ingestion
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment, database setup, environment config
- **[CLAUDE.md](CLAUDE.md)** - Development rules, code patterns, testing standards

---

## 🏗️ Architecture

### System Overview

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Streamlit UI   │    │  PydanticAI      │    │  External APIs   │
│                  │    │  Agent Core      │    │                  │
│  • Proposal Mode │◄──►│  • 10 Tools      │◄──►│  • Brave Search  │
│  • Email Mode    │    │  • RunContext    │    │  • OpenAI LLM    │
│  Port 8501       │    │  • Async Exec    │    │  • Embeddings    │
└──────────────────┘    └──────────────────┘    └──────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                         ┌─────────────────┐
                         │    Supabase     │
                         │                 │
                         │  PostgreSQL +   │
                         │    PGVector     │
                         │                 │
                         │  • documents    │
                         │  • metadata     │
                         │  • embeddings   │
                         └─────────────────┘
                                  ▲
                                  │
                         ┌─────────────────┐
                         │  RAG Pipeline   │
                         │                 │
                         │  • Local Files  │
                         │  • Google Drive │
                         │  • Chunking     │
                         │  • Embedding    │
                         └─────────────────┘
```

### Tech Stack
- **Framework:** PydanticAI v1.39.0 (agent orchestration) ⚠️ **Updated from v0.0.53**
- **UI:** Streamlit v1.44.1
- **Database:** Supabase (PostgreSQL + PGVector v0.3.6)
- **LLMs:** OpenAI, Azure OpenAI, Anthropic, Ollama (configurable)
- **APIs:** Brave Search, OpenAI Embeddings
- **Testing:** pytest + pytest-asyncio + pytest-mock

### Design Patterns
- **Dependency Injection:** AgentDeps dataclass for all tools
- **Type Safety:** Pydantic models for all data structures
- **Async-First:** All I/O operations are async
- **Provider Agnostic:** LLM/embedding providers via environment config
- **Tool Composition:** 5 specialized tools registered with @agent.tool decorator

### RAG Pipeline Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Files     │────▶│   Extract   │────▶│    Chunk    │────▶│   Embed     │
│  .md / PDF  │     │    Text     │     │  (400 chr)  │     │  (OpenAI)   │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                     │
                                                                     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────────────────────┐
│   Query     │────▶│  Semantic   │◄────│      Supabase Store          │
│  (Agent)    │     │   Search    │     │  documents + embeddings      │
└─────────────┘     └─────────────┘     └─────────────────────────────┘
```

---

## 🎯 Quality Standards

### Scoring Criteria
- **Specificity (40%):** Concrete examples with metrics
- **Personalization (30%):** Company context included
- **Structure (20%):** Professional tone, proper sections
- **Length (10%):** Word count compliance
- **No Forbidden Phrases (30%):** Content restriction compliance (when enabled)
- **Required Elements (20%):** Mandatory element presence (when enabled)

### Minimum Thresholds
- **Quality Score:** ≥8.0/10 (enforced)
- **Upwork Proposals:** 150-300 words (customizable)
- **Outreach Emails:** 100-200 words (customizable)
- **Project References:** ≥1 specific example
- **Metrics:** ≥2 concrete numbers/percentages
- **Deck Inclusion:** ≥1 capability deck (AI or Data)
- **Case Studies:** 2-3 relevant project examples

---

## 🐛 Troubleshooting

### Common Issues

**"No results found for company research"**
- Check `BRAVE_API_KEY` is set in `.env`
- Verify company name spelling
- Try using company website or LinkedIn URL

**"No matching projects found"**
- Ensure case studies are ingested via RAG pipeline
- Check `documents` table in Supabase has data
- Verify metadata filters aren't too restrictive

**"Quality score below 8/10"**
- Agent will auto-revise once
- Check if enough case study data is available
- Ensure case studies have metrics in YAML frontmatter

**"Streamlit app won't start"**
- Check all dependencies installed: `pip install -r requirements.txt`
- Verify `.env` file exists and has required variables
- Check port 8501 isn't already in use

See [USER_GUIDE.md](USER_GUIDE.md) for detailed troubleshooting.

---

## 🔒 Security & Best Practices

- **API Keys:** Never commit `.env` to version control
- **Rate Limiting:** Brave Search API has usage limits
- **Data Privacy:** Case studies may contain client information
- **Supabase:** Use service key for server-side operations only
- **Sandboxing:** RestrictedPython used for safe code execution tool

---

## 📈 Performance

### Benchmarks (Target)
- **Proposal Generation:** <5 minutes end-to-end
- **Company Research:** 10-30 seconds (3-10 queries)
- **RAG Search:** 1-3 seconds (4 chunks)
- **Content Generation:** 20-60 seconds (400-600 words)
- **Quality Review:** 10-20 seconds

### Optimization Tips
- Use `response_format="concise"` for faster research
- Reduce `max_results` in search_relevant_projects for speed
- Pre-process case studies during off-hours
- Cache frequently researched companies (future feature)

---

## 🤝 Contributing

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests before committing
python -m pytest tests/ -v

# Follow code style in CLAUDE.md
```

### Code Standards
- **Type hints** on all functions
- **Async** for all I/O operations
- **Pydantic models** for data structures
- **Docstrings** with Args, Returns, Examples
- **Tests** for all new tools (use mocks)

See [CLAUDE.md](CLAUDE.md) for complete development rules.

---

## 📝 License

[Add your license here]

---

## 🙏 Acknowledgments

- **PydanticAI** - Agent framework
- **Supabase** - Database + vector storage
- **Brave Search** - Company intelligence API
- **Streamlit** - Rapid UI development

---

## 📞 Support

- **Issues:** [GitHub Issues](your-repo/issues)
- **Documentation:** [USER_GUIDE.md](USER_GUIDE.md)
- **Email:** [your-support-email]

---

**Built with ❤️ by Ryan Brosas**
