# Product Requirements Document (PRD)
## Brainforge Proposal & Outreach Agent

**Version:** 1.0
**Date:** 2025-12-29
**Status:** MVP Planning
**Owner:** Brainforge Internal Development

---

## Executive Summary

The **Brainforge Proposal & Outreach Agent** is an AI-powered tool designed to help Brainforge's BD/sales team write highly personalized Upwork proposals and cold outreach emails at scale. By leveraging deep company research (via Brave Search) and intelligent retrieval of past work (via RAG), the agent generates tailored content in under 5 minutes—dramatically increasing both volume and win rates.

**Core Problem:** Manual proposal writing is slow (30-60 minutes per proposal), often generic, and limits how many opportunities we can pursue. Current win rates suffer from lack of personalization and depth.

**Solution:** AI agent that researches target companies, finds relevant past projects from our knowledge base, and generates specific, metric-driven proposals with a quality score ≥8/10.

**Expected Impact:**
- ⏱️ **Time:** 30-60 min → <5 min per proposal (10x faster)
- 📈 **Win Rate:** +20-33% improvement
- 📊 **Volume:** 3-5x capacity increase
- 💰 **Revenue:** +$115K annually (conservative estimate)

---

## Mission & Vision

### Mission
Empower Brainforge's BD team to win more clients by automating proposal research and generation while maintaining high personalization and quality standards.

### Vision
**MVP:** Internal tool that generates copy-paste ready proposals and outreach emails with deep personalization based on company research and past work.

**Future:** Intelligent sales automation platform that learns from wins/losses and auto-applies to qualified opportunities across multiple platforms (Upwork, Catalant, Contra).

---

## Target Users

### Primary User: Brainforge BD/Sales Team
- **Who:** Business development team members responsible for winning new clients
- **Current Process:** Manually write proposals by researching companies, searching past work docs, crafting custom responses
- **Pain Points:**
  - Time-consuming (30-60 min per proposal)
  - Generic proposals (no time for deep research)
  - Limited volume (5-10 proposals/week max)
  - Inconsistent quality
  - Can't remember all past projects

### User Personas

**Persona 1: Sales Lead**
- Writes 10-15 proposals/week
- Needs speed + quality
- Wants to focus on high-value opportunities

**Persona 2: BD Team Member**
- Handles cold outreach campaigns
- Needs personalization at scale
- Tracks multiple prospects simultaneously

---

## Success Metrics (MVP)

### Primary KPIs

| Metric | Baseline | MVP Target | Measurement |
|--------|----------|------------|-------------|
| **Time per Proposal** | 30-60 min | <5 min | Time from input to final draft |
| **Win Rate** | Current rate | +20% to +33% | Proposals sent vs won |
| **Volume Capacity** | 5-10/week | 30-50/week | Proposals generated per week |
| **Quality Score** | Varies | ≥8/10 | Agent review score |
| **Personalization** | Low | High | Company context included (yes/no) |

### Secondary KPIs
- Response rate for outreach emails
- Time saved per week
- User satisfaction (team feedback)
- Number of specific project examples referenced

### Success Criteria (MVP Launch)
- ✅ Generate proposal in <5 minutes
- ✅ Quality score ≥8/10 consistently
- ✅ Includes company research when available
- ✅ References at least 1 specific past project with metrics
- ✅ Team adopts tool for 80%+ of proposals

---

## MVP Scope

### In Scope (MVP)

#### Core Capabilities
1. **Company Research** - Brave Search integration for target intelligence
2. **Knowledge Retrieval** - RAG search across 50-60 case studies/decks
3. **Content Generation** - Upwork proposals + cold outreach emails
4. **Quality Assurance** - Automated review with scoring
5. **Copy-Paste Workflow** - Easy export of generated content

#### Use Cases
- ✅ Upwork job application proposals
- ✅ Cold outreach emails to target companies
- ✅ RFP responses (basic)

#### Content Types
- Upwork proposals (400-600 words)
- Outreach emails (3-4 paragraphs)
- RFP responses (structured)

### Out of Scope (Post-MVP)

#### Not Included in MVP
- ❌ Direct Upwork API integration
- ❌ CRM integration
- ❌ Email automation/sending
- ❌ Auto-apply to jobs
- ❌ Win/loss tracking system
- ❌ Multi-user authentication
- ❌ Analytics dashboard
- ❌ Mobile app

These features are reserved for post-MVP iterations based on learning and validation.

---

## User Stories

### Epic 1: Upwork Proposal Generation

