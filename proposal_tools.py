"""
Proposal writer tools for Brainforge MVP.

This module implements 5 specialized PydanticAI tools:
1. research_company - Company intelligence via Brave Search
2. search_relevant_projects - Enhanced RAG with metadata filters
3. get_project_details - Selective case study retrieval
4. generate_content - Template-based proposal/email generator
5. review_and_score - Quality assurance with feedback
"""

from __future__ import annotations

from typing import List, Dict, Literal, Optional, Any
from pydantic_ai import RunContext
from httpx import AsyncClient
from supabase import Client
from openai import AsyncOpenAI
import re
import json

from proposal_schemas import (
    CompanyResearch, ProjectMatch, ProjectSearchResults,
    ProjectDetails, Results, GeneratedContent, Issue, ContentReview
)
from restriction_validator import (
    check_forbidden_phrases,
    check_required_elements,
    get_word_count_range
)
from template_schemas import ContentRestriction
from tools import get_embedding


# ========== Tool 1: Company Research ==========

def build_company_search_queries(company_name: str, focus_areas: Optional[List[str]] = None) -> List[str]:
    """Generate targeted Brave search queries for company research."""
    queries = [
        f"{company_name} company",
        f"{company_name} technology stack",
        f"{company_name} recent news",
    ]

    if focus_areas:
        for area in focus_areas[:2]:
            queries.append(f"{company_name} {area}")

    return queries


