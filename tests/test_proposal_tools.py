"""
Unit tests for proposal writer tools.

Tests all 5 specialized proposal tools:
1. research_company
2. search_relevant_projects
3. get_project_details
4. generate_content
5. review_and_score
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import ValidationError

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock environment and dependencies before imports
os.environ.update({
    'LLM_PROVIDER': 'openai',
    'LLM_BASE_URL': 'https://api.openai.com/v1',
    'LLM_API_KEY': 'test-api-key',
    'LLM_CHOICE': 'gpt-4o-mini',
    'EMBEDDING_PROVIDER': 'openai',
    'EMBEDDING_BASE_URL': 'https://api.openai.com/v1',
    'EMBEDDING_API_KEY': 'test-api-key',
    'EMBEDDING_MODEL_CHOICE': 'text-embedding-3-small',
    'SUPABASE_URL': 'https://test-supabase-url.com',
    'SUPABASE_SERVICE_KEY': 'test-supabase-key',
    'BRAVE_API_KEY': 'test-brave-key'
})

# Import schemas first (no complex dependencies)
from proposal_schemas import (
    CompanyResearch,
    ProjectMatch,
    ProjectSearchResults,
    ProjectDetails,
    Results,
    GeneratedContent,
    Issue,
    ContentReview
)

# Import tool functions
from proposal_tools import (
    research_company,
    search_relevant_projects,
    get_project_details,
    generate_content,
    review_and_score,
    build_company_search_queries,
    execute_brave_search,
    parse_brave_results_to_company_research,
    format_project_match,
    parse_markdown_sections,
    extract_metrics_from_section,
    build_generation_prompt,
    check_quality_criteria,
    calculate_quality_score
)


# ========== Test Fixtures ==========

@pytest.fixture
def mock_context():
    """Mock RunContext with all dependencies."""
    ctx = MagicMock()
    ctx.deps = MagicMock()
    ctx.deps.http_client = AsyncMock()
    ctx.deps.brave_api_key = "test-brave-key"
    ctx.deps.supabase = MagicMock()
    ctx.deps.embedding_client = AsyncMock()
    return ctx


@pytest.fixture
def sample_brave_response():
    """Sample Brave API response."""
    return {
        "web": {
            "results": [
                {
                    "title": "Acme Corp - E-commerce Platform",
                    "description": "Acme Corp is a leading e-commerce startup using Python and React for their Shopify integration.",
                    "url": "https://acmecorp.com"
                },
                {
                    "title": "Acme Corp raises $10M Series A",
                    "description": "E-commerce startup Acme Corp announced $10M funding round to expand their AWS infrastructure.",
                    "url": "https://techcrunch.com/acme"
                },
                {
                    "title": "Acme Technology Stack",
                    "description": "Acme uses PostgreSQL, Docker, and Kubernetes for their cloud infrastructure.",
                    "url": "https://stackshare.io/acme"
                }
            ]
        }
    }


@pytest.fixture
def sample_project_data():
    """Sample project data from Supabase (NEW hybrid search schema)."""
    return [
        {
            "content": "Implemented BI dashboard with 90% error reduction",
            "chunk_metadata": {
                "file_id": "project-001",
                "file_title": "ABC Home Analytics Dashboard",
                "section": "Results"
            },
            "frontmatter": {
                "title": "ABC Home Analytics Dashboard",
                "client": "ABC Home",
                "industry": "E-commerce",
                "project_type": "BI_Analytics",
                "tech_stack": ["Snowflake", "dbt", "Tableau"]
            },
            "combined_score": 0.92,
            "vector_score": 0.90,
            "fts_score": 0.95
        },
        {
            "content": "Built automated reporting system saving $1.2M annually",
            "chunk_metadata": {
                "file_id": "project-002",
                "file_title": "Amazon Reporting Automation",
                "section": "Results"
            },
            "frontmatter": {
                "title": "Amazon Reporting Automation",
                "client": "Amazon",
                "industry": "E-commerce",
                "project_type": "Workflow_Automation",
                "tech_stack": ["Python", "AWS", "PostgreSQL"]
            },
            "combined_score": 0.85,
            "vector_score": 0.80,
            "fts_score": 0.90
        }
    ]


# ========== Test Tool 1: research_company ==========

class TestResearchCompany:
    """Tests for research_company tool."""

    def test_build_company_search_queries(self):
        """Test query generation for company research."""
        queries = build_company_search_queries("Acme Corp")

        assert len(queries) == 3
        assert "Acme Corp company" in queries
        assert "Acme Corp technology stack" in queries
        assert "Acme Corp recent news" in queries

    def test_build_company_search_queries_with_focus(self):
        """Test query generation with focus areas."""
        queries = build_company_search_queries(
            "Acme Corp",
            focus_areas=["challenges", "customers"]
        )

        assert len(queries) == 5
        assert "Acme Corp challenges" in queries
        assert "Acme Corp customers" in queries

    @pytest.mark.asyncio
    async def test_execute_brave_search_success(self):
        """Test successful Brave API call."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "title": "Test Title",
                        "description": "Test Description",
                        "url": "https://example.com"
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response

        result = await execute_brave_search("test query", mock_client, "test-key")

        mock_client.get.assert_called_once()
        assert result["web"]["results"][0]["title"] == "Test Title"

    def test_parse_brave_results_to_company_research(self, sample_brave_response):
        """Test parsing Brave results into CompanyResearch model."""
        results = [sample_brave_response, sample_brave_response]

        company_research = parse_brave_results_to_company_research(results, "Acme Corp")

        assert company_research.company_name == "Acme Corp"
        # Industry detection is based on keywords - can be SaaS or E-commerce
        assert company_research.industry in ["SaaS", "E-commerce", "Unknown"]
        assert "Python" in company_research.tech_stack
        assert "React" in company_research.tech_stack
        assert len(company_research.sources) > 0
        assert company_research.size_estimate in ["startup", "SMB", "enterprise"]

    @pytest.mark.asyncio
    async def test_research_company_concise(self, mock_context, sample_brave_response):
        """Test research_company with concise format."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = sample_brave_response
        mock_context.deps.http_client.get.return_value = mock_response

        result_json = await research_company(mock_context, "Acme Corp", "concise")
        result = CompanyResearch.model_validate_json(result_json)

        assert result.company_name == "Acme Corp"
        assert result.industry != "Unknown"
        assert len(result.tech_stack) > 0

    @pytest.mark.asyncio
    async def test_research_company_error_handling(self, mock_context):
        """Test research_company error handling."""
        mock_context.deps.http_client.get.side_effect = Exception("API Error")

        result_json = await research_company(mock_context, "Acme Corp")
        result = CompanyResearch.model_validate_json(result_json)

        assert result.company_name == "Acme Corp"
        assert "Unable to research" in result.business_description


# ========== Test Tool 2: search_relevant_projects ==========

class TestSearchRelevantProjects:
    """Tests for search_relevant_projects tool."""

    def test_format_project_match_concise(self, sample_project_data):
        """Test formatting project match in concise mode."""
        project = format_project_match(sample_project_data[0], mode="concise")

        assert project.project_id == "project-001"
        assert project.project_name == "ABC Home Analytics Dashboard"
        assert project.industry == "E-commerce"
        assert project.project_type == "BI_Analytics"
        assert "Snowflake" in project.technologies_used
        assert project.relevance_score == 0.92
        assert "90%" in project.key_metric or project.key_metric == ""
        assert project.summary is None

    def test_format_project_match_detailed(self, sample_project_data):
        """Test formatting project match in detailed mode."""
        project = format_project_match(sample_project_data[0], mode="detailed")

        assert project.summary is not None
        assert len(project.summary) <= 203

    @pytest.mark.asyncio
    async def test_search_relevant_projects_no_filters(
        self, mock_context, sample_project_data
    ):
        """Test search without filters."""
        # Mock embedding
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_context.deps.embedding_client.embeddings.create.return_value = mock_embedding_response

        # Mock Supabase RPC
        mock_rpc_result = MagicMock()
        mock_rpc_result.data = sample_project_data
        mock_context.deps.supabase.rpc.return_value.execute.return_value = mock_rpc_result

        result_json = await search_relevant_projects(
            mock_context,
            query="e-commerce analytics",
            max_results=5,
            mode="concise"
        )
        result = ProjectSearchResults.model_validate_json(result_json)

        assert result.total_found == 2
        assert len(result.matches) == 2
        assert result.search_query == "e-commerce analytics"

    @pytest.mark.asyncio
    async def test_search_relevant_projects_with_tech_filter(
        self, mock_context, sample_project_data
    ):
        """Test search with technology filter."""
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_context.deps.embedding_client.embeddings.create.return_value = mock_embedding_response

        # Mock RPC should only return projects matching the tech filter
        # Only project-001 has Snowflake and Tableau
        mock_rpc_result = MagicMock()
        mock_rpc_result.data = [sample_project_data[0]]  # Only first project matches filter
        mock_context.deps.supabase.rpc.return_value.execute.return_value = mock_rpc_result

        result_json = await search_relevant_projects(
            mock_context,
            query="analytics",
            tech_filter=["Snowflake", "Tableau"],
            max_results=5
        )
        result = ProjectSearchResults.model_validate_json(result_json)

        assert result.total_found == 1
        assert result.matches[0].project_id == "project-001"
        assert "tech_filter" in result.filters_applied

    @pytest.mark.asyncio
    async def test_search_relevant_projects_empty_results(self, mock_context):
        """Test search with no results."""
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_context.deps.embedding_client.embeddings.create.return_value = mock_embedding_response

        mock_rpc_result = MagicMock()
        mock_rpc_result.data = []
        mock_context.deps.supabase.rpc.return_value.execute.return_value = mock_rpc_result

        result_json = await search_relevant_projects(mock_context, query="xyz")
        result = ProjectSearchResults.model_validate_json(result_json)

        assert result.total_found == 0
        assert len(result.matches) == 0


# ========== Test Tool 3: get_project_details ==========

class TestGetProjectDetails:
    """Tests for get_project_details tool."""

    def test_parse_markdown_sections(self):
        """Test markdown section parsing."""
        markdown = """## Context
