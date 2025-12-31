from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import AsyncOpenAI
from httpx import AsyncClient
from supabase import Client
from pathlib import Path
from typing import List, Literal, Optional
import os

from prompt import AGENT_SYSTEM_PROMPT
from tools import (
    web_search_tool,
    image_analysis_tool,
    retrieve_relevant_documents_tool,
    list_documents_tool,
    get_document_content_tool,
    execute_sql_query_tool,
    execute_safe_code_tool
)
from proposal_tools import (
    research_company as research_company_tool,
    search_relevant_projects as search_relevant_projects_tool,
    get_project_details as get_project_details_tool,
    generate_content as generate_content_tool,
    review_and_score as review_and_score_tool
)
from template_schemas import UserPreferences

# Load environment variables from what we have set for our agent
project_root = Path(__file__).resolve().parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path, override=True)

# ========== Helper function to get model configuration ==========
def get_model():
    llm = os.getenv('LLM_CHOICE') or 'gpt-4o-mini'
    base_url = os.getenv('LLM_BASE_URL') or 'https://api.openai.com/v1'
    api_key = os.getenv('LLM_API_KEY') or 'ollama'

    return OpenAIModel(llm, base_url=base_url, api_key=api_key)

# ========== Pydantic AI Agent ==========
@dataclass
class AgentDeps:
    supabase: Client
    embedding_client: AsyncOpenAI
    http_client: AsyncClient
    brave_api_key: str | None
    searxng_base_url: str | None
    memories: str
    user_id: str = "default_user"
    user_preferences: Optional[UserPreferences] = None

# To use the code execution MCP server:
# First uncomment the line below that defines 'code_execution_server', then also uncomment 'mcp_servers=[code_execution_server]'
# Start this in a separate terminal with this command after installing Deno:
# deno run -N -R=node_modules -W=node_modules --node-modules-dir=auto jsr:@pydantic/mcp-run-python sse
# Instructions for installing Deno here: https://github.com/denoland/deno/
# Pydantic AI docs for this MCP server: https://ai.pydantic.dev/mcp/run-python/
# code_execution_server = MCPServerHTTP(url='http://localhost:3001/sse')  

agent = Agent(
    get_model(),
    system_prompt=AGENT_SYSTEM_PROMPT,
    deps_type=AgentDeps,
    retries=2,
    # mcp_servers=[code_execution_server]
)

@agent.system_prompt  
def add_memories(ctx: RunContext[str]) -> str:
    return f"\nUser Memories:\n{ctx.deps.memories}"

