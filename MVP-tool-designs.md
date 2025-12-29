# MVP Tool Design: Brainforge Proposal & Outreach Agent

**Version:** 1.0
**Date:** 2025-12-29
**Purpose:** Define optimal toolset for AI-powered proposal and outreach generation

---

## Design Principles (Anthropic-Aligned)

Based on [Anthropic's Engineering Guide](https://www.anthropic.com/engineering/writing-tools-for-agents):

1. **Consolidate functionality** - Combine related operations (not separate tools per variant)
2. **Search, not list** - Filter before returning results (token efficiency)
3. **Response format control** - Let agent choose concise vs detailed
4. **Token efficiency** - Pagination, defaults, truncation
5. **Meaningful responses** - Semantic names + IDs only when needed
6. **Actionable feedback** - Guide agents with clear instructions, not error codes
7. **Trust agent reasoning** - Don't over-structure; agents can parse naturally

---

## Final Toolset (5 Tools)

### Architecture Flow

```
Agent analyzes naturally → research_company + search_relevant_projects →
get_project_details → generate_content → review_and_score
```

**Key Decision:** No dedicated `analyze_requirements` tool - agent parses job postings/targets naturally through its reasoning capabilities.

---

## Tool Specifications

### 1. `research_company`

**Purpose:** Deep company intelligence via Brave Search

**Signature:**
```python
async def research_company(
    ctx: RunContext[AgentDeps],
    company_name: str,
    focus_areas: Optional[List[Literal[
        "business_model", "tech_stack", "recent_news",
        "challenges", "size_funding", "decision_makers"
    ]]] = None,
    response_format: Literal["concise", "detailed"] = "concise"
) -> CompanyResearch
```

**Output Schema:**
```python
class CompanyResearch(BaseModel):
    company_name: str
    industry: str
    business_description: str
    size_estimate: Literal["startup", "SMB", "enterprise"]
    tech_stack: List[str]
    recent_developments: List[str]
    pain_points: List[str]
    key_people: List[str]
    sources: List[str]  # URLs
```

**Key Features:**
- Brave API integration (web search)
- Selective focus areas (token efficiency)
- Response format: concise (~200 tokens) vs detailed (~800 tokens)
- Multi-query synthesis

**Token Budget:**
- Concise: ~200 tokens
- Detailed: ~800 tokens
- Max: 1000 tokens

**Tool Description:**
```python
"""
Research target company using Brave Search to gather intelligence.

What this does:
- Executes targeted web searches via Brave API
- Synthesizes results into structured company profile
- Identifies tech stack, challenges, and opportunities
- Finds recent news and developments

Args:
    company_name: Name of the company to research
    focus_areas: Specific aspects to focus on (optional)
        If None, researches all areas
        Use specific areas to reduce token usage
    response_format:
        - "concise": Key facts only (~200 tokens)
        - "detailed": Full research with sources (~800 tokens)

Returns:
    CompanyResearch with business context, tech stack, pain points, recent news

Best practice:
- Start with "concise" to get overview
- Use "detailed" only if you need deep context
- Specify focus_areas to reduce unnecessary searches

Example:
    # Quick overview
    research_company("Acme Corp", response_format="concise")

    # Deep dive on tech
    research_company(
        "Acme Corp",
        focus_areas=["tech_stack", "challenges"],
        response_format="detailed"
    )
"""
```

---

### 2. `search_relevant_projects`

**Purpose:** Find matching past work from knowledge base (RAG)

**Signature:**
```python
async def search_relevant_projects(
    ctx: RunContext[AgentDeps],
    query: str,
    technologies: Optional[List[str]] = None,
    industry: Optional[str] = None,
    project_type: Optional[Literal["AI_ML", "BI_Analytics", "Automation"]] = None,
    response_format: Literal["concise", "detailed"] = "concise",
    max_results: int = 5
) -> ProjectSearchResults
```

**Output Schema:**
```python
class ProjectMatch(BaseModel):
    project_id: str  # For get_project_details()
    project_name: str  # Semantic name
    project_type: str
    industry: str
    technologies_used: List[str]
    key_metric: str  # e.g., "90% error reduction"
    relevance_score: float  # 0-1
    summary: Optional[str]  # Only in detailed mode

class ProjectSearchResults(BaseModel):
    matches: List[ProjectMatch]
    total_found: int
    search_query: str
```

**Key Features:**
- Multi-dimensional filtering (tech + industry + type)
- Relevance scoring
- Response format control
- Default max_results=5 (token cap)

**Token Budget:**
- Concise: ~50 tokens per result (5 results = 250 tokens)
- Detailed: ~200 tokens per result (5 results = 1000 tokens)

**Tool Description:**
```python
"""
Search Brainforge's past projects for relevant examples.

What this does:
- Semantic search across case studies, decks, and proposals
- Filters by technology, industry, and project type
- Ranks results by relevance to your query
- Returns structured matches with key information

Args:
    query: Natural language search query
        Examples: "BI dashboard for e-commerce"
                 "AI automation for customer support"
    technologies: Filter by specific tech (optional)
        Examples: ["Snowflake", "dbt", "Tableau"]
    industry: Filter by industry (optional)
        Examples: "e-commerce", "home services", "fintech"
    project_type: Filter by project category (optional)
    response_format:
        - "concise": Project name, type, key metric only
        - "detailed": Full summary with metrics, tools, outcomes
    max_results: Maximum number of results (default: 5, max: 10)

Returns:
    ProjectSearchResults with ranked matches

Multi-round search strategy:
1. First search: Broad query in concise mode
2. Review results, identify gaps
3. Second search: Refined query with filters
4. Select top 2-3 for detailed fetch

Example:
    # Broad search
    search_relevant_projects(
        query="sales dashboard reporting",
        response_format="concise",
        max_results=5
    )

    # Refined search
    search_relevant_projects(
        query="Snowflake data warehouse",
        technologies=["Snowflake", "dbt"],
        industry="e-commerce",
        response_format="detailed",
        max_results=3
    )
"""
```

---

### 3. `get_project_details`

**Purpose:** Retrieve full content for specific project

**Signature:**
```python
async def get_project_details(
    ctx: RunContext[AgentDeps],
    project_id: str,
    sections: Optional[List[Literal[
        "context", "challenge", "solution",
        "results", "testimonial", "tools_used", "team"
    ]]] = None
) -> ProjectDetails
```

**Output Schema:**
```python
class ProjectDetails(BaseModel):
    project_name: str
    client_name: str
    context: Optional[str]
    challenge: Optional[str]
    solution: Optional[str]
    results: Optional[Results]  # Metrics, outcomes
    testimonial: Optional[str]
    tools_used: Optional[List[str]]
    team: Optional[List[str]]
```

**Key Features:**
- Selective section fetching (specify what you need)
- Full case study retrieval
- Two-phase pattern: search → fetch

**Token Budget:**
- All sections: ~1500 tokens
- Specific sections: ~200-600 tokens

**Tool Description:**
```python
"""
Retrieve full details for a specific project.

What this does:
- Fetches complete project content from knowledge base
- Returns specific sections (if requested)
- Includes metrics, quotes, and implementation details

Args:
    project_id: ID from search_relevant_projects results
    sections: Specific sections to retrieve (optional)
        If None, returns all sections
        Use specific sections to reduce token usage

Returns:
    ProjectDetails with requested sections

Token efficiency:
- All sections: ~1500 tokens
- Context only: ~300 tokens
- Challenge + Solution: ~600 tokens
- Results only: ~200 tokens

Best practice:
- Use search_relevant_projects first (concise mode)
- Identify top 2-3 most relevant projects
- Fetch full details only for those top matches
- Request specific sections if you only need certain parts

Example:
    # Get full case study
    get_project_details("abc-home-andi")

    # Get only metrics
    get_project_details(
        "abc-home-andi",
        sections=["results", "tools_used"]
    )
"""
```

---

### 4. `generate_content` ⭐ (Consolidated)

**Purpose:** Generate proposals OR outreach emails (unified tool)

**Signature:**
```python
async def generate_content(
    ctx: RunContext[AgentDeps],
    content_type: Literal["upwork_proposal", "outreach_email", "rfp_response"],
    job_posting_or_target: str,
    company_research: Optional[CompanyResearch] = None,
    relevant_projects: List[ProjectDetails] = [],
    additional_context: Optional[str] = None,
    style: Literal["professional", "conversational", "technical"] = "professional"
) -> GeneratedContent
```

**Output Schema:**
```python
class GeneratedContent(BaseModel):
    content: str  # Full draft
    structure: Dict[str, str]  # Section breakdown
    word_count: int
    projects_referenced: List[str]
    personalization_score: float  # 0-1
```

**Content Structures:**

**Upwork Proposal (400-600 words):**
1. Hook (reference their company/project)
2. Understanding (their problem)
3. Experience (past work + metrics)
4. Approach (how we'll solve it)
5. Team & Tools
6. CTA

**Outreach Email (3-4 paragraphs):**
1. Hook (reference their company/news)
2. Relevant experience (1 case study)
3. Value proposition
4. Soft CTA

**RFP Response:**
1. Executive summary
2. Understanding requirements
3. Proposed solution
4. Past experience
5. Team & qualifications
6. Timeline & pricing

**Key Features:**
- Single tool handles all content types (consolidation principle)
- Agent parses job posting naturally (no structured requirements needed)
- Style parameter for tone control
- Automatic personalization scoring
- Structured output for iteration

**Tool Description:**
```python
"""
Generate personalized content (proposals or outreach emails).

What this does:
- Synthesizes all research into compelling content
- Adapts structure and tone based on content_type
- Includes specific examples from relevant_projects
- Personalizes using company_research (if available)

Args:
    content_type: Type of content to generate
        - "upwork_proposal": 400-600 word Upwork application
        - "outreach_email": 3-4 paragraph cold email
        - "rfp_response": Formal RFP response
    job_posting_or_target: The original job posting or target brief
    company_research: From research_company() (optional but recommended)
    relevant_projects: From get_project_details()
    additional_context: Any extra notes/instructions
    style: Writing tone (professional/conversational/technical)

Returns:
    GeneratedContent with full draft and metadata

Best practices:
- ALWAYS include company_research if available (6x response rate)
- Reference AT LEAST 1 specific project with metrics
- Use company name and specifics (not generic)
- Keep Upwork proposals 400-600 words
- Keep outreach emails 3-4 paragraphs

Example:
    # Upwork proposal with full context
    generate_content(
        content_type="upwork_proposal",
        job_posting_or_target=job_text,
        company_research=company_intel,
        relevant_projects=[project1, project2],
        style="conversational"
    )
"""
```

**Why Consolidated:**
- Anthropic principle: "Combine related operations into single tool"
- Single tool handles all generation variants
- Maintains context across types
- Simpler agent reasoning

---

### 5. `review_and_score`

**Purpose:** Quality assurance with actionable feedback

**Signature:**
```python
async def review_and_score(
    ctx: RunContext[AgentDeps],
    content: str,
    content_type: Literal["upwork_proposal", "outreach_email", "rfp_response"],
    original_input: str,
    check_list: Optional[List[str]] = None
) -> ContentReview
```

**Output Schema:**
```python
class Issue(BaseModel):
    category: str
    description: str
    suggestion: str  # Actionable fix

class ContentReview(BaseModel):
    quality_score: float  # 1-10
    passed_checks: List[str]
    failed_checks: List[str]
    specific_issues: List[Issue]
    suggestions: List[str]
    revised_content: Optional[str]  # Auto-fix if issues found
```

**Review Criteria by Type:**

**Upwork Proposal:**
- ✓ Strong hook (references company/project)
- ✓ Addresses all requirements from job posting
- ✓ Specific examples with metrics
- ✓ 400-600 words
- ✓ Clear CTA
- ✓ No generic language

**Outreach Email:**
- ✓ Brief (3-4 paragraphs)
- ✓ Company-specific context
- ✓ 1 relevant case study
- ✓ Soft ask
- ✓ Personalized

**Tool Description:**
```python
"""
Review content quality and provide actionable feedback.

What this does:
- Evaluates content against best practices
- Checks for specificity (not generic language)
- Validates requirements coverage
- Provides quality score and specific improvements

Args:
    content: The generated content to review
    content_type: Type of content (for context-aware review)
    original_input: Original job posting or target (to check coverage)
    check_list: Additional criteria to check (optional)

Returns:
    ContentReview with score, issues, and suggestions

Error guidance:
- If missing specifics: "Add metrics from [project name]"
- If too generic: "Replace 'we're experts' with specific example"
- If too long: "Cut to 500 words, focus on [sections]"

Best practice:
- Review before sending
- Aim for quality_score ≥ 8
- Address all failed_checks
- Use revised_content if provided

Example:
    review = review_and_score(
        content=proposal_draft,
        content_type="upwork_proposal",
        original_input=job_posting
    )

    if review.quality_score < 8:
        # Iterate with feedback
"""
```

---

## Rationale: Why 5 Tools?

### Design Philosophy:

| Factor | Analysis |
|--------|----------|
| **Anthropic Alignment** | "Trust agent reasoning" - don't over-structure |
| **Simplicity** | 5 tools vs 6 or 7 (20% reduction) |
| **Agent Capability** | Modern LLMs excel at parsing job postings naturally |
| **Token Efficiency** | No extra tool call for requirements analysis |
| **Flexibility** | Agent can adapt parsing strategy per input type |

### Design Decisions:

| Decision | Reasoning |
|----------|-----------|
| Remove analyze_requirements | Agent parses job postings naturally in reasoning |
| Merge proposal + email generation | Same operation, different templates (Anthropic: consolidate) |
| Separate search + get_details | Two-phase retrieval (survey → deep dive) |
| Response format enums | Token efficiency (agent controls verbosity) |
| Section-based fetching | Fetch only what's needed |

---

## Typical Workflow

### Upwork Proposal (4-5 tool calls)

```python
# Agent naturally parses job posting through reasoning
# Identifies: company name, tech stack, pain points, requirements

# 1. Research company (if mentioned in job)
company = research_company(
    "Acme E-commerce",
    focus_areas=["business_model", "challenges"],
    response_format="concise"
)

# 2. Find relevant work
projects = search_relevant_projects(
    query="Snowflake BI dashboard e-commerce",
    technologies=["Snowflake", "dbt", "Tableau"],
    industry="e-commerce",
    response_format="concise",
    max_results=5
)

# 3. Deep dive top matches
project1 = get_project_details(
    projects.matches[0].project_id,
    sections=["solution", "results", "testimonial"]
)

project2 = get_project_details(
    projects.matches[1].project_id,
    sections=["results"]
)

# 4. Generate
proposal = generate_content(
    content_type="upwork_proposal",
    job_posting_or_target=job_text,
    company_research=company,
    relevant_projects=[project1, project2],
    style="conversational"
)

# 5. Review
review = review_and_score(
    content=proposal.content,
    content_type="upwork_proposal",
    original_input=job_text
)
```

**Time:** <5 minutes
**Tool Calls:** 4-5 (vs 5-6 with analyze_requirements)
**Token Usage:** ~1,450-4,500 tokens

---

## Agent System Prompt (Requirements Parsing)

Since we removed `analyze_requirements` tool, the agent needs guidance:

```
When you receive a job posting or outreach target, first analyze it carefully:

For Upwork Jobs:
- Identify company name (if mentioned) → research_company()
- Extract required technologies → use for search_relevant_projects()
- Understand pain points and requirements
- Note budget and timeline constraints

For Outreach Targets:
- Research the company first → research_company()
- Identify their industry and likely challenges
- Search for similar past work

Then proceed with research → generation → review workflow.
```

---

## Token Efficiency Summary

| Tool | Concise | Detailed | Max |
|------|---------|----------|-----|
| research_company | ~200 | ~800 | 1,000 |
| search_relevant_projects | ~250 | ~1,000 | 1,500 |
| get_project_details | ~300 | ~1,500 | 2,000 |
| generate_content | N/A | ~500-800 | 1,000 |
| review_and_score | N/A | ~200-400 | 500 |

**Total Workflow:** 1,450 - 4,500 tokens
**Saved:** ~100 tokens (no analyze_requirements call)

---

## Expected Impact

### Performance Metrics (Research-Backed)

| Metric | Current (Manual) | With Agent | Source |
|--------|------------------|------------|--------|
| Time per proposal | 30-60 min | <5 min | 5-10x faster |
| Company research | 10 min | 30 sec | 20x faster |
| Win rate improvement | Baseline | +33% | [Iris AI](https://www.heyiris.ai/blog/ai-proposal-writing-assistant) |
| Personalization impact | Generic | 6x transaction rate | [Persana](https://persana.ai/blogs/cold-email-automation-tools) |
| Volume capacity | 5-10/week | 30-50/week | 3-5x volume |

### Business Impact (Conservative)

**Assumptions:**
- Current: 2 projects/month @ $20K avg
- Improved win rate: +20%
- Volume increase: 3x

**Result:**
- New projects/month: 2.4 (from 2)
- Additional revenue: $9,600/month = $115K/year

---

## References

- [Anthropic: Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [AI Proposal Tools Impact](https://www.heyiris.ai/blog/ai-proposal-writing-assistant)
- [Win Rate Factors](https://forecastio.ai/blog/master-your-win-rates-to-accelerate-sales-efficiency)
- [Cold Email Personalization](https://persana.ai/blogs/cold-email-automation-tools)
- [B2B Lead Generation with AI](https://www.landbase.com/blog/5-ways-agentic-ai-is-reinventing-outbound-lead-generation-in-2025)

---

**End of Document**