Some background information

## Challenge
The problem we faced

## Solution
How we solved it
"""
        sections = parse_markdown_sections(markdown)

        assert "context" in sections
        assert "challenge" in sections
        assert "solution" in sections
        assert "background" in sections["context"]

    def test_extract_metrics_from_section(self):
        """Test metrics extraction from text."""
        text = "We achieved a 90% reduction in errors and saved $1.2M annually"

        metrics = extract_metrics_from_section(text)

        assert "reduction_percent" in metrics
        assert metrics["reduction_percent"] == 90
        assert "cost_savings" in metrics
        assert metrics["cost_savings"] == 1_200_000

    @pytest.mark.asyncio
    async def test_get_project_details_success(self, mock_context):
        """Test successful project details retrieval (NEW normalized schema)."""
        mock_result = MagicMock()
        mock_result.data = [
            {
                "frontmatter": {
                    "title": "ABC Home Analytics Dashboard",
                    "client": "ABC Home",
                    "industry": "E-commerce",
                    "project_type": "BI_Analytics",
                    "tech_stack": ["Snowflake", "dbt", "Tableau"]
                },
                "chunks": [
                    {
                        "content": "We achieved 90% error reduction and saved $500K annually",
                        "section": "Results"
                    }
                ],
                "metrics": [
                    {"metric_name": "error_reduction", "value": 90}
                ]
            }
        ]
        # Mock RPC call for get_case_study_full
        mock_context.deps.supabase.rpc.return_value.execute.return_value = mock_result

        result_json = await get_project_details(
            mock_context,
            project_id="project-001",
            sections=["results"]
        )
        result = ProjectDetails.model_validate_json(result_json)

        assert result.project_name == "ABC Home Analytics Dashboard"
        assert result.client_name == "ABC Home"
        assert result.results is not None
        assert "error_reduction" in str(result.results.metrics) or len(result.results.outcomes) > 0

    @pytest.mark.asyncio
    async def test_get_project_details_not_found(self, mock_context):
        """Test project not found."""
        mock_result = MagicMock()
        mock_result.data = []
        # Mock RPC call for get_case_study_full (no data found)
        mock_context.deps.supabase.rpc.return_value.execute.return_value = mock_result

        result_json = await get_project_details(mock_context, "nonexistent")
        result = ProjectDetails.model_validate_json(result_json)

        assert result.project_name == "Unknown Project"
        assert result.client_name == "Unknown Client"


# ========== Test Tool 4: generate_content ==========

class TestGenerateContent:
    """Tests for generate_content tool."""

    def test_build_generation_prompt_upwork(self):
        """Test prompt building for Upwork proposal."""
        company = CompanyResearch(
            company_name="Acme Corp",
            industry="E-commerce",
            business_description="Leading e-commerce platform",
            size_estimate="startup",
            tech_stack=["Python", "React"],
            recent_developments=[],
            pain_points=[],
            key_people=[],
            sources=[]
        )

        projects = [
            ProjectMatch(
                project_id="p1",
                project_name="ABC Analytics",
                project_type="BI_Analytics",
                industry="E-commerce",
                technologies_used=["Tableau"],
                key_metric="90% reduction",
                relevance_score=0.9
            )
        ]

        prompt = build_generation_prompt(
            "upwork_proposal",
            company,
            projects,
            "Job posting text here"
        )

        assert "Acme Corp" in prompt
        assert "E-commerce" in prompt
        assert "Python" in prompt or "React" in prompt
        assert "ABC Analytics" in prompt
        assert "90% reduction" in prompt
        assert "150-300 words" in prompt

    @pytest.mark.asyncio
    async def test_generate_content_upwork_proposal(self, mock_context):
        """Test Upwork proposal generation."""
        company_json = CompanyResearch(
            company_name="Acme",
            industry="E-commerce",
            business_description="Test",
            size_estimate="startup",
            tech_stack=[],
            recent_developments=[],
            pain_points=[],
            key_people=[],
            sources=[]
        ).model_dump_json()

        projects_json = ProjectSearchResults(
            matches=[],
            total_found=0,
            search_query="test",
            filters_applied={}
        ).model_dump_json()

        # Mock the generator agent run - Agent is imported inside the function
        with patch('pydantic_ai.Agent') as MockAgent:
            mock_agent_instance = MagicMock()
            mock_result = MagicMock()
            mock_result.data = "This is a test proposal with specific metrics like 90% improvement."
            mock_agent_instance.run = AsyncMock(return_value=mock_result)
            MockAgent.return_value = mock_agent_instance

            result_json = await generate_content(
                mock_context,
                "upwork_proposal",
                company_json,
                projects_json,
                "Job posting here"
            )
            result = GeneratedContent.model_validate_json(result_json)

            assert result.content is not None
            assert result.word_count > 0
            assert 0.0 <= result.personalization_score <= 1.0


# ========== Test Tool 5: review_and_score ==========

class TestReviewAndScore:
    """Tests for review_and_score tool."""

    def test_check_quality_criteria_upwork_pass(self):
        """Test quality criteria for good Upwork proposal."""
        content = """We recently completed a similar project for ABC Corp where we achieved
        a 90% reduction in processing time using our automated workflow. Our team has
        extensive experience with Python and React. I'd love to schedule a call to
        discuss how we can help with your e-commerce platform."""

        # Make content proper length (150-300 words for proposals)
        content = content + " " + " ".join(["Additional content"] * 30)

        criteria = check_quality_criteria(content, "upwork_proposal")

        assert criteria["has_specific_metrics"] is True
        assert criteria["has_project_reference"] is True
        assert criteria["has_call_to_action"] is True

    def test_check_quality_criteria_upwork_fail(self):
        """Test quality criteria for poor proposal."""
        content = "We are very good at what we do. Really awesome team."

        criteria = check_quality_criteria(content, "upwork_proposal")

        assert criteria["has_specific_metrics"] is False
        assert criteria["professional_tone"] is False
        assert criteria["proper_length"] is False

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        # All criteria passed
        criteria_all_pass = {
            "has_specific_metrics": True,
            "has_project_reference": True,
            "proper_length": True,
            "has_call_to_action": True,
            "professional_tone": True
        }
        score = calculate_quality_score(criteria_all_pass)
        assert score == 10.0

        # Only metrics passed (40% weight)
        criteria_metrics_only = {
            "has_specific_metrics": True,
            "has_project_reference": False,
            "proper_length": False,
            "has_call_to_action": False,
            "professional_tone": False
        }
        score = calculate_quality_score(criteria_metrics_only)
        assert score == 4.0

    @pytest.mark.asyncio
    async def test_review_and_score_high_quality(self, mock_context):
        """Test review of high-quality content."""
        content = """Dear Hiring Manager,

