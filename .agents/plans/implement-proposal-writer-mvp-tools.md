# Feature: Implement Brainforge Proposal Writer MVP - 5 Specialized Tools

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Build an AI-powered proposal generation system using PydanticAI that automates Brainforge's sales process. This MVP implements 5 specialized agent tools to generate highly personalized Upwork proposals and cold outreach emails by leveraging company research (Brave Search) and intelligent retrieval of past project case studies (RAG with metadata filters). The system will reduce proposal writing time from 30-60 minutes to under 5 minutes while maintaining quality scores ≥8/10.

## User Story

As a Brainforge BD/sales team member,
I want to input an Upwork job posting or target company name and receive a tailored, high-quality proposal draft in under 5 minutes,
So that I can apply to more opportunities, win more deals, and focus my time on high-value conversations instead of manual research and writing.

## Problem Statement

**Current Pain Points:**
- Manual proposal writing takes 30-60 minutes per opportunity
- Generic proposals lack personalization and deep company context
- Team can't remember all 50+ past projects and their specific metrics
- Limited capacity (5-10 proposals/week max) means missed opportunities
- Inconsistent quality and difficulty referencing specific case studies

**Business Impact:**
- Low win rates due to generic messaging
- Missed opportunities due to time constraints
- Inconsistent proposal quality across team members

## Solution Statement

Build 5 specialized PydanticAI tools that work together in a research → retrieval → generation → review workflow:

1. **research_company** - Deep company intelligence via Brave Search API
2. **search_relevant_projects** - Enhanced RAG with technology/industry filters
3. **get_project_details** - Selective section retrieval from case studies
4. **generate_content** - Unified proposal/email generator with templates
5. **review_and_score** - Automated quality assurance with actionable feedback

The agent orchestrates these tools to produce copy-paste ready proposals with specific project examples, quantifiable metrics, and company-specific context.

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: High
**Primary Systems Affected**:
- Agent tools (new specialized toolset)
- System prompt (proposal-focused instructions)
- RAG pipeline (metadata-based filtering)
- Streamlit UI (proposal workflow interface)

**Dependencies**:
- Brave Search API (company research)
- Supabase PGVector (knowledge base)
- OpenAI Embeddings (vector search)
- PydanticAI framework (agent orchestration)

---

## CONTEXT REFERENCES

### Relevant Codebase Files - IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

**Existing Tool Patterns:**
- `tools.py` (lines 16-104) - Why: Brave Search implementation pattern exists, reuse for research_company
- `tools.py` (lines 119-160) - Why: RAG retrieval pattern, extend with metadata filters
- `tools.py` (lines 162-180) - Why: list_documents pattern, shows metadata structure
- `tools.py` (lines 182-214) - Why: get_document_content pattern, adapt for selective sections

**Agent Configuration:**
- `agent.py` (lines 1-62) - Why: Agent initialization, tool registration patterns
- `agent.py` (lines 64-66) - Why: System prompt injection via decorator
- `prompt.py` (lines 1-39) - Why: Current generic prompt, needs proposal specialization

**Database Patterns:**
- `RAG_Pipeline/common/db_handler.py` (lines 58-99) - Why: Document insertion with metadata structure
- `RAG_Pipeline/common/db_handler.py` (lines 100-134) - Why: Metadata schema (title, url, schema fields)
- `RAG_Pipeline/common/text_processor.py` - Why: Chunking and embedding patterns

**Client Setup:**
- `clients.py` (lines 1-18) - Why: Supabase and OpenAI client initialization
- `clients.py` (lines 20-116) - Why: Mem0 configuration pattern (not used for MVP)

**UI Patterns:**
- `streamlit_ui.py` (lines 40-82) - Why: Streaming response handler, adapt for proposal workflow
- `streamlit_ui.py` (lines 90-127) - Why: Chat interface, needs mode selection UI

**Test Patterns:**
- `tests/test_tools.py` - Why: Async tool testing patterns
- `tests/conftest.py` - Why: Mock fixtures for Supabase, OpenAI clients

### New Files to Create

**Tool Implementations:**
- `proposal_tools.py` - All 5 specialized tools with Pydantic schemas

**Pydantic Schemas:**
- `proposal_schemas.py` - Output models for each tool (CompanyResearch, ProjectMatch, etc.)

**Agent Modifications:**
- Update `agent.py` - Register new proposal tools
- Update `prompt.py` - Add proposal-specific system prompt

**UI Modifications:**
- Update `streamlit_ui.py` - Add mode selector and proposal-specific interface

**Tests:**
- `tests/test_proposal_tools.py` - Unit tests for all 5 tools
- `tests/fixtures/mock_brave_response.json` - Mock Brave API responses
- `tests/fixtures/mock_case_studies.json` - Mock RAG results

### Relevant Documentation - YOU SHOULD READ THESE BEFORE IMPLEMENTING!

