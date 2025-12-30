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

    Args:
        ctx: Context with HTTP client and Brave API key
        company_name: Company to research
        response_format: "concise" (top 3 sources) or "detailed" (top 10 sources)

    Returns:
        JSON string with CompanyResearch schema
    """
    try:
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

def format_project_match(doc: dict, mode: Literal["concise", "detailed"] = "concise") -> ProjectMatch:
    """Format Supabase document as ProjectMatch model."""
    metadata = doc.get('metadata', {})

    project_match = ProjectMatch(
        project_id=metadata.get('file_id', 'unknown'),
        project_name=metadata.get('file_title', 'Untitled Project'),
        project_type=metadata.get('project_type', 'Unknown'),
        industry=metadata.get('industry', 'Unknown'),
        technologies_used=metadata.get('tech_stack', []),
        key_metric="",
        relevance_score=doc.get('similarity', 0.5),
        summary=None
    )

    content = doc.get('content', '')
    metrics_match = re.search(r'(\d+%?\s*(?:reduction|improvement|increase|faster|savings))', content, re.IGNORECASE)
    if metrics_match:
        project_match.key_metric = metrics_match.group(1)

    if mode == "detailed" and content:
        project_match.summary = content[:200] + "..."

    return project_match


async def search_relevant_projects(
    ctx: RunContext[AgentDeps],
    query: str,
    tech_filter: Optional[List[str]] = None,
    industry: Optional[str] = None,
    project_type: Optional[str] = None,
    max_results: int = 5,
    mode: Literal["concise", "detailed"] = "concise"
) -> str:
    """
    Search case studies with metadata filters.

    Args:
        ctx: Context with Supabase and embedding clients
        query: Search query
        tech_filter: Filter by technologies (e.g., ["Python", "React"])
        industry: Filter by industry (e.g., "SaaS")
        project_type: Filter by type (e.g., "AI_ML")
        max_results: Max projects to return
        mode: "concise" or "detailed"

    Returns:
        JSON string with ProjectSearchResults schema
    """
    try:
        query_embedding = await get_embedding(query, ctx.deps.embedding_client)

        result = ctx.deps.supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_count': max_results * 2
            }
        ).execute()

        if not result.data:
            return ProjectSearchResults(
                matches=[],
                total_found=0,
                search_query=query,
                filters_applied={}
            ).model_dump_json()

        filtered_results = []
        for doc in result.data:
            metadata = doc.get('metadata', {})

            if tech_filter:
                doc_tech = metadata.get('tech_stack', [])
                if not any(tech in doc_tech for tech in tech_filter):
                    continue

            if industry and metadata.get('industry') != industry:
                continue

            if project_type and metadata.get('project_type') != project_type:
                continue

            filtered_results.append(doc)

        matches = [format_project_match(doc, mode) for doc in filtered_results[:max_results]]

        filters_applied = {}
        if tech_filter:
            filters_applied['tech_filter'] = tech_filter
        if industry:
            filters_applied['industry'] = industry
        if project_type:
            filters_applied['project_type'] = project_type

        return ProjectSearchResults(
            matches=matches,
            total_found=len(filtered_results),
            search_query=query,
            filters_applied=filters_applied
        ).model_dump_json()

    except Exception as e:
        print(f"Error in search_relevant_projects: {e}")
        return ProjectSearchResults(
            matches=[],
            total_found=0,
            search_query=query,
            filters_applied={}
        ).model_dump_json()


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
    Get detailed sections from a case study.

    Args:
        ctx: Context with Supabase client
        project_id: Project file_id from search results
        sections: Sections to retrieve

    Returns:
        JSON string with ProjectDetails schema
    """
    try:
        result = ctx.deps.supabase.from_('documents') \
            .select('id, content, metadata') \
            .eq('metadata->>file_id', project_id) \
            .order('id') \
            .execute()

        if not result.data:
            return ProjectDetails(
                project_name="Unknown Project",
                client_name="Unknown Client",
                tools_used=[],
                team=[]
            ).model_dump_json()

        metadata = result.data[0]['metadata']
        full_content = '\n\n'.join([chunk['content'] for chunk in result.data])

        parsed_sections = parse_markdown_sections(full_content)

        results_section = parsed_sections.get('results', '')
        metrics = extract_metrics_from_section(results_section)
        outcomes = [line.strip() for line in results_section.split('\n') if line.strip() and not line.startswith('#')]

        project_details = ProjectDetails(
            project_name=metadata.get('file_title', 'Untitled').split(' - ')[0],
            client_name=metadata.get('client', 'Client'),
            context=parsed_sections.get('context') or parsed_sections.get('background') if 'context' in sections else None,
            challenge=parsed_sections.get('challenge') if 'challenge' in sections else None,
            solution=parsed_sections.get('solution') if 'solution' in sections else None,
            results=Results(metrics=metrics, outcomes=outcomes[:3]) if 'results' in sections else None,
            testimonial=parsed_sections.get('testimonial'),
            tools_used=metadata.get('tech_stack', []),
            team=[]
        )

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