**Story 1.1: Quick Proposal for Known Company**
```
As a BD team member,
I want to paste an Upwork job posting and get a tailored proposal in <5 minutes,
So that I can apply to more opportunities without sacrificing quality.

Acceptance Criteria:
- Paste job posting → click "Generate"
- Agent researches company (if mentioned)
- Agent finds 2-3 relevant past projects
- Agent generates 400-600 word proposal
- Quality score ≥8/10
- Copy button to grab content
- Time: <5 minutes total
```

**Story 1.2: Generic Job Without Company**
```
As a BD team member,
I want to generate proposals even when no company is mentioned,
So that I can respond to all opportunities.

Acceptance Criteria:
- Agent extracts tech stack and requirements
- Searches past work by technology/industry
- Generates relevant proposal
- Still includes specific examples
```

### Epic 2: Cold Outreach Campaign

**Story 2.1: Personalized Outreach Email**
```
As a BD team member,
I want to input a target company name and get a personalized outreach email,
So that I can run outbound campaigns at scale.

Acceptance Criteria:
- Input: Company name
- Agent researches company via Brave
- Agent finds relevant case study
- Generates 3-4 paragraph email
- Includes company-specific context
- Copy button for email
- Time: <3 minutes
```

### Epic 3: Quality & Iteration

**Story 3.1: Review and Refine**
```
As a BD team member,
I want the agent to review its own output and suggest improvements,
So that I'm confident the proposal meets quality standards.

Acceptance Criteria:
- Automatic quality score (1-10)
- Specific improvement suggestions
- Option to regenerate with feedback
- Clear pass/fail on quality threshold (8/10)
```

---

## Technical Architecture

### Technology Stack

**Agent Framework:**
- **PydanticAI** - Agent orchestration and tool management (provider-agnostic)
- **LLM Provider** - Flexible, supports:
  - OpenAI (GPT-4, GPT-4o, etc.)
  - Azure OpenAI
  - Anthropic (Claude)
  - Ollama (local models)
  - Any OpenAI-compatible API

**Data & Storage:**
- **Supabase** - PostgreSQL + PGVector for knowledge base
- **PGVector** - Vector embeddings for semantic search

**External APIs:**
- **Brave Search API** - Company research and intelligence
- **Embeddings Provider** - Flexible:
  - OpenAI Embeddings API
  - Azure OpenAI Embeddings
  - Ollama (local embeddings)

**UI:**
- **Replit Frontend** - Existing working frontend (to be adapted for this use case)

### Provider Configuration

**PydanticAI is provider-agnostic** - switch between LLM providers via environment variables:

```python
# .env configuration
LLM_PROVIDER=azure_openai  # or 'openai', 'anthropic', 'ollama'
LLM_BASE_URL=https://your-azure-endpoint.openai.azure.com/
LLM_API_KEY=your-api-key
LLM_CHOICE=gpt-4o  # or 'claude-3-5-sonnet', etc.

EMBEDDING_PROVIDER=azure_openai  # or 'openai', 'ollama'
EMBEDDING_BASE_URL=https://your-azure-endpoint.openai.azure.com/
EMBEDDING_API_KEY=your-api-key
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
```

No code changes required to switch providers - just update environment variables.

### Agent Tools (5 Core Tools)