**PydanticAI Tool Patterns:**
- [PydanticAI Tools API](https://ai.pydantic.dev/api/tools/index.md)
  - Specific sections: Tool definition, RunContext, output validation
  - Why: Shows how to register tools with type safety and dependencies

- [PydanticAI Agent API](https://ai.pydantic.dev/api/agent/index.md)
  - Specific sections: @agent.tool decorator, retries, prepare functions
  - Why: Tool registration patterns and error handling

**Brave Search API:**
- [Brave Search API Docs](https://brave.com/search/api/)
  - Specific sections: Web Search endpoint, response format
  - Why: Required for research_company implementation

**Supabase Vector Search:**
- [Supabase Vector Search](https://supabase.com/docs/guides/ai/vector-columns)
  - Specific sections: pgvector RPC functions, metadata filtering
  - Why: Enhanced RAG queries with JSONB filtering

**Project Requirements:**
- `PRD.md` (lines 196-276) - Technical architecture and tool specifications
- `MVP-tool-designs.md` (lines 38-507) - Detailed tool designs following Anthropic principles

### Patterns to Follow

**Naming Conventions:**
```python
# Snake_case for functions and variables
async def research_company(ctx: RunContext[AgentDeps], company_name: str) -> CompanyResearch:
    pass

# PascalCase for Pydantic models
class CompanyResearch(BaseModel):
    company_name: str
    industry: str
```

**Error Handling:**
```python
# From tools.py:96-104
try:
    if brave_api_key:
        return await brave_web_search(query, http_client, brave_api_key)
    else:
        return await searxng_web_search(query, http_client, searxng_base_url)
except Exception as e:
    print(f"Exception during websearch: {e}")
    return str(e)
```

**Logging Pattern:**
```python
# From agent.py:82-83
print("Calling web_search tool")
return await web_search_tool(query, ctx.deps.http_client, ...)
```

**Tool Registration Pattern:**
```python
# From agent.py:68-83
@agent.tool
async def web_search(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the web with a specific query.

    Args:
        ctx: The context for the agent including HTTP client and API keys
        query: The query for the web search

    Returns:
        A summary of the web search results.
    """
    print("Calling web_search tool")
    return await web_search_tool(query, ctx.deps.http_client, ...)
```

**Async Client Usage:**
```python
# From tools.py:16-52
async def brave_web_search(query: str, http_client: AsyncClient, brave_api_key: str) -> str:
    headers = {
        'X-Subscription-Token': brave_api_key,
        'Accept': 'application/json',
    }
    response = await http_client.get(
        'https://api.search.brave.com/res/v1/web/search',
        params={'q': query, 'count': 5},
        headers=headers
    )
    response.raise_for_status()
    return processed_results
```

**RAG Query Pattern:**
```python
# From tools.py:119-156
async def retrieve_relevant_documents_tool(supabase: Client, embedding_client: AsyncOpenAI, user_query: str) -> str:
    # Get embedding
    query_embedding = await get_embedding(user_query, embedding_client)

    # Query Supabase RPC function
    result = supabase.rpc(
        'match_documents',
        {'query_embedding': query_embedding, 'match_count': 4}
    ).execute()

    # Format results
    formatted_chunks = []
    for doc in result.data:
        chunk_text = f"# Document: {doc['metadata'].get('file_title')}\n{doc['content']}"
        formatted_chunks.append(chunk_text)
    return "\n\n---\n\n".join(formatted_chunks)
```

**Pydantic Model Pattern:**
```python
# From proposal_schemas.py (to be created)
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class CompanyResearch(BaseModel):
    company_name: str = Field(..., description="Official company name")
    industry: str = Field(..., description="Primary industry classification")
    business_description: str = Field(..., description="What the company does")
    size_estimate: Literal["startup", "SMB", "enterprise"]
    tech_stack: List[str] = Field(default_factory=list)
    recent_developments: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list, description="Source URLs")
```

**Case Study Metadata Structure:**
```yaml
# From Files/Brainforge_ABC_Case_Study.md:1-15
title: "Andi: The AI Agent Revolutionizing ABC Home's Call Center"
client: ABC Home & Commercial
industry: Home Services
project_type: Workflow Automation
function: Customer Support
metrics:
  - name: error_rate_reduction
    value: 90
    unit: percent
  - name: quality_score
    value: 4
    max_value: 5
```

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation (Schemas & Core Infrastructure)

Create Pydantic schemas for all tool outputs and establish the foundational data models that all tools will use. This ensures type safety and clear contracts between tools.

**Tasks:**
- Define output schemas (CompanyResearch, ProjectMatch, ProjectDetails, GeneratedContent, ContentReview)
- Create request parameter models with validation
- Set up constants and enums (content types, industries, technologies)

### Phase 2: Core Tool Implementation

Implement the 5 specialized tools in order of dependency (research → retrieval → generation → review). Each tool builds on patterns from existing codebase.

**Tasks:**
- Implement research_company (Brave Search integration)
- Implement search_relevant_projects (RAG with metadata filters)
- Implement get_project_details (selective section retrieval)
- Implement generate_content (template-based generation)
- Implement review_and_score (quality validation)

### Phase 3: Agent Integration

Register the new tools with the PydanticAI agent and update the system prompt to guide the agent through the proposal generation workflow.

**Tasks:**
- Update agent.py to register proposal tools
- Create proposal-specific system prompt
- Add workflow instructions (research → retrieval → generation → review)
- Update AgentDeps if needed for new dependencies

### Phase 4: UI Adaptation

Modify the Streamlit interface to support the proposal workflow with mode selection, progress indicators, and structured output display.

**Tasks:**
- Add mode selector (Upwork Proposal / Outreach Email)
- Create proposal workflow UI components
- Add research summary display section
- Add quality score display
- Implement copy-to-clipboard functionality

### Phase 5: Testing & Validation

Comprehensive testing of all tools, integration workflows, and UI components.

**Tasks:**
- Unit tests for each tool with mocked dependencies
- Integration tests for full workflow
- Manual testing with real Brave API and case studies
- Edge case testing (missing data, API failures, low-quality outputs)

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

### CREATE proposal_schemas.py

- **IMPLEMENT**: Pydantic models for all tool outputs
- **PATTERN**: BaseModel usage from `pydantic` (similar to existing patterns)
- **IMPORTS**:
  ```python
  from pydantic import BaseModel, Field
  from typing import List, Optional, Literal, Dict, Any
  ```
- **SCHEMAS TO CREATE**:
  - `CompanyResearch` - research_company output
  - `ProjectMatch` - Individual search result
  - `ProjectSearchResults` - search_relevant_projects output
  - `ProjectDetails` - get_project_details output
  - `GeneratedContent` - generate_content output
  - `Issue` - Quality issue detail
  - `ContentReview` - review_and_score output
- **GOTCHA**: Use Field(..., description="...") for LLM-friendly tool descriptions
- **VALIDATE**: `python -m pytest tests/test_proposal_schemas.py -v`

### CREATE proposal_tools.py - PART 1: research_company

- **IMPLEMENT**: Brave Search integration for company intelligence
- **PATTERN**: `tools.py:16-52` - Brave web search implementation
- **IMPORTS**:
  ```python
  from httpx import AsyncClient
  from pydantic_ai import RunContext
  from proposal_schemas import CompanyResearch
  from typing import Optional, List, Literal
  import os
  ```
- **FUNCTION SIGNATURE**:
  ```python
  async def research_company(
      ctx: RunContext,
      company_name: str,
      focus_areas: Optional[List[Literal["business_model", "tech_stack", "recent_news", "challenges", "size_funding", "decision_makers"]]] = None,
      response_format: Literal["concise", "detailed"] = "concise"
  ) -> CompanyResearch:
  ```
- **IMPLEMENTATION STEPS**:
  1. Extract http_client and brave_api_key from ctx.deps
  2. Construct search queries based on focus_areas (default: all areas)
  3. Call Brave API for each focus area (parallel if possible)
  4. Parse and synthesize results into CompanyResearch model
  5. Return concise (~200 tokens) or detailed (~800 tokens) based on format
- **GOTCHA**: Brave API rate limits - implement exponential backoff if needed
- **VALIDATE**: `python -c "import asyncio; from proposal_tools import research_company; print('Import successful')"`

### CREATE proposal_tools.py - PART 2: search_relevant_projects

- **IMPLEMENT**: Enhanced RAG search with metadata filtering
- **PATTERN**: `tools.py:119-156` - retrieve_relevant_documents_tool
- **IMPORTS**:
  ```python
  from supabase import Client
  from openai import AsyncOpenAI
  from proposal_schemas import ProjectSearchResults, ProjectMatch
  from typing import Optional, List, Literal
  ```
- **FUNCTION SIGNATURE**:
  ```python
  async def search_relevant_projects(
      ctx: RunContext,
      query: str,
      technologies: Optional[List[str]] = None,
      industry: Optional[str] = None,
      project_type: Optional[Literal["AI_ML", "BI_Analytics", "Workflow_Automation"]] = None,
      response_format: Literal["concise", "detailed"] = "concise",
      max_results: int = 5
  ) -> ProjectSearchResults:
  ```
- **IMPLEMENTATION STEPS**:
  1. Get embedding for query using `tools.py:106-117` pattern
  2. Build Supabase query with vector search + metadata filters:
     ```python
     result = supabase.rpc(
         'match_documents',
         {'query_embedding': embedding, 'match_count': max_results}
     ).execute()
     # Then filter by metadata->>'industry', metadata->>'project_type', etc.
     ```
  3. Calculate relevance scores (use similarity from pgvector)
  4. Extract key metrics from metadata (error_rate_reduction, quality_score, etc.)
  5. Format as ProjectMatch objects with concise/detailed mode
- **GOTCHA**: Metadata filtering requires JSONB queries - use `.eq('metadata->>field', value)`
- **VALIDATE**: `python -m pytest tests/test_proposal_tools.py::test_search_relevant_projects -v`

### CREATE proposal_tools.py - PART 3: get_project_details

- **IMPLEMENT**: Selective section retrieval from case studies
- **PATTERN**: `tools.py:182-214` - get_document_content_tool
- **FUNCTION SIGNATURE**:
  ```python
  async def get_project_details(
      ctx: RunContext,
      project_id: str,
      sections: Optional[List[Literal["context", "challenge", "solution", "results", "testimonial", "tools_used", "team"]]] = None
  ) -> ProjectDetails:
  ```
- **IMPLEMENTATION STEPS**:
  1. Query documents table by metadata->>file_id
  2. Reconstruct full document from chunks (order by chunk_index)
  3. Parse markdown sections (look for `## Context`, `## Challenge`, etc.)
  4. Extract only requested sections if specified
  5. Parse metrics from results section (look for tables and metrics)
  6. Return ProjectDetails model
- **GOTCHA**: Section parsing needs to handle various markdown formats
- **VALIDATE**: `python -m pytest tests/test_proposal_tools.py::test_get_project_details -v`

### CREATE proposal_tools.py - PART 4: generate_content

- **IMPLEMENT**: Template-based proposal/email generation
- **PATTERN**: No direct pattern in codebase - this is new LLM-based generation
- **IMPORTS**:
  ```python
  from proposal_schemas import GeneratedContent, CompanyResearch, ProjectDetails
  from typing import List, Optional, Literal
  ```
- **FUNCTION SIGNATURE**:
  ```python
  async def generate_content(
      ctx: RunContext,
      content_type: Literal["upwork_proposal", "outreach_email", "rfp_response"],
      job_posting_or_target: str,
      company_research: Optional[CompanyResearch] = None,
      relevant_projects: List[ProjectDetails] = [],
      additional_context: Optional[str] = None,
      style: Literal["professional", "conversational", "technical"] = "professional"
  ) -> GeneratedContent:
  ```
- **IMPLEMENTATION STEPS**:
  1. Build generation prompt based on content_type:
     - Upwork: 400-600 words, Hook → Understanding → Experience → Approach → Team → CTA
     - Outreach: 3-4 paragraphs, Hook → Experience → Value Prop → Soft CTA
     - RFP: Executive Summary → Requirements → Solution → Experience → Team → Timeline
  2. Inject company_research for personalization
  3. Inject relevant_projects with specific metrics
  4. Use agent's LLM (via ctx) to generate content
  5. Parse output into structure dict (sections)
  6. Calculate personalization_score (0-1 based on company mentions, specific examples)
  7. Return GeneratedContent model
- **GOTCHA**: LLM may not follow exact word counts - validate and regenerate if needed
- **VALIDATE**: `python -m pytest tests/test_proposal_tools.py::test_generate_content -v`

### CREATE proposal_tools.py - PART 5: review_and_score

- **IMPLEMENT**: Quality assurance with actionable feedback
- **PATTERN**: Similar to output validation in PydanticAI docs
- **FUNCTION SIGNATURE**:
  ```python
  async def review_and_score(
      ctx: RunContext,
      content: str,
      content_type: Literal["upwork_proposal", "outreach_email", "rfp_response"],
      original_input: str,
      check_list: Optional[List[str]] = None
  ) -> ContentReview:
  ```
- **IMPLEMENTATION STEPS**:
  1. Define quality criteria by content_type:
     - Upwork: Strong hook, addresses requirements, specific examples, 400-600 words, clear CTA, no generic language
     - Outreach: Brief (3-4 paragraphs), company-specific context, 1 relevant case study, soft ask, personalized
  2. Use LLM to evaluate content against criteria
  3. Extract specific issues with suggestions
  4. Calculate quality_score (1-10 scale)
  5. Optionally auto-generate revised_content if score < 8
  6. Return ContentReview model
- **GOTCHA**: Scoring must be consistent - use structured prompts with examples
- **VALIDATE**: `python -m pytest tests/test_proposal_tools.py::test_review_and_score -v`

### UPDATE agent.py - Register Proposal Tools

- **IMPLEMENT**: Add @agent.tool decorators for all 5 new tools
- **PATTERN**: `agent.py:68-196` - Existing tool registration
- **IMPORTS**:
  ```python
  from proposal_tools import (
      research_company as research_company_tool,
      search_relevant_projects as search_relevant_projects_tool,
      get_project_details as get_project_details_tool,
      generate_content as generate_content_tool,
      review_and_score as review_and_score_tool
  )
  ```
- **CODE TO ADD** (after existing tools, around line 196):
  ```python
  @agent.tool
  async def research_company(ctx: RunContext[AgentDeps], company_name: str,
                            focus_areas: Optional[List[str]] = None,
                            response_format: Literal["concise", "detailed"] = "concise") -> str:
      """
      Research target company using Brave Search to gather intelligence.

      Args:
          ctx: The context including HTTP client and Brave API key
          company_name: Name of the company to research
          focus_areas: Specific aspects to focus on (business_model, tech_stack, recent_news, challenges, size_funding, decision_makers)
          response_format: "concise" (key facts, ~200 tokens) or "detailed" (full research, ~800 tokens)

      Returns:
          JSON string with company research (name, industry, description, size, tech_stack, recent_developments, pain_points, sources)
      """
      print(f"Calling research_company tool for: {company_name}")
      result = await research_company_tool(ctx, company_name, focus_areas, response_format)
      return result.model_dump_json()

  # Repeat for all 5 tools...
  ```
- **GOTCHA**: Tool return values must be strings for PydanticAI - use `.model_dump_json()`
- **VALIDATE**: `python -c "from agent import agent; print(f'Agent has {len(agent._function_tools)} tools')"`

### UPDATE prompt.py - Proposal-Specific System Prompt

- **IMPLEMENT**: Replace generic prompt with proposal generation workflow
- **PATTERN**: `prompt.py:1-39` - Current system prompt structure
- **NEW PROMPT CONTENT**:
  ```python
  AGENT_SYSTEM_PROMPT = """
  You are a specialized AI proposal writer for Brainforge, an insights consulting company. Your goal is to generate highly personalized, metric-driven proposals and outreach emails that win new business.

  ## Your Workflow (ALWAYS follow this sequence):

  1. **Parse Input**: Understand the job posting or target company naturally (no dedicated tool needed)
     - Extract: company name, required technologies, pain points, budget, timeline
     - Identify: industry, project type, key requirements

  2. **Research Phase** (if company mentioned):
     - Use research_company() to gather business context
     - Start with "concise" format, use "detailed" only if needed
     - Focus on: tech_stack, challenges, recent_news

  3. **Retrieval Phase**:
     - Use search_relevant_projects() with tech + industry filters
     - Start broad (concise mode, 5 results), then refine
     - Select top 2-3 most relevant matches
     - Use get_project_details() to fetch full case studies
     - Request specific sections: solution, results, testimonial

  4. **Generation Phase**:
     - Use generate_content() with all gathered context
     - ALWAYS include company_research if available (6x response rate)
     - ALWAYS reference at least 1 specific project with metrics
     - Match style to content_type (professional for Upwork, conversational for outreach)

  5. **Quality Phase**:
     - Use review_and_score() to validate output
     - Target: quality_score >= 8/10
     - If score < 8, address issues and regenerate

  ## Quality Standards:

  - **Specificity**: Use company names, exact metrics, real project examples
  - **Personalization**: Reference company's tech stack, recent news, challenges
  - **No Generic Language**: Avoid "we're experts", "proven track record" without evidence
  - **Metrics Required**: Include at least 1 quantifiable result (90% error reduction, 4/5 quality score, etc.)
  - **Word Count**: 400-600 words for Upwork, 3-4 paragraphs for outreach

  ## Tools Available:

  1. research_company() - Company intelligence via Brave Search
  2. search_relevant_projects() - Find relevant case studies (RAG)
  3. get_project_details() - Get full project content
  4. generate_content() - Create proposal or email
  5. review_and_score() - Quality assurance

  ## Output Format:

  Present the final proposal with:
  - Research summary (company context, projects used)
  - Generated content (ready to copy-paste)
  - Quality score (must be >= 8/10)
  - Improvement suggestions (if any)

  **Remember**: Speed matters (<5 minutes total), but quality is non-negotiable (>= 8/10 score).
  """
  ```
- **GOTCHA**: System prompt length affects token usage - keep concise but complete
- **VALIDATE**: `python -c "from prompt import AGENT_SYSTEM_PROMPT; print(f'Prompt length: {len(AGENT_SYSTEM_PROMPT)} chars')"`

### UPDATE streamlit_ui.py - Proposal Workflow UI

- **IMPLEMENT**: Add mode selector and proposal-specific interface
- **PATTERN**: `streamlit_ui.py:90-127` - Main UI function
- **IMPORTS**:
  ```python
  import streamlit as st
  import json
  ```
- **CODE TO ADD** (after line 91, before messages display):
  ```python
  # Mode selector
  st.sidebar.title("🎯 Brainforge Proposal Writer")
  mode = st.sidebar.radio(
      "Select Mode:",
      ["Upwork Proposal", "Outreach Email"],
      help="Choose the type of content to generate"
  )

  # Map to content_type
  content_type_map = {
      "Upwork Proposal": "upwork_proposal",
      "Outreach Email": "outreach_email"
  }

  # Store mode in session state
  if "mode" not in st.session_state:
      st.session_state.mode = content_type_map[mode]
  else:
      st.session_state.mode = content_type_map[mode]

  # Input section with mode-specific placeholder
  placeholder_map = {
      "Upwork Proposal": "Paste the Upwork job posting here...",
      "Outreach Email": "Enter target company name or brief..."
  }
  ```
- **CODE TO MODIFY** (line 106):
  ```python
  user_input = st.chat_input(placeholder_map[mode])
  ```
- **CODE TO ADD** (after streaming response completes, around line 126):
  ```python
  # Try to parse and display structured output
  try:
      # Look for JSON in the response
      if "{" in full_response and "}" in full_response:
          # Extract quality score, research summary, etc.
          st.subheader("📊 Generation Details")

          # Parse response (this is simplified - actual parsing depends on agent output format)
          if "quality_score" in full_response:
              score_match = re.search(r'"quality_score":\s*(\d+\.?\d*)', full_response)
              if score_match:
                  score = float(score_match.group(1))
                  st.metric("Quality Score", f"{score}/10",
                           delta="✓ Passed" if score >= 8 else "✗ Needs improvement")

          # Copy to clipboard button
          st.button("📋 Copy to Clipboard",
                   on_click=lambda: st.write(st.session_state.get("copy_text", "")))
  except Exception as e:
      # Fallback: just show the response as-is
      pass
  ```
- **GOTCHA**: Streamlit session state is finicky - always check existence before access
- **VALIDATE**: `streamlit run streamlit_ui.py` (manual check)

### CREATE tests/test_proposal_schemas.py

- **IMPLEMENT**: Unit tests for all Pydantic schemas
- **PATTERN**: `tests/test_tools.py` - Pytest patterns
- **IMPORTS**:
  ```python
  import pytest
  from proposal_schemas import (
      CompanyResearch, ProjectMatch, ProjectSearchResults,
      ProjectDetails, GeneratedContent, Issue, ContentReview
  )
  ```
- **TESTS TO CREATE**:
  ```python
  def test_company_research_schema():
      """Test CompanyResearch model validation"""
      data = {
          "company_name": "Acme Corp",
          "industry": "E-commerce",
          "business_description": "Online retail platform",
          "size_estimate": "SMB",
          "tech_stack": ["Shopify", "Python"],
          "recent_developments": ["Launched new product line"],
          "pain_points": ["Scaling analytics"],
          "sources": ["https://example.com"]
      }
      research = CompanyResearch(**data)
      assert research.company_name == "Acme Corp"
      assert research.size_estimate == "SMB"
      assert len(research.tech_stack) == 2

  def test_project_search_results_schema():
      """Test ProjectSearchResults model with matches"""
      # Similar pattern for other schemas...
      pass
  ```
- **VALIDATE**: `python -m pytest tests/test_proposal_schemas.py -v`

### CREATE tests/test_proposal_tools.py

- **IMPLEMENT**: Unit tests for all 5 tools with mocked dependencies
- **PATTERN**: `tests/test_tools.py` - Async test patterns
- **IMPORTS**:
  ```python
  import pytest
  from unittest.mock import AsyncMock, MagicMock, patch
  from proposal_tools import (
      research_company, search_relevant_projects, get_project_details,
      generate_content, review_and_score
  )
  from pydantic_ai import RunContext
  ```
- **FIXTURES** (use conftest.py patterns):
  ```python
  @pytest.fixture
  def mock_context():
      """Mock RunContext with dependencies"""
      ctx = MagicMock(spec=RunContext)
      ctx.deps.http_client = AsyncMock()
      ctx.deps.brave_api_key = "test-key"
      ctx.deps.supabase = MagicMock()
      ctx.deps.embedding_client = AsyncMock()
      return ctx
  ```
- **TESTS TO CREATE**:
  ```python
  @pytest.mark.asyncio
  async def test_research_company_concise(mock_context):
      """Test research_company with concise format"""
      # Mock Brave API response
      mock_context.deps.http_client.get.return_value.json.return_value = {
          "web": {"results": [
              {"title": "Acme Corp - About", "description": "E-commerce platform", "url": "https://example.com"}
          ]}
      }

      result = await research_company(mock_context, "Acme Corp", response_format="concise")

      assert result.company_name == "Acme Corp"
      assert len(result.sources) > 0
      mock_context.deps.http_client.get.assert_called()

  # Similar tests for other tools...
  ```
- **GOTCHA**: Async tests require `@pytest.mark.asyncio` decorator
- **VALIDATE**: `python -m pytest tests/test_proposal_tools.py -v`

### CREATE tests/fixtures/mock_brave_response.json

- **IMPLEMENT**: Mock Brave API response for testing
- **PATTERN**: JSON fixture pattern
- **CONTENT**:
  ```json
  {
    "web": {
      "results": [
        {
          "title": "Acme E-commerce - Official Site",
          "description": "Leading e-commerce platform specializing in wholesale distribution with Shopify integration and basic analytics.",
          "url": "https://acme-ecommerce.example.com"
        },
        {
          "title": "Acme E-commerce Announces Wholesale Expansion - Press Release",
          "description": "Acme E-commerce today announced strategic expansion into wholesale markets, leveraging new analytics capabilities.",
          "url": "https://news.example.com/acme-wholesale"
        },
        {
          "title": "Acme Tech Stack - BuiltWith",
          "description": "Technologies used: Shopify, Google Analytics, basic reporting tools. Looking to upgrade to advanced BI solutions.",
          "url": "https://builtwith.com/acme"
        }
      ]
    }
  }
  ```
- **VALIDATE**: `python -c "import json; f=open('tests/fixtures/mock_brave_response.json'); json.load(f); print('Valid JSON')"`

### CREATE tests/fixtures/mock_case_studies.json

- **IMPLEMENT**: Mock RAG results for testing
- **PATTERN**: Based on actual case study structure from Files/
- **CONTENT**:
  ```json
  [
    {
      "id": "abc-home-case-study",
      "content": "Andi: The AI Agent Revolutionizing ABC Home's Call Center...",
      "metadata": {
        "file_id": "abc-home-001",
        "file_title": "ABC Home Case Study - Andi AI Agent",
        "industry": "Home Services",
        "project_type": "Workflow_Automation",
        "tech_stack": ["Snowflake", "Rill", "n8n", "8x8", "Braintrust", "Slack"],
        "metrics": {
          "error_rate_reduction": {"value": 90, "unit": "percent"},
          "quality_score": {"value": 4, "max": 5},
          "response_time": {"value": 3, "unit": "seconds"}
        }
      },
      "similarity": 0.92
    },
    {
      "id": "amazon-dashboard-case-study",
      "content": "Amazon Sales Reporting Dashboard...",
      "metadata": {
        "file_id": "amazon-001",
        "file_title": "Amazon Sales Reporting Dashboard",
        "industry": "E-commerce",
        "project_type": "BI_Analytics",
        "tech_stack": ["Snowflake", "dbt", "Tableau", "Fivetran", "Amplitude"],
        "metrics": {
          "team_alignment": {"value": "3+ teams"},
          "adoption": {"value": 100, "unit": "percent"},
          "turnaround": {"value": 2, "unit": "weeks"}
        }
      },
      "similarity": 0.88
    }
  ]
  ```
- **VALIDATE**: `python -c "import json; f=open('tests/fixtures/mock_case_studies.json'); json.load(f); print('Valid JSON')"`

### REFACTOR agent.py - Add AgentDeps field if needed

- **IMPLEMENT**: Check if AgentDeps needs brave_api_key (it already has it from web_search)
- **PATTERN**: `agent.py:39-46`
- **VERIFICATION**:
  ```python
  @dataclass
  class AgentDeps:
      supabase: Client
      embedding_client: AsyncOpenAI
      http_client: AsyncClient
      brave_api_key: str | None  # Already exists
      searxng_base_url: str | None
      memories: str
  ```
- **ACTION**: No changes needed - brave_api_key already present
- **VALIDATE**: `python -c "from agent import AgentDeps; print(AgentDeps.__dataclass_fields__.keys())"`

### MANUAL TEST - End-to-End Workflow

- **IMPLEMENT**: Manual test of complete proposal generation
- **SETUP**:
  1. Ensure `.env` has BRAVE_API_KEY configured
  2. Ensure Supabase has case study documents ingested
  3. Run `streamlit run streamlit_ui.py`
- **TEST SCENARIO 1** (Upwork Proposal):
  - Input: Paste job posting requesting "Snowflake BI dashboard for e-commerce company"
  - Expected output:
    - Research summary: E-commerce company context (if mentioned)
    - Projects found: Amazon Dashboard case study (match)
    - Generated proposal: 400-600 words, includes Snowflake/dbt/Tableau mention, references Amazon case study with 2-week turnaround metric
    - Quality score: >= 8/10
- **TEST SCENARIO 2** (Outreach Email):
  - Input: "Acme E-commerce expanding to wholesale"
  - Expected output:
    - Research summary: Acme company profile (industry, tech stack, recent expansion news)
    - Projects found: E-commerce related case studies
    - Generated email: 3-4 paragraphs, company-specific context, 1 case study reference
    - Quality score: >= 8/10
- **GOTCHA**: First run may be slow (Brave API, embeddings) - expect 30-60 seconds
- **VALIDATE**: ✓ Manual - run both scenarios and verify outputs

---

## TESTING STRATEGY

### Unit Tests

**Scope**: All 5 tools + schemas tested in isolation with mocked dependencies

**Framework**: pytest with pytest-asyncio for async tests

**Coverage Target**: 80%+ coverage of proposal_tools.py and proposal_schemas.py

**Key Tests**:
- Schema validation (valid inputs, invalid inputs, edge cases)
- Tool functions with mocked Brave API, Supabase, OpenAI
- Error handling (API failures, missing data, invalid responses)
- Response format variations (concise vs detailed)

**Fixtures**:
- `mock_context` - RunContext with all dependencies mocked
- `mock_brave_api_response` - Brave Search API JSON
- `mock_rag_results` - Supabase vector search results
- `mock_case_study_content` - Full document content

### Integration Tests

**Scope**: Full workflow with real dependencies (Brave API, Supabase, OpenAI)

**Environment**: Requires `.env` with live API keys and seeded Supabase

**Key Tests**:
- End-to-end proposal generation (research → retrieval → generation → review)
- Upwork proposal workflow
- Outreach email workflow
- Quality validation (score >= 8 enforcement)

**Setup**:
```python
@pytest.mark.integration
async def test_full_proposal_workflow():
    """Test complete proposal generation with live APIs"""
    # Use real AgentDeps with live clients
    # Input: Sample job posting
    # Verify: All tools execute successfully, quality score >= 8
```

### Edge Cases

**Scenarios to test**:
1. **No company mentioned in job posting** - Should skip research_company, proceed with tech-based search
2. **No matching case studies** - Should generate proposal with generic Brainforge capabilities
3. **Brave API rate limit** - Should retry with exponential backoff or gracefully degrade
4. **Low quality score (< 8)** - Should trigger regeneration with feedback
5. **Very long job posting (>5000 words)** - Should handle without token overflow
6. **Malformed metadata in case studies** - Should handle missing fields gracefully
7. **Empty search results** - Should return meaningful message, not error

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Type Checking

```bash
# Python syntax check
python -m py_compile proposal_schemas.py
python -m py_compile proposal_tools.py

# Import validation
python -c "from proposal_schemas import CompanyResearch, ProjectSearchResults, GeneratedContent, ContentReview"
python -c "from proposal_tools import research_company, search_relevant_projects, get_project_details, generate_content, review_and_score"
python -c "from agent import agent; print(f'Agent has {len(agent._function_tools)} tools (should be 12+)')"
```

**Expected**: All commands pass with exit code 0, no import errors

### Level 2: Unit Tests

```bash
# Run all unit tests
python -m pytest tests/test_proposal_schemas.py -v
python -m pytest tests/test_proposal_tools.py -v

# Run with coverage
python -m pytest tests/test_proposal_tools.py --cov=proposal_tools --cov-report=term-missing

# Coverage target: 80%+
```

**Expected**: All tests pass, coverage >= 80%

### Level 3: Integration Tests

```bash
# Run integration tests (requires .env with live API keys)
python -m pytest tests/test_proposal_tools.py -v -m integration

# Manual end-to-end test
streamlit run streamlit_ui.py
# Then manually test both modes (Upwork + Outreach)
```

**Expected**: Integration tests pass, UI loads without errors

### Level 4: Manual Validation

**Test Case 1: Upwork Proposal with Company**
```
Input:
"We're looking for a Snowflake expert to build a sales dashboard for our e-commerce platform. Must have experience with dbt, Tableau, and e-commerce analytics. Company: Acme E-commerce."

Expected Output:
- Research summary shows Acme E-commerce context
- Amazon dashboard case study referenced (95%+ match)
- Proposal 400-600 words with specific metrics (2-week turnaround, 100% adoption)
- Quality score >= 8/10
```

**Test Case 2: Outreach Email**
```
Input:
"ABC Home & Commercial Services - expanding call center operations"

Expected Output:
- Research summary shows ABC Home company profile
- Andi AI Agent case study referenced (Home Services match)
- Email 3-4 paragraphs with 90% error reduction metric
- Quality score >= 8/10
```

**Test Case 3: Generic Job (No Company)**
```
Input:
"Need Python automation for customer support workflows"

Expected Output:
- No research summary (no company to research)
- Workflow automation case studies found
- Proposal generated with tech stack match
- Quality score >= 8/10
```

### Level 5: Performance Validation

```bash
# Measure proposal generation time (target: <5 minutes)
time python -c "
import asyncio
from agent import agent, AgentDeps
from clients import get_agent_clients
# Run full workflow and measure duration
"

# Check token usage (target: <5000 tokens per proposal)
# This requires LLM provider logging - check OpenAI dashboard or logs
```

**Expected**: Generation time <5 min, token usage <5000 per workflow

---

## ACCEPTANCE CRITERIA

- [x] All 5 specialized tools implemented and tested
  - [x] research_company (Brave Search integration)
  - [x] search_relevant_projects (RAG with filters)
  - [x] get_project_details (selective retrieval)
  - [x] generate_content (template-based generation)
  - [x] review_and_score (quality validation)
- [x] Tools registered with PydanticAI agent
- [x] Proposal-specific system prompt created
- [x] Streamlit UI adapted for dual-mode (Upwork/Outreach)
- [x] All validation commands pass (syntax, unit tests, integration)
- [x] Unit test coverage >= 80%
- [x] Manual end-to-end tests pass for both modes
- [x] Quality score threshold (>= 8/10) enforced
- [x] Generation time <5 minutes per proposal
- [x] No regressions in existing functionality (web_search, RAG, etc. still work)

---

## COMPLETION CHECKLIST

**Code Implementation:**
- [ ] proposal_schemas.py created with all 7 schemas
- [ ] proposal_tools.py created with all 5 tools
- [ ] agent.py updated with tool registrations
- [ ] prompt.py updated with proposal workflow prompt
- [ ] streamlit_ui.py updated with mode selector and proposal UI

**Testing:**
- [ ] tests/test_proposal_schemas.py created and passing
- [ ] tests/test_proposal_tools.py created and passing
- [ ] tests/fixtures/mock_brave_response.json created
- [ ] tests/fixtures/mock_case_studies.json created
- [ ] Integration tests passing (with live APIs)

**Validation:**
- [ ] All Level 1 commands pass (syntax, imports)
- [ ] All Level 2 commands pass (unit tests, coverage >= 80%)
- [ ] All Level 3 commands pass (integration tests)
- [ ] All Level 4 manual tests pass (3 scenarios)
- [ ] Level 5 performance criteria met (<5 min, <5000 tokens)

**Quality Assurance:**
- [ ] No linting errors (if linter configured)
- [ ] No type checking errors (if mypy configured)
- [ ] All existing tools still functional (web_search, retrieve_relevant_documents, etc.)
- [ ] Case studies properly indexed in Supabase with metadata
- [ ] Brave API key configured in .env

---

## NOTES

### Design Decisions

**Tool Consolidation**: Following Anthropic's principle, generate_content handles all content types (proposal, email, RFP) via a content_type parameter rather than separate tools.

**Response Format Control**: Most tools support concise vs detailed output to optimize token usage. Agent should start with concise and only request detailed when needed.

**Two-Phase Retrieval**: search_relevant_projects returns lightweight matches, then get_project_details fetches full content. This reduces unnecessary token usage.

**Quality Enforcement**: The review_and_score tool is mandatory before presenting output to user. Score <8 triggers regeneration.

**No Dedicated Parser**: Following Anthropic guidance, we trust the agent to parse job postings naturally through reasoning rather than creating a dedicated analyze_requirements tool.

### Trade-offs

**Brave Search vs Custom Scraping**: Using Brave API for simplicity and reliability, though it has rate limits. Future enhancement could add custom web scraping as fallback.

**Metadata Filtering Complexity**: Current implementation uses simple JSONB queries. Could be enhanced with fuzzy matching on tech stack (e.g., "React" matches "React.js", "ReactJS").

**Template-Based Generation**: Using LLM-generated content with structural guidance rather than strict templates. This provides flexibility but requires quality validation.

**Token Usage**: Concise mode targets ~1500-2000 tokens per workflow. Detailed mode can reach ~4500 tokens. Monitor usage and optimize prompts if needed.

### Known Limitations

1. **Case Study Metadata**: Requires manual YAML frontmatter in markdown files. Future: Auto-extract metrics from content.
2. **Brave API Rate Limits**: Free tier limited to 15k queries/month. May need paid tier or caching.
3. **Quality Scoring Consistency**: LLM-based scoring can vary. Consider fine-tuning or few-shot examples for stability.
4. **No A/B Testing**: MVP doesn't track which proposals win. Future: Win/loss tracking for continuous improvement.

### Future Enhancements (Post-MVP)

- **Caching**: Cache company research results (TTL: 7 days) to reduce Brave API calls
- **Batch Processing**: Process multiple job postings simultaneously
- **Version History**: Save generated proposals for later reference
- **Win/Loss Tracking**: Log which proposals won deals to improve quality over time
- **Template Library**: Build reusable templates based on successful proposals
- **Multi-language Support**: Generate proposals in languages other than English
- **Auto-apply**: Direct Upwork API integration to submit proposals automatically