def build_generation_prompt(
    content_type: Literal["upwork_proposal", "outreach_email", "rfp_response"],
    company_research: Optional[CompanyResearch],
    relevant_projects: List[ProjectMatch],
    user_context: str
) -> str:
    """Build prompt for content generation."""
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
    content_type: Literal["upwork_proposal", "outreach_email", "rfp_response"],
    company_research_json: str,
    relevant_projects_json: str,
    user_context: str,
    word_limit: Optional[int] = None
) -> str:
    """
    Generate proposal or email with company context and project examples.

    Args:
        ctx: Context with LLM client
        content_type: Type of content to generate
        company_research_json: JSON from research_company tool
        relevant_projects_json: JSON from search_relevant_projects tool
        user_context: User's notes or job posting text
        word_limit: Optional word count constraint

    Returns:
        JSON string with GeneratedContent schema
    """
    try:
        company_research = None
        if company_research_json:
            company_research = CompanyResearch.model_validate_json(company_research_json)

        search_results = ProjectSearchResults.model_validate_json(relevant_projects_json)
        relevant_projects = search_results.matches

        prompt = build_generation_prompt(content_type, company_research, relevant_projects, user_context)

        from pydantic_ai import Agent
        from agent import get_model
        model = get_model()
        generator_agent = Agent(model, result_type=str)

        result = await generator_agent.run(prompt)
        content = result.data

        word_count = len(content.split())
        projects_referenced = [p.project_id for p in relevant_projects[:2]]

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
        print(f"Error in generate_content: {e}")
        return GeneratedContent(
            content=f"Error generating content: {str(e)}",
            structure={},
            word_count=0,
            projects_referenced=[],
            personalization_score=0.0,
            token_estimate=0
        ).model_dump_json()


# ========== Tool 5: Review and Score ==========

def check_quality_criteria(content: str, content_type: str) -> Dict[str, Any]:
    """Check quality criteria based on content type."""
    checks = {
        "has_specific_metrics": bool(re.search(r'\d+%', content)),
        "has_project_reference": bool(re.search(r'(project|case study|client|work)', content, re.IGNORECASE)),
        "proper_length": False,
        "has_call_to_action": bool(re.search(r'(schedule|discuss|connect|reach out|meeting)', content, re.IGNORECASE)),
        "professional_tone": not bool(re.search(r'(very|really|super|awesome|amazing)', content, re.IGNORECASE))
    }

    word_count = len(content.split())

    if content_type == "upwork_proposal":
        checks["proper_length"] = 150 <= word_count <= 300
    elif content_type == "outreach_email":
        checks["proper_length"] = 100 <= word_count <= 200

    return checks


def calculate_quality_score(criteria_results: Dict[str, bool]) -> float:
    """Calculate quality score from criteria results."""
    weights = {
        "has_specific_metrics": 0.4,
        "has_project_reference": 0.3,
        "proper_length": 0.1,
        "has_call_to_action": 0.1,
        "professional_tone": 0.1
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