I noticed your e-commerce project and wanted to share our relevant experience.
We recently completed a similar project for ABC Corp where we achieved a 90%
reduction in processing errors using Python and React. Our automated workflow
saved them $500K annually.

Our team has 5+ years of experience with Shopify integrations and can deliver
this project efficiently. I'd love to schedule a brief call to discuss your
specific requirements and share more details about our approach.

Looking forward to connecting!
""" + " ".join(["Additional relevant content about our expertise"] * 20)

        result_json = await review_and_score(mock_context, content, "upwork_proposal")
        result = ContentReview.model_validate_json(result_json)

        assert result.quality_score >= 8.0
        assert len(result.passed_checks) >= 3
        assert result.revised_content is None

    @pytest.mark.asyncio
    async def test_review_and_score_low_quality(self, mock_context):
        """Test review of low-quality content."""
        content = "We are very experienced and can do great work for you."

        result_json = await review_and_score(mock_context, content, "upwork_proposal")
        result = ContentReview.model_validate_json(result_json)

        assert result.quality_score < 8.0
        assert len(result.failed_checks) > 0
        assert len(result.specific_issues) > 0


# ========== Integration Tests ==========

class TestProposalToolsIntegration:
    """Integration tests for complete workflow."""

    @pytest.mark.asyncio
    async def test_complete_proposal_workflow(self, mock_context, sample_brave_response, sample_project_data):
        """Test complete proposal generation workflow."""
        # Step 1: Research company
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = sample_brave_response
        mock_context.deps.http_client.get.return_value = mock_response

        company_json = await research_company(mock_context, "Acme Corp", "concise")
        company = CompanyResearch.model_validate_json(company_json)
        assert company.company_name == "Acme Corp"

        # Step 2: Search projects
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_context.deps.embedding_client.embeddings.create.return_value = mock_embedding_response

        mock_rpc_result = MagicMock()
        mock_rpc_result.data = sample_project_data
        mock_context.deps.supabase.rpc.return_value.execute.return_value = mock_rpc_result

        projects_json = await search_relevant_projects(
            mock_context,
            query="e-commerce analytics",
            max_results=5
        )
        projects = ProjectSearchResults.model_validate_json(projects_json)
        assert len(projects.matches) > 0

        # Step 3: Generate content
        with patch('pydantic_ai.Agent') as MockAgent:
            mock_agent_instance = MagicMock()
            mock_result = MagicMock()
            mock_result.data = "Complete proposal with 90% metrics and project references to ABC Corp." + " " * 200
            mock_agent_instance.run = AsyncMock(return_value=mock_result)
            MockAgent.return_value = mock_agent_instance

            content_json = await generate_content(
                mock_context,
                "upwork_proposal",
                company_json,
                projects_json,
                "Job posting"
            )
            content = GeneratedContent.model_validate_json(content_json)
            assert content.word_count > 0

        # Step 4: Review and score
        review_json = await review_and_score(
            mock_context,
            content.content,
            "upwork_proposal"
        )
        review = ContentReview.model_validate_json(review_json)
        assert 1.0 <= review.quality_score <= 10.0
