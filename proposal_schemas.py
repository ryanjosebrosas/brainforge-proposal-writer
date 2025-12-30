"""
Pydantic schemas for the Brainforge Proposal Writer MVP.

This module defines 7 core data models used across the proposal generation workflow:
- CompanyResearch: Company intelligence from web search
- ProjectMatch & ProjectSearchResults: RAG search results
- ProjectDetails: Full case study content
- GeneratedContent: Proposal/email drafts
- Issue & ContentReview: Quality assurance feedback
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any


# ========== Constants ==========

COMMON_INDUSTRIES = [
    "SaaS", "E-commerce", "Healthcare", "Finance", "Education",
    "Manufacturing", "Retail", "Technology", "Home Services",
    "Logistics", "Media", "Real Estate", "Consulting"
]

COMMON_TECHNOLOGIES = [
    "Python", "JavaScript", "TypeScript", "React", "Next.js", "Node.js",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
    "AWS", "Azure", "GCP", "Snowflake", "dbt", "Tableau", "PowerBI",
    "Airflow", "Spark", "TensorFlow", "PyTorch", "FastAPI", "Django",
    "n8n", "Zapier", "Salesforce", "HubSpot", "Shopify", "Stripe"
]

PROJECT_TYPES = [
    "AI_ML", "BI_Analytics", "Workflow_Automation", "Data_Engineering",
    "Web_Development", "Mobile_App", "API_Integration", "Cloud_Migration",
    "Database_Optimization", "ETL_Pipeline", "Dashboard", "Chatbot",
    "Process_Automation", "System_Integration", "Data_Migration"
]


# ========== Core Schemas ==========

class CompanyResearch(BaseModel):
    """Company intelligence from Brave Search API."""

    company_name: str = Field(..., description="Official company name")
    industry: str = Field(..., description="Primary industry/sector")
    business_description: str = Field(..., description="What the company does (1-2 sentences)")
    size_estimate: Literal["startup", "SMB", "enterprise"] = Field(..., description="Company size category")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies mentioned in search results")
    recent_developments: List[str] = Field(default_factory=list, description="Recent news, funding, product launches")
    pain_points: List[str] = Field(default_factory=list, description="Inferred challenges or needs")
    key_people: List[str] = Field(default_factory=list, description="Executives, founders mentioned")
    sources: List[str] = Field(default_factory=list, description="URLs used for research")


class ProjectMatch(BaseModel):
    """Individual project match from RAG search."""

    project_id: str = Field(..., description="Unique file_id from Supabase")
    project_name: str = Field(..., description="Project title from metadata")
    project_type: str = Field(..., description="Category (AI_ML, BI_Analytics, etc.)")
    industry: str = Field(..., description="Client industry")
    technologies_used: List[str] = Field(default_factory=list, description="Tech stack from metadata")
    key_metric: str = Field("", description="Most impressive metric (e.g., '90% error reduction')")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score from vector search")
    summary: Optional[str] = Field(None, description="Brief project description (detailed mode only)")


class ProjectSearchResults(BaseModel):
    """Collection of project matches from RAG search."""

    matches: List[ProjectMatch] = Field(default_factory=list, description="Ranked project matches")
    total_found: int = Field(..., description="Total number of matches before truncation")
    search_query: str = Field(..., description="Original search query used")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Tech/industry filters used")


class Results(BaseModel):
    """Nested model for project results/metrics."""

    metrics: Dict[str, Any] = Field(default_factory=dict, description="Quantifiable outcomes (e.g., {'error_reduction': 90})")
    outcomes: List[str] = Field(default_factory=list, description="Business impact statements")


class ProjectDetails(BaseModel):
    """Full case study content with selective sections."""

    project_name: str = Field(..., description="Project title")
    client_name: str = Field(..., description="Client organization")
    context: Optional[str] = Field(None, description="Background/situation section")
    challenge: Optional[str] = Field(None, description="Problem statement section")
    solution: Optional[str] = Field(None, description="Approach/implementation section")
    results: Optional[Results] = Field(None, description="Outcomes and metrics")
    testimonial: Optional[str] = Field(None, description="Client quote if available")
    tools_used: List[str] = Field(default_factory=list, description="Technologies and tools")
    team: List[str] = Field(default_factory=list, description="Team members involved")


class GeneratedContent(BaseModel):
    """Generated proposal or outreach email."""

    content: str = Field(..., description="Full text of generated proposal/email")
    structure: Dict[str, str] = Field(default_factory=dict, description="Sections breakdown (e.g., {'opening': '...', 'body': '...'})")
    word_count: int = Field(..., description="Total word count")
    projects_referenced: List[str] = Field(default_factory=list, description="Project IDs mentioned in content")
    personalization_score: float = Field(..., ge=0.0, le=1.0, description="How personalized to company (0=generic, 1=highly specific)")
    token_estimate: int = Field(..., description="Estimated tokens for LLM consumption")


class Issue(BaseModel):
    """Individual quality issue found during review."""

    category: str = Field(..., description="Issue type (e.g., 'Missing metrics', 'Generic language')")
    description: str = Field(..., description="Specific problem identified")
    suggestion: str = Field(..., description="How to fix the issue")
    severity: Literal["low", "medium", "high"] = Field(..., description="Impact level")


class ContentReview(BaseModel):
    """Quality assurance results with actionable feedback."""

    quality_score: float = Field(..., ge=1.0, le=10.0, description="Overall quality score (1-10)")
    passed_checks: List[str] = Field(default_factory=list, description="Quality criteria met")
    failed_checks: List[str] = Field(default_factory=list, description="Quality criteria not met")
    specific_issues: List[Issue] = Field(default_factory=list, description="Detailed problems found")
    suggestions: List[str] = Field(default_factory=list, description="General improvement recommendations")
    revised_content: Optional[str] = Field(None, description="Auto-revised version if score <8")