async def execute_brave_search(query: str, http_client: AsyncClient, api_key: str) -> dict:
    """Execute Brave Search API call. Pattern from tools.py:16-52."""
    headers = {
        'X-Subscription-Token': api_key,
        'Accept': 'application/json',
    }

    response = await http_client.get(
        'https://api.search.brave.com/res/v1/web/search',
        params={
            'q': query,
            'count': 5,
            'text_decorations': True,
            'search_lang': 'en'
        },
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def parse_brave_results_to_company_research(results_list: List[dict], company_name: str) -> CompanyResearch:
    """Parse Brave API responses into CompanyResearch model."""
    all_results = []
    for result in results_list:
        web_results = result.get('web', {}).get('results', [])
        all_results.extend(web_results[:3])

    industry = "Unknown"
    business_description = ""
    size_estimate = "SMB"
    tech_stack = []
    recent_developments = []
    pain_points = []
    key_people = []
    sources = []

    for item in all_results:
        title = item.get('title', '')
        description = item.get('description', '')
        url = item.get('url', '')

        sources.append(url)

        full_text = f"{title} {description}".lower()

        if not business_description and len(description) > 50:
            business_description = description[:200]

        if any(ind.lower() in full_text for ind in ["saas", "software", "cloud"]):
            industry = "SaaS"
        elif any(ind.lower() in full_text for ind in ["ecommerce", "e-commerce", "retail"]):
            industry = "E-commerce"
        elif any(ind.lower() in full_text for ind in ["healthcare", "health", "medical"]):
            industry = "Healthcare"

        for tech in ["python", "react", "aws", "azure", "postgresql", "mongodb", "kubernetes", "docker"]:
            if tech in full_text and tech.title() not in tech_stack:
                tech_stack.append(tech.title())

        if any(word in full_text for word in ["funding", "raised", "series", "acquisition", "launched"]):
            if description:
                recent_developments.append(description[:150])

    if "enterprise" in business_description.lower() or "1000+" in business_description:
        size_estimate = "enterprise"
    elif "startup" in business_description.lower() or "founded 20" in business_description:
        size_estimate = "startup"

    return CompanyResearch(
        company_name=company_name,
        industry=industry,
        business_description=business_description or f"Company operating in {industry} sector",
        size_estimate=size_estimate,
        tech_stack=tech_stack[:5],
        recent_developments=recent_developments[:3],
        pain_points=pain_points,
        key_people=key_people,
        sources=sources[:5]
    )


async def research_company(
    ctx: RunContext[AgentDeps],
    company_name: str,
    response_format: Literal["concise", "detailed"] = "concise"
) -> str:
    """
    Research target company using Brave Search API.

    IMPORTANT: Only call this tool if a specific company name is mentioned in the job posting.
    Do NOT call for generic terms or if no company is mentioned.

    Args:
        ctx: Context with HTTP client and Brave API key
        company_name: Company to research (must be a real company name, not generic terms)
        response_format: "concise" (top 3 sources) or "detailed" (top 10 sources)

    Returns:
        JSON string with CompanyResearch schema
    """
    # Validate company_name is not empty or generic
    if not company_name or len(company_name.strip()) < 2:
        print(f"Skipping research_company: No company name provided")
        return CompanyResearch(
            company_name="Unknown",
            industry="Unknown",
            business_description="No company specified",
            size_estimate="Unknown",
            tech_stack=[],
            recent_developments=[],
            pain_points=[],
            key_people=[],
            sources=[]
        ).model_dump_json()

    # Skip generic/invalid terms that waste API calls
    generic_terms = ['company', 'client', 'organization', 'business', 'firm', 'startup', 'technology', 'tech stack']
    company_lower = company_name.lower().strip()
    if company_lower in generic_terms or all(term in company_lower for term in ['the', 'a', 'an']):
        print(f"Skipping research_company: '{company_name}' appears to be generic, not a real company")
        return CompanyResearch(
            company_name=company_name,
            industry="Unknown",
            business_description="Generic term provided instead of company name",
            size_estimate="Unknown",
            tech_stack=[],
            recent_developments=[],
            pain_points=[],
            key_people=[],
            sources=[]
        ).model_dump_json()

    try:
        print(f"Calling research_company for: {company_name}")
        queries = build_company_search_queries(company_name)
        max_queries = 2 if response_format == "concise" else 4

        results = []
        for query in queries[:max_queries]:
            search_result = await execute_brave_search(query, ctx.deps.http_client, ctx.deps.brave_api_key)
            results.append(search_result)

        company_research = parse_brave_results_to_company_research(results, company_name)
        return company_research.model_dump_json()

    except Exception as e:
        print(f"Error in research_company: {e}")
        fallback = CompanyResearch(
            company_name=company_name,
            industry="Unknown",
            business_description=f"Unable to research {company_name} at this time.",
            size_estimate="SMB",
            tech_stack=[],
            recent_developments=[],
            pain_points=[],
            key_people=[],
            sources=[]
        )
        return fallback.model_dump_json()


# ========== Tool 2: Search Relevant Projects ==========

def build_enriched_project_match(search_doc: dict, full_study: dict) -> ProjectMatch:
    """
    Build enriched ProjectMatch using FULL case study data from get_case_study_full RPC.

    Args:
        search_doc: Original search result (for relevance score)
        full_study: Full case study data from get_case_study_full()

    Returns:
        ProjectMatch with complete context and all metrics
    """
    frontmatter = full_study.get('frontmatter', {}) or {}
    chunks = full_study.get('chunks', []) or []
    metrics = full_study.get('metrics', []) or []

    # Extract ALL metrics from chunks and metrics table
    all_metrics = []

    # Get metrics from document_rows table
    if metrics:
        for metric in metrics:
            if isinstance(metric, dict):
                value = metric.get('value', '')
                unit = metric.get('unit', '')
                metric_str = f"{value}{unit}" if unit else str(value)
                all_metrics.append(metric_str)

    # Get metrics from content text (Results section)
    results_chunks = [c for c in chunks if c.get('section', '').lower() == 'results']
    for chunk in results_chunks:
        content = chunk.get('content', '')
        found = re.findall(
            r'(\d+(?:\.\d+)?%?\s*(?:reduction|improvement|increase|faster|savings?|saved|\$\d+[KM]?|weeks?|months?|x\s*faster))',
            content,
            re.IGNORECASE
        )
        all_metrics.extend(found[:3])

    # Build rich summary with ALL sections
    summary_parts = []
    for section_name in ['challenge', 'solution', 'results']:
        section_chunks = [c for c in chunks if c.get('section', '').lower() == section_name]
        if section_chunks:
            section_text = " ".join([c.get('content', '')[:200] for c in section_chunks[:2]])
            summary_parts.append(f"**{section_name.title()}**: {section_text}")

    rich_summary = "\n".join(summary_parts)

    # Add metrics at the top
    if all_metrics:
        metrics_str = ", ".join(list(dict.fromkeys(all_metrics))[:5])  # Unique, top 5
        rich_summary = f"**Key Metrics**: {metrics_str}\n\n{rich_summary}"

    return ProjectMatch(
        project_id=full_study.get('file_id', 'unknown'),
        project_name=frontmatter.get('title', full_study.get('file_name', 'Unknown Project')),
        project_type=frontmatter.get('project_type', 'Unknown'),
        industry=frontmatter.get('industry', 'Unknown'),
        technologies_used=frontmatter.get('tech_stack', []),
        key_metric=all_metrics[0] if all_metrics else "",
        relevance_score=search_doc.get('combined_score', 0.5),
        summary=rich_summary
    )


def format_project_match(doc: dict, mode: Literal["concise", "detailed"] = "concise") -> ProjectMatch:
    """
    Format hybrid search result as ProjectMatch model.

    NEW: Uses frontmatter from document_metadata (normalized schema).
    """
    chunk_metadata = doc.get('chunk_metadata', {})
    frontmatter = doc.get('frontmatter', {}) or {}

    project_match = ProjectMatch(
        project_id=chunk_metadata.get('file_id', 'unknown'),
        project_name=frontmatter.get('title', chunk_metadata.get('file_title', 'Untitled Project')),
        project_type=frontmatter.get('project_type', 'Unknown'),
        industry=frontmatter.get('industry', 'Unknown'),
        technologies_used=frontmatter.get('tech_stack', []),
        key_metric="",
        relevance_score=doc.get('combined_score', 0.0),  # RRF combined score
        summary=None
    )

    # Extract key metric from content or frontmatter
    content = doc.get('content', '')

    if mode == "detailed" and content:
        # In detailed mode, extract ALL metrics and include in summary
        metrics_found = re.findall(
            r'(\d+(?:\.\d+)?%?\s*(?:reduction|improvement|increase|faster|savings?|saved|\$\d+[KM]?|weeks?|months?|days?|hours?|x faster))',
            content,
            re.IGNORECASE
        )

        section = chunk_metadata.get('section', '')

        # Build rich summary with metrics
        if metrics_found:
            metrics_str = ", ".join(metrics_found[:3])  # Top 3 metrics
            project_match.key_metric = metrics_found[0]  # Primary metric
            project_match.summary = f"[{section}] Metrics: {metrics_str}. {content[:300]}..."
        else:
            project_match.summary = f"[{section}] {content[:400]}..."
    else:
        # Concise mode: just extract first metric
        metrics_match = re.search(r'(\d+%?\s*(?:reduction|improvement|increase|faster|savings|saved))', content, re.IGNORECASE)
        if metrics_match:
            project_match.key_metric = metrics_match.group(1)

    return project_match


async def search_relevant_projects(
    ctx: RunContext[AgentDeps],
    query: str,
    tech_filter: Optional[List[str]] = None,
    industry: Optional[str] = None,
    project_type: Optional[str] = None,
    section: Optional[str] = None,
    max_results: int = 5,
    mode: Literal["concise", "detailed"] = "concise"
) -> str:
    """
    Search case studies using HYBRID SEARCH (vector + FTS + RRF).

    NEW BEHAVIOR:
    - Uses search_hybrid_rag RPC function (combines vector + full-text search)
    - Filters at database level (faster, more accurate)
    - Returns frontmatter from document_metadata (normalized schema)
    - RRF ranking for better relevance

    Args:
        ctx: Context with Supabase and embedding clients
        query: Search query (semantic + keyword matching)
        tech_filter: Filter by technologies (e.g., ["Snowflake", "n8n"])
        industry: Filter by industry (e.g., "Home Services", "E-commerce")
        project_type: Filter by type (e.g., "AI_ML", "BI_Analytics")
        section: Filter by section (e.g., "Results", "Challenge")
        max_results: Max projects to return (default: 5)
        mode: "concise" or "detailed"

    Returns:
        JSON string with ProjectSearchResults schema

    Example:
        search_relevant_projects(
            query="Snowflake data warehouse analytics dashboard",
            tech_filter=["Snowflake", "dbt"],
            industry="E-commerce",
            max_results=3
        )
    """
    try:
        print(f"[SEARCH] Query: '{query}' | Industry: {industry} | Type: {project_type} | Tech: {tech_filter}")

        # Get embedding for vector search component
        query_embedding = await get_embedding(query, ctx.deps.embedding_client)

        # Use ONLY the first tech for database filter (RPC doesn't support arrays)
        tech_for_filter = tech_filter[0] if tech_filter and len(tech_filter) > 0 else None

        # Call hybrid search RPC (vector + FTS with RRF)
        result = ctx.deps.supabase.rpc(
            'search_hybrid_rag',
            {
                'query_text': query,
                'query_embedding': query_embedding,
                'match_count': max_results,
                'industry_filter': industry,
                'project_type_filter': project_type,
                'tech_filter': tech_for_filter,
                'section_filter': section
            }
        ).execute()

        if not result.data:
            print("[SEARCH] No results found")
            return ProjectSearchResults(
                matches=[],
                total_found=0,
                search_query=query,
                filters_applied={}
            ).model_dump_json()

        # Format results - but in detailed mode, get FULL case study details
        matches = []
        if mode == "detailed":
            # Get full case study for top matches (includes all sections + metrics)
            print(f"[SEARCH] Fetching full details for top {min(3, len(result.data))} matches...")
            for doc in result.data[:3]:  # Top 3 only
                file_id = doc.get('chunk_metadata', {}).get('file_id')
                if file_id:
                    try:
                        # Call get_case_study_full RPC
                        full_study = ctx.deps.supabase.rpc(
                            'get_case_study_full',
                            {'case_study_file_id': file_id}
                        ).execute()

                        if full_study.data and len(full_study.data) > 0:
                            study_data = full_study.data[0]
                            # Build enriched ProjectMatch with full context
                            enriched_match = build_enriched_project_match(doc, study_data)
                            matches.append(enriched_match)
                        else:
                            # Fallback to basic format if RPC fails
                            matches.append(format_project_match(doc, mode))
                    except Exception as e:
                        print(f"[SEARCH] Error fetching full study for {file_id}: {e}")
                        matches.append(format_project_match(doc, mode))
                else:
                    matches.append(format_project_match(doc, mode))
        else:
            # Concise mode: just basic formatting
            matches = [format_project_match(doc, mode) for doc in result.data]

        # Build filters_applied dict
        filters_applied = {}
        if tech_filter:
            filters_applied['tech_filter'] = tech_filter
        if industry:
            filters_applied['industry'] = industry
        if project_type:
            filters_applied['project_type'] = project_type
        if section:
            filters_applied['section'] = section

        print(f"[SEARCH] Found {len(matches)} matches (scores: {[round(m.relevance_score, 3) for m in matches]})")

        # Return FORMATTED TEXT instead of JSON (PydanticAI pattern)
        formatted_results = []
        for match in matches:
            tech_str = ", ".join(match.technologies_used) if match.technologies_used else "N/A"
            metric_str = match.key_metric if match.key_metric else "N/A"

            project_text = f"""# {match.project_name}
**Project ID:** {match.project_id}
**Project Type:** {match.project_type}
**Industry:** {match.industry}
**Technologies:** {tech_str}
**Key Metric:** {metric_str}
**Relevance Score:** {match.relevance_score:.2f}

{match.summary if match.summary else 'No summary available.'}
"""
            formatted_results.append(project_text)

        results_text = "\n\n---\n\n".join(formatted_results)

        filters_str = ", ".join([f"{k}={v}" for k, v in filters_applied.items()]) if filters_applied else "None"

        header = f"""Search Results for: "{query}"
Filters Applied: {filters_str}
Total Matches: {len(matches)}

==========================================

"""
        return header + results_text

    except Exception as e:
        print(f"Error in search_relevant_projects: {e}")
        import traceback
        traceback.print_exc()
        return f"Error searching projects: {str(e)}\n\nNo projects found for query: '{query}'"


# ========== Tool 3: Get Project Details ==========

def parse_markdown_sections(content: str) -> Dict[str, str]:
    """Split markdown by ## headers."""
    sections = {}
    lines = content.split('\n')
    current_section = None
    current_content = []

    for line in lines:
        if line.startswith('## '):
            if current_section:
                sections[current_section.lower()] = '\n'.join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        else:
            if current_section:
                current_content.append(line)

    if current_section:
        sections[current_section.lower()] = '\n'.join(current_content).strip()

    return sections


def extract_metrics_from_section(section_text: str) -> Dict[str, Any]:
    """Extract quantifiable metrics from text using regex."""
    metrics = {}

    percentages = re.findall(r'(\d+)%\s*(reduction|improvement|increase|faster)', section_text, re.IGNORECASE)
    for value, metric_type in percentages:
        key = f"{metric_type.lower()}_percent"
        metrics[key] = int(value)

    dollar_amounts = re.findall(r'\$(\d+(?:,\d+)*(?:\.\d+)?)\s*([MKmk]?)', section_text)
    for amount, suffix in dollar_amounts:
        clean_amount = float(amount.replace(',', ''))
        if suffix.upper() == 'M':
            clean_amount *= 1_000_000
        elif suffix.upper() == 'K':
            clean_amount *= 1_000
        metrics['cost_savings'] = clean_amount

    return metrics


async def get_project_details(
    ctx: RunContext[AgentDeps],
    project_id: str,
    sections: List[str] = ["context", "challenge", "solution", "results"]
) -> str:
    """
    Get detailed sections from a case study using normalized schema.

    NEW BEHAVIOR:
    - Uses get_case_study_full RPC (retrieves from document_metadata + documents + document_rows)
    - Returns frontmatter, all chunks organized by section, and metrics
    - Single efficient query instead of multiple table scans

    Args:
        ctx: Context with Supabase client
        project_id: Project file_id from search results
        sections: Sections to retrieve (filters which sections to include)

    Returns:
        JSON string with ProjectDetails schema

    Example:
        get_project_details(
            project_id="abc_home_dashboard.md",
            sections=["challenge", "solution", "results"]
        )
    """
    try:
        print(f"[GET_DETAILS] Retrieving case study: {project_id}")

        # Call RPC to get full case study from normalized schema
        result = ctx.deps.supabase.rpc(
            'get_case_study_full',
            {'case_study_file_id': project_id}
        ).execute()

        if not result.data or len(result.data) == 0:
            print(f"[GET_DETAILS] No data found for {project_id}")
            return ProjectDetails(
                project_name="Unknown Project",
                client_name="Unknown Client",
                tools_used=[],
                team=[]
            ).model_dump_json()

        case_study = result.data[0]
        frontmatter = case_study.get('frontmatter', {}) or {}
        chunks = case_study.get('chunks', []) or []
        metrics_data = case_study.get('metrics', []) or []

        # Organize chunks by section
        sections_dict = {}
        for chunk in chunks:
            section_name = chunk.get('section', '').lower()
            if section_name not in sections_dict:
                sections_dict[section_name] = []
            sections_dict[section_name].append(chunk.get('content', ''))

        # Combine content for each section
        for section_name in sections_dict:
            sections_dict[section_name] = '\n\n'.join(sections_dict[section_name])

        # Extract metrics from document_rows and section text
        metrics_dict = {}
        outcomes = []

        # Add metrics from document_rows
        for metric in metrics_data:
            metric_name = metric.get('metric_name', '')
            metric_value = metric.get('value', metric.get('metric_value', ''))
            metrics_dict[metric_name] = metric_value

        # Extract additional metrics from Results section text
        results_text = sections_dict.get('results', '')
        if results_text:
            extracted_metrics = extract_metrics_from_section(results_text)
            metrics_dict.update(extracted_metrics)
            outcomes = [line.strip() for line in results_text.split('\n')
                       if line.strip() and not line.startswith('#') and not line.startswith('|')][:3]

        # Build ProjectDetails response
        project_details = ProjectDetails(
            project_name=frontmatter.get('title', 'Untitled Project'),
            client_name=frontmatter.get('client', 'Unknown Client'),
            context=sections_dict.get('context') if 'context' in [s.lower() for s in sections] else None,
            challenge=sections_dict.get('challenge') if 'challenge' in [s.lower() for s in sections] else None,
            solution=sections_dict.get('solution') if 'solution' in [s.lower() for s in sections] else None,
            results=Results(metrics=metrics_dict, outcomes=outcomes) if 'results' in [s.lower() for s in sections] else None,
            testimonial=sections_dict.get('testimonial'),
            tools_used=frontmatter.get('tech_stack', []),
            team=frontmatter.get('team', []) if isinstance(frontmatter.get('team'), list) else []
        )

        print(f"[GET_DETAILS] Retrieved {len(chunks)} chunks, {len(metrics_dict)} metrics")

        return project_details.model_dump_json()

    except Exception as e:
        print(f"Error in get_project_details: {e}")
        return ProjectDetails(
            project_name="Error retrieving project",
            client_name="Unknown",
            tools_used=[],
            team=[]
        ).model_dump_json()


# ========== Tool 4: Generate Content ==========

def build_text_generation_prompt(
    content_type: Literal["upwork_proposal", "catalant_proposal", "outreach_email", "rfp_response"],
    company_research: Optional[CompanyResearch],
    relevant_projects_text: str,
    user_context: str,
    word_limit: Optional[int] = None
) -> str:
    """Build prompt for content generation using TEXT from search tool (PydanticAI pattern)."""
    if content_type == "upwork_proposal":
        word_count = word_limit if word_limit else "1500 characters"
        prompt = f"""Write an Upwork proposal for this job posting.

JOB POSTING:
{user_context}

"""
        if company_research:
            prompt += f"""COMPANY CONTEXT:
- {company_research.company_name} is in {company_research.industry}
- Tech stack: {', '.join(company_research.tech_stack)}
- {company_research.business_description}

"""

        prompt += f"""RELEVANT BRAINFORGE PROJECTS:
{relevant_projects_text}

CRITICAL: Use this EXACT STRUCTURE for Upwork proposals:

**Intro & Authority:**
I've built analytics functions that drive attributable revenue growth for Athletic Greens, Midi Health, and Stackblitz.

**Positioning & Value Levers:**
[Short credibility statement]. I'll help your team [list 3-4 business value levers like: lower CAC, drive conversions, extend LTV, reduce churn].

**Pain & Solution Summary:**
The biggest business pain appears to be [describe pain from job posting]. I can leverage my expertise in [tools/stack from job] to [solve pain], ensuring [outcome] while providing [additional value].

**Proof of Capability:**
Sample win from 30+ engagements:
[Pick ONE project from above with metrics] – [Brief description with quantified results like "40% faster" or "$50K saved"].

**Recommended Next Steps:**
Here's what I would recommend:
1. [First actionable recommendation specific to their need]
2. [Second recommendation - could reference similar Brainforge clients]
3. [Third recommendation - execution focused]

**Attachment Note:**
Attached: [Brainforge AI Capabilities Deck or Brainforge Data Capabilities Deck] — it shows exactly how Brainforge applies this expertise to deliver [specific result type].

**Close:**
Looking forward to connecting to discuss how we can apply similar outcomes here.

REQUIREMENTS:
- Follow the EXACT structure above (all 7 sections)
- Include 2+ specific metrics from the project examples
- No generic language - use specific technologies and outcomes
- Maximum {word_count}
- NO semicolons or exclamation points
"""

    elif content_type == "catalant_proposal":
        word_count = word_limit if word_limit else "500-800 words"
        prompt = f"""Write a formal Catalant consulting proposal for this project.

PROJECT BRIEF:
{user_context}

"""
        if company_research:
            prompt += f"""COMPANY CONTEXT:
- {company_research.company_name} is in {company_research.industry}
- Tech stack: {', '.join(company_research.tech_stack)}
- {company_research.business_description}

"""

        prompt += f"""RELEVANT BRAINFORGE PROJECTS:
{relevant_projects_text}

CRITICAL: Use this EXACT STRUCTURE for Catalant proposals:

**Credentials Opening:**
I'm a senior analytics architect with 10+ YOE building the data function of a Series B startup (100+ member team) and leading the product analytics team at a 9-figure CPG brand. Now I lead Brainforge, the data and AI consultancy for midmarket businesses looking to unlock enterprise level Business Intelligence.

**Relevance Statement:**
I have experience in [specific domain from job] doing exactly this type of [specific work type from job]. I've completed numerous [relevant project types].

**Past Projects:**
The two past projects I highlighted with this pitch include [Client A] and [Client B].

1. **[Client A from above]**: [2-3 sentence description: project scope, challenge, solution, and quantified outcome with specific metrics]

2. **[Client B from above]**: [2-3 sentence description: project scope, challenge, solution, and quantified outcome with specific metrics]

**Additional Clients:**
Additionally, I've worked with [list 3-5 other clients from above] on [brief description of relevant work].

**Availability:**
I am available to begin this work immediately and look forward to connecting soon.

**Deck Attachment:**
I've attached our [AI/Data] Capabilities Deck. It shows how we [brief value proposition matching their need].

REQUIREMENTS:
- Follow the EXACT structure above (all 6 sections)
- Use REAL client names and metrics from the projects provided
- More formal than Upwork (credentials-first, no next steps)
- Length: {word_count}
- NO semicolons or exclamation points
"""

    elif content_type == "outreach_email":
        word_count = word_limit if word_limit else "100-200"
        prompt = f"""Write a personalized outreach email ({word_count} words) to {company_research.company_name if company_research else 'the company'}:

Context: {user_context}

"""
        if company_research:
            prompt += f"""About {company_research.company_name}:
- Industry: {company_research.industry}
- Tech: {', '.join(company_research.tech_stack[:3])}
- Recent: {company_research.recent_developments[0] if company_research.recent_developments else 'N/A'}

"""

        prompt += f"""Relevant Case Studies:

{relevant_projects_text}

Requirements:
- Personalized opening referencing their business
- 1-2 relevant case study examples with metrics
- Value proposition
- Soft call-to-action (meeting request)
- {word_count} words
"""

    else:
        prompt = f"""Write an RFP response for:

{user_context}

Relevant Project Examples:

{relevant_projects_text}
"""

    return prompt


def build_generation_prompt(
    content_type: Literal["upwork_proposal", "outreach_email", "rfp_response"],
    company_research: Optional[CompanyResearch],
    relevant_projects: List[ProjectMatch],
    user_context: str
) -> str:
    """Build prompt for content generation (DEPRECATED - use build_text_generation_prompt)."""
    if content_type == "upwork_proposal":
        prompt = f"""Write a compelling Upwork proposal (150-300 words) for this job:

{user_context}

"""
        if company_research:
            prompt += f"""Company Context:
- {company_research.company_name} is in {company_research.industry}
- Tech stack: {', '.join(company_research.tech_stack)}
- {company_research.business_description}

"""

        if relevant_projects:
            prompt += f"""Relevant Brainforge Projects:
"""
            for proj in relevant_projects[:2]:
                prompt += f"- {proj.project_name} ({proj.industry}): {proj.key_metric}\n"

        prompt += """
Requirements:
- Reference at least 2 specific metrics from our projects
- Mention company-specific context if available
- Professional, confident tone
- Clear call-to-action
- 150-300 words
"""

    elif content_type == "outreach_email":
        prompt = f"""Write a personalized outreach email (100-200 words) to {company_research.company_name if company_research else 'the company'}:

Context: {user_context}

"""
        if company_research:
            prompt += f"""About {company_research.company_name}:
- Industry: {company_research.industry}
- Tech: {', '.join(company_research.tech_stack[:3])}
- Recent: {company_research.recent_developments[0] if company_research.recent_developments else 'N/A'}

"""

        if relevant_projects:
            prompt += f"""Relevant Case Study:
{relevant_projects[0].project_name} - {relevant_projects[0].key_metric}

"""

        prompt += """
Requirements:
- Personalized opening referencing their business
- 1 relevant case study example
- Value proposition
- Soft call-to-action (meeting request)
- 100-200 words
"""

    else:
        prompt = f"Write an RFP response for:\n\n{user_context}"

    return prompt


async def generate_content(
    ctx: RunContext[AgentDeps],
    content_type: Literal["upwork_proposal", "catalant_proposal", "outreach_email", "rfp_response"],
    company_research_json: str,
    relevant_projects_text: str,
    user_context: str,
    word_limit: Optional[int] = None
) -> str:
    """
    Generate proposal or email with company context and project examples.

    **NEW (PydanticAI Pattern):** Accepts FORMATTED TEXT from search tool, not JSON.

    Args:
        ctx: Context with LLM client
        content_type: Type of content to generate
        company_research_json: JSON from research_company tool (still JSON for now)
        relevant_projects_text: FORMATTED TEXT from search_relevant_projects tool
        user_context: User's notes or job posting text
        word_limit: Optional word count constraint

    Returns:
        JSON string with GeneratedContent schema
    """
    try:
        print(f"[GENERATE] Starting content generation:")
        print(f"  content_type: {content_type}")
        print(f"  company_research_json length: {len(company_research_json) if company_research_json else 0}")
        print(f"  relevant_projects_text length: {len(relevant_projects_text) if relevant_projects_text else 0}")
        print(f"  user_context length: {len(user_context) if user_context else 0}")
        print(f"  word_limit: {word_limit}")

        company_research = None
        if company_research_json:
            try:
                company_research = CompanyResearch.model_validate_json(company_research_json)
                print(f"[GENERATE] Parsed company research: {company_research.company_name}")
            except Exception as e:
                print(f"[GENERATE] Error parsing company_research_json: {e}")
                print(f"[GENERATE] company_research_json content: {company_research_json[:200]}")
                company_research = None

        # Build prompt using text-based context
        prompt = build_text_generation_prompt(
            content_type,
            company_research,
            relevant_projects_text,
            user_context,
            word_limit
        )

        from pydantic_ai import Agent
        from agent import get_model
        model = get_model()
        generator_agent = Agent(model, output_type=str)

        result = await generator_agent.run(prompt)
        content = result.data

        word_count = len(content.split())

        # Extract project names from text (simple regex to find project headers)
        import re
        project_names = re.findall(r'^# (.+)$', relevant_projects_text, re.MULTILINE)
        projects_referenced = project_names[:3] if project_names else []

        personalization_score = 0.5
        if company_research and company_research.company_name.lower() in content.lower():
            personalization_score += 0.3
        if any(metric in content.lower() for metric in ['%', 'reduction', 'improvement', 'faster']):
            personalization_score += 0.2
        personalization_score = min(personalization_score, 1.0)

        token_estimate = len(content.split()) * 2

        return GeneratedContent(
            content=content,
            structure={"full": content},
            word_count=word_count,
            projects_referenced=projects_referenced,
            personalization_score=personalization_score,
            token_estimate=token_estimate
        ).model_dump_json()

    except Exception as e:
        import traceback
        print(f"[GENERATE] ERROR in generate_content: {e}")
        print(f"[GENERATE] Traceback:")
        traceback.print_exc()
        return GeneratedContent(
            content=f"Error generating content: {str(e)}",
            structure={},
            word_count=0,
            projects_referenced=[],
            personalization_score=0.0,
            token_estimate=0
        ).model_dump_json()


# ========== Tool 5: Review and Score ==========

def check_quality_criteria(
    content: str,
    content_type: str,
    restrictions: Optional[ContentRestriction] = None
) -> Dict[str, Any]:
    """
    Check quality criteria based on content type and optional restrictions.

    Args:
        content: Generated proposal/email text
        content_type: Type of content (upwork_proposal, outreach_email, etc.)
        restrictions: Optional ContentRestriction for custom validation

    Returns:
        Dict with quality checks (True = passed, False = failed)
    """
    checks = {
        "has_specific_metrics": bool(re.search(r'\d+%', content)),
        "has_project_reference": bool(re.search(r'(project|case study|client|work)', content, re.IGNORECASE)),
        "proper_length": False,
        "has_call_to_action": bool(re.search(r'(schedule|discuss|connect|reach out|meeting)', content, re.IGNORECASE)),
        "professional_tone": not bool(re.search(r'(very|really|super|awesome|amazing)', content, re.IGNORECASE))
    }

    word_count = len(content.split())

    # Check word count (use custom range if restrictions provided)
    if restrictions:
        min_words, max_words = get_word_count_range(content_type, restrictions)
        checks["proper_length"] = min_words <= word_count <= max_words

        # Add restriction-specific checks
        forbidden_found = check_forbidden_phrases(content, restrictions)
        checks["no_forbidden_phrases"] = len(forbidden_found) == 0

        required_missing = check_required_elements(content, restrictions)
        checks["has_required_elements"] = len(required_missing) == 0
    else:
        # Default word count ranges
        if content_type == "upwork_proposal":
            checks["proper_length"] = 150 <= word_count <= 300
        elif content_type == "outreach_email":
            checks["proper_length"] = 100 <= word_count <= 200

    return checks


def calculate_quality_score(criteria_results: Dict[str, bool]) -> float:
    """
    Calculate quality score from criteria results.

    Args:
        criteria_results: Dict of check results (True = passed, False = failed)

    Returns:
        Quality score from 1.0 to 10.0
    """
    weights = {
        "has_specific_metrics": 0.4,
        "has_project_reference": 0.3,
        "proper_length": 0.1,
        "has_call_to_action": 0.1,
        "professional_tone": 0.1,
        # Restriction checks (if present)
        "no_forbidden_phrases": 0.3,  # Critical check
        "has_required_elements": 0.2  # Important check
    }

    score = 0.0
    for criterion, passed in criteria_results.items():
        if passed:
            score += weights.get(criterion, 0.0) * 10

    return min(max(score, 1.0), 10.0)


async def review_and_score(
    ctx: RunContext[AgentDeps],
    content: str,
    content_type: Literal["upwork_proposal", "outreach_email", "rfp_response"]
) -> str:
    """
    Quality check with actionable feedback. Auto-revises if score <8.

    Args:
        ctx: Context with LLM client
        content: Generated content to review
        content_type: Type of content being reviewed

    Returns:
        JSON string with ContentReview schema
    """
    try:
        criteria = check_quality_criteria(content, content_type)
        quality_score = calculate_quality_score(criteria)

        passed_checks = [check for check, passed in criteria.items() if passed]
        failed_checks = [check for check, passed in criteria.items() if not passed]

        specific_issues = []
        suggestions = []

        if not criteria["has_specific_metrics"]:
            specific_issues.append(Issue(
                category="Missing Metrics",
                description="No specific quantifiable results mentioned",
                suggestion="Add metrics like '90% error reduction' or '$1.2M cost savings'",
                severity="high"
            ))

        if not criteria["has_project_reference"]:
            specific_issues.append(Issue(
                category="Generic Content",
                description="No specific project or case study referenced",
                suggestion="Mention a relevant client project by name",
                severity="high"
            ))

        if not criteria["proper_length"]:
            word_count = len(content.split())
            target = "150-300 words" if content_type == "upwork_proposal" else "100-200 words"
            specific_issues.append(Issue(
                category="Length Issue",
                description=f"Content is {word_count} words, target is {target}",
                suggestion=f"Adjust content length to {target}",
                severity="medium"
            ))

        if quality_score < 8.0:
            suggestions.append("Add at least 2 specific metrics from case studies")
            suggestions.append("Reference company-specific context if available")
            suggestions.append("Ensure professional tone throughout")

        revised_content = None
        if quality_score < 8.0:
            suggestions.append("Content needs revision to meet 8/10 quality threshold")

        return ContentReview(
            quality_score=quality_score,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            specific_issues=specific_issues,
            suggestions=suggestions,
            revised_content=revised_content
        ).model_dump_json()

    except Exception as e:
        print(f"Error in review_and_score: {e}")
        return ContentReview(
            quality_score=5.0,
            passed_checks=[],
            failed_checks=[],
            specific_issues=[],
            suggestions=["Error during review"],
            revised_content=None
        ).model_dump_json()