@agent.tool
async def web_search(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the web with a specific query and get a summary of the top search results.
    
    Args:
        ctx: The context for the agent including the HTTP client and optional Brave API key/SearXNG base url
        query: The query for the web search
        
    Returns:
        A summary of the web search.
        For Brave, this is a single paragraph.
        For SearXNG, this is a list of the top search results including the most relevant snippet from the page.
    """
    print("Calling web_search tool")
    return await web_search_tool(query, ctx.deps.http_client, ctx.deps.brave_api_key, ctx.deps.searxng_base_url)    

@agent.tool
async def retrieve_relevant_documents(ctx: RunContext[AgentDeps], user_query: str) -> str:
    """
    Retrieve relevant document chunks based on the query with RAG.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        user_query: The user's question or query
        
    Returns:
        A formatted string containing the top 4 most relevant documents chunks
    """
    print("Calling retrieve_relevant_documents tool")
    return await retrieve_relevant_documents_tool(ctx.deps.supabase, ctx.deps.embedding_client, user_query)

@agent.tool
async def list_documents(ctx: RunContext[AgentDeps]) -> List[str]:
    """
    Retrieve a list of all available documents.
    
    Returns:
        List[str]: List of documents including their metadata (URL/path, schema if applicable, etc.)
    """
    print("Calling list_documents tool")
    return await list_documents_tool(ctx.deps.supabase)

@agent.tool
async def get_document_content(ctx: RunContext[AgentDeps], document_id: str) -> str:
    """
    Retrieve the full content of a specific document by combining all its chunks.
    
    Args:
        ctx: The context including the Supabase client
        document_id: The ID (or file path) of the document to retrieve
        
    Returns:
        str: The full content of the document with all chunks combined in order
    """
    print("Calling get_document_content tool")
    return await get_document_content_tool(ctx.deps.supabase, document_id)

@agent.tool
async def execute_sql_query(ctx: RunContext[AgentDeps], sql_query: str) -> str:
    """
    Run a SQL query - use this to query from the document_rows table once you know the file ID you are querying. 
    dataset_id is the file_id and you are always using the row_data for filtering, which is a jsonb field that has 
    all the keys from the file schema given in the document_metadata table.

    Never use a placeholder file ID. Always use the list_documents tool first to get the file ID.

    Example query:

    SELECT AVG((row_data->>'revenue')::numeric)
    FROM document_rows
    WHERE dataset_id = '123';

    Example query 2:

    SELECT 
        row_data->>'category' as category,
        SUM((row_data->>'sales')::numeric) as total_sales
    FROM document_rows
    WHERE dataset_id = '123'
    GROUP BY row_data->>'category';
    
    Args:
        ctx: The context including the Supabase client
        sql_query: The SQL query to execute (must be read-only)
        
    Returns:
        str: The results of the SQL query in JSON format
    """
    print(f"Calling execute_sql_query tool with SQL: {sql_query }")
    return await execute_sql_query_tool(ctx.deps.supabase, sql_query)    

@agent.tool
async def image_analysis(ctx: RunContext[AgentDeps], document_id: str, query: str) -> str:
    """
    Analyzes an image based on the document ID of the image provided.
    This function pulls the binary of the image from the knowledge base
    and passes that into a subagent with a vision LLM
    Before calling this tool, call list_documents to see the images available
    and to get the exact document ID for the image.
    
    Args:
        ctx: The context including the Supabase client
        document_id: The ID (or file path) of the image to analyze
        query: What to extract from the image analysis
        
    Returns:
        str: An analysis of the image based on the query
    """
    print("Calling image_analysis tool")
    return await image_analysis_tool(ctx.deps.supabase, document_id, query)    

# Using the MCP server instead for code execution, but you can use this simple version
# if you don't want to use MCP for whatever reason! Just uncomment the line below:
@agent.tool
async def execute_code(ctx: RunContext[AgentDeps], code: str) -> str:
    """
    Executes a given Python code string in a protected environment.
    Use print to output anything that you need as a result of executing the code.

    Args:
        code: Python code to execute

    Returns:
        str: Anything printed out to standard output with the print command
    """
    print(f"executing code: {code}")
    print(f"Result is: {execute_safe_code_tool(code)}")
    return execute_safe_code_tool(code)

# ========== Proposal Writer Tools ==========

@agent.tool
async def research_company(
    ctx: RunContext[AgentDeps],
    company_name: str,
    response_format: Literal["concise", "detailed"] = "concise"
) -> str:
    """
    Research target company using Brave Search API to gather intelligence.

    Use this when you have a company name to research their industry, tech stack,
    recent news, and business context. This provides personalization for proposals.

    Args:
        ctx: Context with HTTP client and Brave API key
        company_name: Name of the company to research (e.g., "Acme Corp")
        response_format: "concise" (top 3 sources, faster) or "detailed" (top 10 sources, comprehensive)

    Returns:
        JSON string with CompanyResearch schema containing:
        - company_name, industry, business_description
        - size_estimate (startup/SMB/enterprise)
        - tech_stack, recent_developments, pain_points
        - sources (URLs)

    Example:
        Use when job posting mentions a company: "Looking for help with our Shopify store at Acme Corp"
    """
    print(f"Calling research_company tool for: {company_name}")
    return await research_company_tool(ctx, company_name, response_format)

@agent.tool
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
    Search Brainforge's case studies with advanced metadata filters.

    Use this to find relevant past projects that match the job requirements.
    Filter by technologies, industry, or project type for better matches.

    Args:
        ctx: Context with Supabase and embedding clients
        query: Search query describing what you're looking for (e.g., "AI workflow automation")
        tech_filter: List of technologies to filter by (e.g., ["Python", "React"])
        industry: Filter by industry (e.g., "E-commerce", "Healthcare")
        project_type: Filter by type (e.g., "AI_ML", "BI_Analytics", "Workflow_Automation")
        max_results: Maximum number of projects to return (default 5)
        mode: "concise" (just metadata) or "detailed" (includes summary)

    Returns:
        JSON string with ProjectSearchResults schema containing:
        - matches: List of ProjectMatch objects with relevance scores
        - total_found: Total matches before truncation
        - search_query, filters_applied

    Example:
        search_relevant_projects(ctx, "e-commerce analytics dashboard", tech_filter=["Tableau", "Python"])
    """
    print(f"Calling search_relevant_projects tool with query: {query}")
    return await search_relevant_projects_tool(
        ctx=ctx,
        query=query,
        tech_filter=tech_filter,
        industry=industry,
        project_type=project_type,
        section=None,  # Section filter not exposed in agent tool
        max_results=max_results,
        mode=mode
    )

@agent.tool
async def get_project_details(
    ctx: RunContext[AgentDeps],
    project_id: str,
    sections: List[str] = ["context", "challenge", "solution", "results"]
) -> str:
    """
    Retrieve full case study content for a specific project.

    Use this after search_relevant_projects to get detailed information about
    the top matching projects. This provides the specific metrics and context
    needed for personalized proposals.

    CRITICAL: Use the **Project ID** field from search results, NOT the project name.

    Args:
        ctx: Context with Supabase client
        project_id: The **Project ID** value from search_relevant_projects results
                   Example: "eden_data_operating_system.md" NOT "Eden Data Operating System"
        sections: Which sections to retrieve (default: all main sections)
                 Options: "context", "challenge", "solution", "results", "testimonial"

    Returns:
        JSON string with ProjectDetails schema containing:
        - project_name, client_name
        - context, challenge, solution (optional based on sections param)
        - results (metrics dict + outcomes list)
        - testimonial, tools_used, team

    Example:
        From search results showing:
        # Eden Data Operating System
        **Project ID:** eden_data_operating_system.md

        Call: get_project_details(ctx, "eden_data_operating_system.md")
    """
    print(f"Calling get_project_details tool for project: {project_id}")
    return await get_project_details_tool(ctx, project_id, sections)

@agent.tool
async def generate_content(
    ctx: RunContext[AgentDeps],
    content_type: Literal["upwork_proposal", "catalant_proposal", "outreach_email", "rfp_response"],
    company_research_json: str,
    relevant_projects_text: str,
    user_context: str,
    word_limit: Optional[int] = None
) -> str:
    """
    Generate personalized proposal or outreach email with specific examples.

    **IMPORTANT:** Pass the EXACT TEXT from search_relevant_projects tool directly.
    Do NOT try to parse, modify, or reconstruct it as JSON.

    Use this after gathering company research and relevant projects to create
    the final content. This combines all context into a compelling narrative.

    Args:
        ctx: Context with LLM client
        content_type: Type of content to generate:
                     - "upwork_proposal": 1500 character proposal for Upwork job posting
                     - "catalant_proposal": 500-800 word formal consulting proposal
                     - "outreach_email": 100-200 word cold outreach
                     - "rfp_response": Formal RFP response
        company_research_json: JSON from research_company tool (can be empty string if no company)
        relevant_projects_text: FORMATTED TEXT from search_relevant_projects tool (pass as-is!)
        user_context: The job posting or outreach context from user
        word_limit: Optional word count constraint (overrides defaults)

    Returns:
        JSON string with GeneratedContent schema containing:
        - content: The generated text
        - structure: Breakdown of sections
        - word_count, projects_referenced
        - personalization_score (0.0-1.0)
        - token_estimate

    Example workflow:
        1. research_company() → company_json
        2. search_relevant_projects() → projects_text (formatted text)
        3. generate_content(ctx, "upwork_proposal", company_json, projects_text, job_posting)
    """
    print(f"Calling generate_content tool for content_type: {content_type}")
    return await generate_content_tool(ctx, content_type, company_research_json, relevant_projects_text, user_context, word_limit)

@agent.tool
async def review_and_score(
    ctx: RunContext[AgentDeps],
    content: str,
    content_type: Literal["upwork_proposal", "outreach_email", "rfp_response"]
) -> str:
    """
    Quality assurance check with actionable feedback and scoring.

    ALWAYS use this after generate_content to ensure quality standards.
    If score <8/10, you MUST iterate and regenerate with improvements.

    Args:
        ctx: Context with LLM client
        content: The generated content to review (from generate_content)
        content_type: Type of content being reviewed

    Returns:
        JSON string with ContentReview schema containing:
        - quality_score: 1.0-10.0 (must be ≥8.0 to pass)
        - passed_checks, failed_checks: Lists of criteria met/not met
        - specific_issues: List of Issue objects with severity
        - suggestions: List of improvement recommendations
        - revised_content: Auto-revised version if score <8

    Quality criteria checked:
        - has_specific_metrics (40% weight)
        - has_project_reference (30% weight)
        - proper_length (10% weight)
        - has_call_to_action (10% weight)
        - professional_tone (10% weight)

    Example:
        review_and_score(ctx, generated_proposal, "upwork_proposal")
        If quality_score < 8.0, use suggestions to regenerate
    """
    print(f"Calling review_and_score tool for content_type: {content_type}")
    return await review_and_score_tool(ctx, content, content_type)