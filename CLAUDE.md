# Brainforge Proposal Writer - Global Development Rules

## 1. Core Principles

**CRITICAL: ARCHON-FIRST TASK MANAGEMENT**
- ALWAYS use Archon MCP server for task tracking (NOT TodoWrite)
- Check `find_tasks()` before starting any work
- Update task status: `todo` → `doing` → `review` → `done`
- Never code without an active task in Archon

**YAGNI (You Aren't Gonna Need It)**
- Only implement what's explicitly required RIGHT NOW
- Don't add "nice to have" features or future-proofing
- No speculative generalization or abstraction
- Follow PRD.md - if it's not in scope, don't build it
- Prefer simple solutions over clever ones

**Type Safety First**
- Use Pydantic models for ALL data structures
- Use type hints on ALL functions and variables
- No `Any` types without explicit justification

**Async Everything**
- All I/O operations MUST be async (database, HTTP, embeddings)
- Use `AsyncClient`, `AsyncOpenAI`, async Supabase patterns
- Never block the event loop

**Provider Agnostic**
- LLM providers configured via environment variables (OpenAI, Azure, Anthropic, Ollama)
- Embedding providers configurable (OpenAI, Ollama)
- No hardcoded provider-specific logic

**Documentation Standards**
- Every tool has detailed docstring with Args, Returns, Examples
- PRD.md is source of truth for requirements
- Code comments explain "why", not "what"

## 2. Tech Stack

- **Python 3.11+** with PydanticAI v0.0.53 (agent framework)
- **LLM Providers:** OpenAI, Azure OpenAI, Anthropic, Ollama (configurable via .env)
- **Data:** Supabase (PostgreSQL + PGVector v0.3.6), Mem0 v0.1.102 (memory)
- **APIs:** Brave Search (company research), OpenAI Embeddings (text-embedding-3-small)
- **UI:** Streamlit v1.44.1, httpx v0.28.1 (async HTTP)
- **Testing:** pytest v8.3.5, pytest-asyncio v0.26.0, pytest-mock v3.14.0
- **Tools:** RestrictedPython v8.0 (safe code execution), python-dotenv

## 3. Architecture

### Project Structure
```
.
├── agent.py                 # PydanticAI agent + tool registration
├── tools.py                 # Tool implementations (web search, RAG, SQL, vision, code exec)
├── prompt.py                # System prompt
├── clients.py               # Supabase, OpenAI, Mem0 client setup
├── streamlit_ui.py          # Web interface
├── RAG_Pipeline/
│   ├── common/              # Shared DB handler, text processor
│   ├── Google_Drive/        # Drive file watcher
│   └── Local_Files/         # Local file watcher
├── tests/                   # Unit tests
├── Files/                   # Sample case studies (markdown)
├── .env                     # Environment config (not in git)
└── .env.example             # Template

```

### Agent Pattern
- **AgentDeps dataclass** - Dependency injection for all tools
- **@agent.tool decorator** - Register tools with PydanticAI
- **RunContext[AgentDeps]** - Access deps in tool functions
- **System prompt injection** - Via @agent.system_prompt decorator

### RAG Pipeline Pattern
- **Chunking** - 400 char chunks with configurable overlap
- **Embedding** - OpenAI or Ollama embeddings
- **Storage** - Supabase documents table with JSONB metadata
- **Retrieval** - match_documents RPC function (pgvector similarity)

### Tool Design Principles (Anthropic)
- Consolidate related operations
- Search with filters, not list-all
- Response format control (concise vs detailed)
- Token efficiency via pagination
- Actionable error messages

## 4. Code Style

### Naming Conventions
```python
# snake_case for functions, variables, modules
async def research_company(company_name: str) -> CompanyResearch:
    pass

# PascalCase for classes and Pydantic models
class CompanyResearch(BaseModel):
    company_name: str
    industry: str

# UPPER_CASE for constants
MAX_RETRIES = 3
DEFAULT_CHUNK_SIZE = 400

# Prefix protected with _
def _internal_helper():
    pass

# Prefix private with __ (name mangling)
def __private_method():
    pass
```

### Import Organization (PEP 8)
```python
# 1. System imports
import os
import sys
from pathlib import Path
from typing import List, Optional

# 2. Third-party imports
from httpx import AsyncClient
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from supabase import Client

# 3. Local imports
from agent import AgentDeps
from tools import research_company
```

**Rules:**
- Three sections separated by blank lines
- Alphabetize within each section
- Import full modules when possible
- Avoid `from x import y` for functions (prevents circular imports)
- OK for classes and types

### Code Style Patterns
```python
# Truthiness checks - prefer implicit over explicit
if company_name:  # Good
    process()
if not results:  # Good
    handle_empty()
if value is None:  # Good - explicit None check
    set_default()

# AVOID
if company_name == True:  # Wrong
    pass
if len(results) == 0:  # Wrong - use "if not results:"
    pass

# List comprehensions over loops
filtered = [p for p in projects if p.score > 0.8]
ids = [doc['id'] for doc in documents]

# Context managers for resources
with open('data.json') as f:
    data = json.load(f)

async with AsyncClient() as client:
    response = await client.get(url)

# Line continuations with parentheses (keep under 100 chars)
result = research_company(
    ctx=context,
    company_name="Very Long Company Name Inc",
    response_format="detailed"
)
```

**Rules:**
- Use truthiness: `if attr:` not `if attr == True:`
- Always use `with` for file/resource operations
- Prefer comprehensions for simple transformations
- Keep lines under 100 characters
- Use 4 spaces (not tabs)

### Pydantic Model Pattern
```python
from pydantic import BaseModel, Field

class CompanyResearch(BaseModel):
    """Company intelligence from web research."""
    company_name: str = Field(..., description="Official company name")
    industry: str = Field(..., description="Primary industry")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies used")
    sources: List[str] = Field(default_factory=list, description="Source URLs")

    # No __init__, use model_validate() to create instances
    # Use .model_dump_json() to serialize for PydanticAI tools
```

### Async Function Pattern
```python
async def research_company(
    ctx: RunContext[AgentDeps],
    company_name: str,
    response_format: Literal["concise", "detailed"] = "concise"
) -> CompanyResearch:
    """
    Research target company using Brave Search.

    Args:
        ctx: RunContext with deps (http_client, brave_api_key)
        company_name: Name of company to research
        response_format: "concise" (~200 tokens) or "detailed" (~800 tokens)

    Returns:
        CompanyResearch model with business context

    Example:
        result = await research_company(ctx, "Acme Corp", "concise")
    """
    try:
        # Implementation
        pass
    except Exception as e:
        print(f"Error in research_company: {e}")
        return default_response
```

### Tool Registration Pattern
```python
# In agent.py
@agent.tool
async def research_company(
    ctx: RunContext[AgentDeps],
    company_name: str
) -> str:
    """
    Tool docstring visible to LLM - be specific!

    Args:
        ctx: Context with dependencies
        company_name: Company to research

    Returns:
        JSON string with company research
    """
    print(f"Calling research_company tool for: {company_name}")
    result = await research_company_tool(ctx, company_name)
    return result.model_dump_json()  # PydanticAI requires string returns
```

## 5. Logging

Use simple `print()` statements (Streamlit captures these):

```python
# Tool invocations
print(f"Calling {tool_name} tool with args: {args}")

# Errors with context
print(f"Error in {operation}: {error}")

# Database operations
print(f"Deleted {len(response.data)} document chunks for file ID: {file_id}")
```

**Log:** Tool calls, API requests, errors, database operations, performance metrics

## 6. Testing

### Framework: pytest + pytest-asyncio

### Test File Structure
```
tests/
├── conftest.py              # Shared fixtures
├── test_tools.py            # Tool function tests
├── test_clients.py          # Client setup tests
└── fixtures/
    ├── mock_brave.json      # Mock API responses
    └── mock_case_studies.json
```

### Async Test Pattern
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_context():
    """Mock RunContext with all dependencies."""
    ctx = MagicMock()
    ctx.deps.http_client = AsyncMock()
    ctx.deps.brave_api_key = "test-key"
    ctx.deps.supabase = MagicMock()
    return ctx

@pytest.mark.asyncio
async def test_research_company(mock_context):
    """Test company research with mocked Brave API."""
    # Mock API response
    mock_context.deps.http_client.get.return_value.json.return_value = {
        "web": {"results": [{"title": "Acme", "description": "E-commerce"}]}
    }

    result = await research_company(mock_context, "Acme Corp")

    assert result.company_name == "Acme Corp"
    mock_context.deps.http_client.get.assert_called_once()
```

### Run Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_tools.py -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=term-missing

# Async tests only
python -m pytest tests/ -v -m asyncio
```

## 7. Common Patterns

### Pattern 1: RAG Retrieval
```python
# From tools.py:119-156
async def retrieve_relevant_documents_tool(
    supabase: Client,
    embedding_client: AsyncOpenAI,
    user_query: str
) -> str:
    # 1. Get embedding
    query_embedding = await get_embedding(user_query, embedding_client)

    # 2. Query Supabase RPC function
    result = supabase.rpc(
        'match_documents',
        {'query_embedding': query_embedding, 'match_count': 4}
    ).execute()

    # 3. Format results
    formatted_chunks = []
    for doc in result.data:
        chunk = f"# {doc['metadata'].get('file_title')}\n{doc['content']}"
        formatted_chunks.append(chunk)

    return "\n\n---\n\n".join(formatted_chunks)
```

### Pattern 2: External API Call (Brave Search)
```python
# From tools.py:16-52
async def brave_web_search(query: str, http_client: AsyncClient, api_key: str) -> str:
    headers = {'X-Subscription-Token': api_key, 'Accept': 'application/json'}

    response = await http_client.get(
        'https://api.search.brave.com/res/v1/web/search',
        params={'q': query, 'count': 5},
        headers=headers
    )
    response.raise_for_status()

    data = response.json()
    results = []
    for item in data.get('web', {}).get('results', [])[:3]:
        results.append(f"Title: {item['title']}\nSummary: {item['description']}\n")

    return "\n".join(results)
```

### Pattern 3: Supabase Document Insertion
```python
# From RAG_Pipeline/common/db_handler.py:58-99
def insert_document_chunks(chunks: List[str], embeddings: List[List[float]],
                          file_id: str, file_url: str, file_title: str):
    data = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        data.append({
            "content": chunk,
            "metadata": {
                "file_id": file_id,
                "file_url": file_url,
                "file_title": file_title,
                "chunk_index": i
            },
            "embedding": embedding
        })

    for item in data:
        supabase.table("documents").insert(item).execute()
```

## 8. Development Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # Then edit with your API keys

# Run
streamlit run streamlit_ui.py
python RAG_Pipeline/Local_Files/main.py --directory "./Files"

# Test
python -m pytest tests/ -v
python -m pytest tests/ --cov=. --cov-report=html

# Quality (if installed)
mypy agent.py tools.py && black --check . && flake8 .
```

## 9. Environment Configuration

### Required Variables (.env)
```bash
# LLM Configuration
LLM_PROVIDER=openai                    # openai, azure_openai, anthropic, ollama
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_CHOICE=gpt-4o-mini                 # Model name

# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your-api-key
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# Optional: Web Search
BRAVE_API_KEY=your-brave-key           # For company research
SEARXNG_BASE_URL=http://localhost:8081 # Alternative to Brave

# Optional: Memory
DATABASE_URL=postgresql://user:pass@host:5432/db  # For Mem0
```

## 10. AI Coding Assistant Instructions

1. **ALWAYS check Archon MCP tasks first** - Use `find_tasks()` before any implementation
2. **Research before implementing** - Use `rag_search_knowledge_base()` for patterns and docs
3. **Follow async patterns** - All I/O must be async, use existing tool patterns as templates
4. **Use Pydantic models** - Define schemas before implementing tools
5. **Provider-agnostic code** - Read from `os.getenv()`, never hardcode providers
6. **Tool docstrings matter** - LLM reads them, be specific about Args/Returns/Examples
7. **Test with mocks** - Use pytest fixtures, AsyncMock for external APIs
8. **Reference existing code** - tools.py:16-214, agent.py:68-196 show core patterns
9. **Check PRD.md and MVP-tool-designs.md** - Source of truth for requirements
10. **Validate continuously** - Run imports, syntax checks, tests after each change

---

## Quick Checklist

Before submitting code, verify:

**Naming & Style:**
- [ ] All names follow conventions (snake_case, PascalCase, UPPER_CASE)
- [ ] Imports organized in 3 sections (system, third-party, local)
- [ ] Used truthiness checks (`if attr:` not `if attr == True:`)
- [ ] File operations use `with` or `async with`
- [ ] List operations use comprehensions where appropriate
- [ ] Lines under 100 characters
- [ ] 4 spaces (not tabs)

**Type Safety & Async:**
- [ ] All functions have type hints (args and return)
- [ ] All I/O operations are async (database, HTTP, embeddings)
- [ ] Pydantic models used for data structures
- [ ] No `Any` types without justification

**Documentation & Testing:**
- [ ] Public functions/classes have docstrings with Args/Returns
- [ ] Tool docstrings are LLM-friendly (specific, with examples)
- [ ] Tests are isolated and use mocks (no real APIs/databases)
- [ ] Test names are descriptive (no docstrings needed)

**Project Specific:**
- [ ] AgentDeps used for dependency injection
- [ ] Tools return JSON strings via `.model_dump_json()`
- [ ] Provider settings read from environment variables
- [ ] Archon task status updated (todo → doing → review → done)

---

**Last Updated:** 2025-12-29
**Project:** Brainforge Proposal & Outreach Agent
**Status:** MVP Development