Based on [Anthropic's tool design principles](https://www.anthropic.com/engineering/writing-tools-for-agents):

#### 1. `research_company`
- **Purpose:** Deep company intelligence via Brave Search
- **Input:** Company name, focus areas
- **Output:** Business context, tech stack, pain points, recent news
- **Token Budget:** 200-1000 tokens

#### 2. `search_relevant_projects`
- **Purpose:** Find matching past work (RAG)
- **Input:** Query, tech filters, industry
- **Output:** Ranked list of relevant projects
- **Token Budget:** 250-1500 tokens

#### 3. `get_project_details`
- **Purpose:** Retrieve full case study content
- **Input:** Project ID, sections
- **Output:** Complete project details with metrics
- **Token Budget:** 300-1500 tokens

#### 4. `generate_content`
- **Purpose:** Create proposals or outreach emails
- **Input:** Content type, research context, projects
- **Output:** Formatted draft with metadata
- **Token Budget:** 500-1000 tokens

#### 5. `review_and_score`
- **Purpose:** Quality assurance and feedback
- **Input:** Generated content, original requirements
- **Output:** Quality score, issues, suggestions
- **Token Budget:** 200-500 tokens

**See:** `MVP-tool-designs.md` for complete specifications

### Data Pipeline

**Knowledge Base Sources:**
- 50-60+ case study PDFs → Markdown conversion
- Pitch decks and presentations
- Past winning proposals (if available)
- Team profiles and capabilities

**RAG Pipeline:**
- Existing RAG pipeline (Google Drive + Local Files)
- Supabase ingestion
- Vector embedding and indexing
- Metadata enrichment (tech_stack, industry, metrics)

### Workflow Architecture

```
User Input (Job Posting/Company)
    ↓
Agent parses naturally (no dedicated tool)
    ↓
[RESEARCH PHASE]
- research_company (if company mentioned)
- search_relevant_projects (tech + industry filters)
- get_project_details (top 2-3 matches)
    ↓
[GENERATION PHASE]
- generate_content (all context combined)
    ↓
[QUALITY PHASE]
- review_and_score (validate quality)
    ↓
Output: Copy-paste ready proposal (≥8/10 score)
```

---

## User Experience (MVP)

### Replit Frontend (Adapted)

```
┌─────────────────────────────────────────────┐
│  🎯 Brainforge Proposal Writer             │
├─────────────────────────────────────────────┤
│                                             │
│  Mode: ◉ Upwork Proposal  ○ Outreach       │
│                                             │
├─────────────────────────────────────────────┤
│  📋 Input:                                  │
│  ┌─────────────────────────────────────┐   │
│  │ Paste job posting or company name  │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [Generate Proposal] 🚀                    │
│                                             │
├─────────────────────────────────────────────┤
│  🔍 Research Summary:                       │
│                                             │
│  🏢 Company: Acme E-commerce Inc           │
│  📍 Industry: E-commerce                   │
│  💻 Tech: Shopify, basic analytics         │
│  📰 Recent: Expanding to wholesale          │
│                                             │
│  📚 Relevant Projects Found:               │
│  ✅ Amazon Dashboard (95% match)           │
│  ✅ ABC Home Case Study (80% match)        │
│                                             │
├─────────────────────────────────────────────┤
│  📝 Generated Proposal:                     │
│  ┌─────────────────────────────────────┐   │
│  │ [Full proposal text here...]        │   │
│  │                                     │   │
│  │ Quality Score: 9/10 ✓               │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [📋 Copy to Clipboard] [🔄 Regenerate]   │
│  [✏️ Edit] [💾 Save]                       │
│                                             │
└─────────────────────────────────────────────┘
```

**Note:** Existing Replit frontend will be adapted to support proposal writer workflow. Core functionality exists; UI adjustments needed for dual-mode (Upwork/Outreach) and copy-paste features.

### Key UX Features

**1. Copy-Paste Workflow**
- ✅ One-click copy to clipboard
- ✅ Preserves formatting
- ✅ Ready to paste into Upwork/email

**2. Transparency**
- ✅ Show research summary
- ✅ Show which projects were used
- ✅ Show quality score

**3. Iteration**
- ✅ Regenerate with feedback
- ✅ Manual editing before copy
- ✅ Save drafts

**4. Speed**
- ✅ <5 minute total workflow
- ✅ Progress indicators
- ✅ Streaming generation (see content being written)

---

## Data Requirements

### Knowledge Base Preparation

**User Responsibility:**
- Convert 50-60+ PDFs → Markdown format
- Add metadata frontmatter (tech_stack, industry, metrics)
- Organize into folders (case-studies/, decks/, proposals/)

**Metadata Schema (YAML frontmatter):**
```yaml
---
title: "Project Name"
client: "Client Name"
industry: "E-commerce"
project_type: "BI_Analytics"
tech_stack: ["Snowflake", "dbt", "Tableau"]
metrics:
  - type: "win_rate"
    value: 33
    unit: "percent"
testimonial: true
---
```

**Data Pipeline:**
- Use existing RAG pipeline (Local Files mode)
- Ingest Markdown files to Supabase
- Vector embeddings via OpenAI or Ollama
- Metadata indexing for filters

### Quality Standards

**All documents must include:**
- Clear project description
- Technologies used
- Client industry
- Quantifiable results/metrics
- Client testimonials (if available)

---

## Non-Functional Requirements

### Performance
- **Response Time:** <5 minutes for complete proposal
- **Availability:** 99% uptime (Replit + Supabase)
- **Concurrency:** Support 1-3 simultaneous users (MVP)

### Quality
- **Accuracy:** Quality score ≥8/10 consistently
- **Relevance:** Search results must match requirements
- **Personalization:** Company context included when available

### Security & Compliance
- **Data Privacy:** All data stored in Brainforge-controlled Supabase
- **API Keys:** Secure storage in environment variables
- **Access Control:** Local deployment (no public access for MVP)
- **Compliance:** GDPR consideration for client data (note: important for future)

### Scalability (Future)
- MVP handles 1-3 users
- Post-MVP: Multi-user support, auth, role-based access

---

## Roadmap

### Phase 1: MVP (Current)
**Scope:** Core 5 tools, copy-paste workflow

**Deliverables:**
- ✅ 5 agent tools implemented
- ✅ Brave Search integration
- ✅ RAG pipeline connected to Supabase
- ✅ Replit frontend adapted (dual mode: Upwork + Outreach)
- ✅ Copy-to-clipboard functionality
- ✅ Quality scoring
- ✅ 50-60 case studies ingested

**Success Criteria:**
- Generate proposal in <5 minutes
- Quality score ≥8/10
- Team adoption ≥80%

---

### Phase 2: Learning & Optimization (Post-MVP)
**Scope:** Track outcomes, learn from data

**Features:**
- Win/loss tracking
- Pattern identification (what works)
- A/B testing different approaches
- Proposal template library
- Success analytics dashboard

**Expected Impact:**
- Win rate optimization
- Template improvements
- Data-driven insights

---

### Phase 3: Automation (Future)
**Scope:** Reduce manual effort further

**Features:**
- Auto-apply to qualified Upwork jobs
- Multi-platform support (Catalant, Contra)
- Email automation for outreach
- CRM integration
- Scheduled outreach campaigns

**Expected Impact:**
- 10x volume increase
- Fully automated prospecting
- Focus on high-value conversations only

---

### Phase 4: Platform Expansion (Vision)
**Scope:** Scale beyond Brainforge

**Potential:**
- Offer as product to other consulting firms
- White-label solution
- API access
- Enterprise features (multi-tenant, SSO)

**Decision Point:** After Phase 2 validation

---

## Risks & Mitigations

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Brave API rate limits | Medium | Low | Implement caching, smart query batching |
| RAG retrieval quality | High | Medium | Manual review of knowledge base, iterative improvement |
| Token costs (Claude API) | Medium | Medium | Optimize prompts, use response_format controls |
| Supabase performance | Medium | Low | Index optimization, query caching |

### Product Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Generated proposals too generic | High | Medium | Quality scoring, require specific examples |
| Team doesn't adopt tool | High | Low | Involve team in testing, gather feedback |
| Win rates don't improve | High | Low | Track metrics, iterate on quality |
| Data prep takes too long | Medium | Medium | Prioritize top 20 case studies first |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Competitors use similar tools | Low | High | Differentiation through company research depth |
| Platform policy changes (Upwork) | Medium | Low | Manual review before sending |
| Over-reliance on automation | Medium | Medium | Quality thresholds, human review |

---

## Dependencies & Assumptions

### Dependencies
- **External APIs:**
  - Brave Search API (company research)
  - LLM Provider (OpenAI, Azure OpenAI, or Anthropic)
  - Embeddings Provider (OpenAI, Azure OpenAI, or Ollama)

- **Infrastructure:**
  - Supabase instance (database + vector store)
  - Replit environment (existing frontend)

- **Data:**
  - 50-60 case studies converted to Markdown
  - Metadata added to all documents

### Assumptions
- ✅ Team has Brave API access
- ✅ Supabase already set up with PGVector
- ✅ Existing RAG pipeline functional
- ✅ User will handle PDF → Markdown conversion
- ✅ Quality threshold of 8/10 is achievable
- ✅ Company research via Brave provides sufficient context
- ✅ Copy-paste workflow acceptable for MVP
- ✅ LLM provider (OpenAI/Azure/Claude) selected and configured
- ✅ PydanticAI supports provider switching via environment variables

---

## Open Questions

### Product Questions
1. Should we support batch processing (multiple jobs at once)?
2. Do we need version history for proposals?
3. Should we track which proposals were actually sent?

### Technical Questions
1. How to handle very long job postings (>5000 words)?
2. Should we cache company research results to reduce API calls?
3. What's the optimal chunk size for RAG embeddings?

### Business Questions
1. What's the actual current win rate (baseline)?
2. How many proposals does team currently send per week?
3. What percentage of time is spent on research vs writing?

---

## Appendix

### Related Documents
- **MVP Tool Designs:** `MVP-tool-designs.md` - Complete tool specifications
- **Architecture Guide:** `.agents/external-docs/vertical-slice-architecture-setup-guide.md`
- **Anthropic Guide:** [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)

### Key Research Sources
- [AI Proposal Tools Impact (2025)](https://www.heyiris.ai/blog/ai-proposal-writing-assistant)
- [Win Rate Optimization](https://forecastio.ai/blog/master-your-win-rates-to-accelerate-sales-efficiency)
- [Cold Email Personalization ROI](https://persana.ai/blogs/cold-email-automation-tools)
- [B2B Lead Generation with AI](https://www.landbase.com/blog/5-ways-agentic-ai-is-reinventing-outbound-lead-generation-in-2025)

---

**Document Status:** Ready for Implementation
**Next Steps:** Begin Phase 1 (MVP) development
**Approval Required:** Brainforge Leadership

---

**End of Document**
