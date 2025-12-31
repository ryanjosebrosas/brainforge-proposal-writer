"""
Streamlit UI for Brainforge Proposal Writer MVP.

Dual-mode interface for generating:
1. Upwork Proposals (400-600 words)
2. Outreach Emails (100-200 words)
"""

from httpx import AsyncClient
import streamlit as st
import asyncio
import os
import json

from agent import agent, AgentDeps
from clients import get_agent_clients
from proposal_schemas import (
    CompanyResearch,
    ProjectSearchResults,
    GeneratedContent,
    ContentReview
)

# Page configuration
st.set_page_config(
    page_title="Brainforge Proposal Writer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .quality-score-high {
        color: #28a745;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .quality-score-medium {
        color: #ffc107;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .quality-score-low {
        color: #dc3545;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_agent_deps_cached():
    """Cache agent dependencies."""
    return get_agent_clients()


async def run_proposal_workflow(content_type, user_input, deck_type="data"):
    """
    Run the complete proposal generation workflow.

    Returns: dict with research, projects, content, and review data
    """
    embedding_client, supabase, user_preferences = get_agent_deps_cached()

    async with AsyncClient() as http_client:
        agent_deps = AgentDeps(
            embedding_client=embedding_client,
            supabase=supabase,
            http_client=http_client,
            brave_api_key=os.getenv("BRAVE_API_KEY", ""),
            searxng_base_url=os.getenv("SEARXNG_BASE_URL", ""),
            memories="",
            user_id="default_user",
            user_preferences=user_preferences
        )

        # Deck query and name based on user selection
        deck_query = "AI capabilities overview" if deck_type == "ai" else "data analytics capabilities"
        deck_name = "Brainforge AI Capabilities Deck" if deck_type == "ai" else "Brainforge Data Capabilities Deck"

        # Run agent with the workflow prompt
        if content_type == "upwork_proposal":
            prompt = f"""Generate an Upwork proposal for this job posting:

{user_input}

DECK TO USE: {deck_name} (user selected - search for "{deck_query}" to get full deck content)

Follow the complete workflow:
1. Check if a SPECIFIC company name OR website URL is mentioned
   - If company URL (starts with http:// or https://): call research_company with the COMPLETE URL unchanged
   - If company name only (like "Acme Corp" or "Amazon"): call research_company with the company name
   - If neither: skip research_company
   - CRITICAL: If you see a URL, DO NOT extract the company name - pass the ENTIRE URL

2. FETCH SELECTED DECK CONTENT:
   - Call search_relevant_projects for: "{deck_query}" (mode="detailed")
   - This gets the full {deck_name} content from Supabase
   - Use this content to show Brainforge's capabilities

3. TWO-SWEEP CASE STUDY SEARCH (YOU MUST DO BOTH SWEEPS):

   VALID PROJECT TYPES: BI_Analytics, Data_Engineering, Workflow_Automation, AI_ML

   SWEEP #1 - Targeted with filters (REQUIRED):
   - **If you called research_company:** Parse the CompanyResearch JSON from step 1
   - Extract: industry field (e.g., "Healthcare", "E-commerce", "SaaS")
   - Extract keywords from business_description and pain_points
   - Pick project_type from VALID list (e.g., BI_Analytics or Data_Engineering)
   - Call search_relevant_projects(query="[keywords from company]", industry="Healthcare", project_type="BI_Analytics", mode="detailed")
   - CRITICAL: You MUST pass industry parameter from CompanyResearch if available

   SWEEP #2 - Broader search (REQUIRED):
   - Use general job description keywords
   - Call search_relevant_projects(query="analytics dashboards", mode="detailed")
   - CRITICAL: NO industry, NO project_type parameters

   COMBINE results from both sweeps, deduplicate, pick top 2-3 best matches

4. Use generate_content with deck content + case studies (mention "{deck_name}" in attachment note)
5. Use review_and_score to validate quality

Return the final proposal with quality score."""

        elif content_type == "catalant_proposal":
            prompt = f"""Generate a Catalant consulting proposal for this project:

{user_input}

DECK TO USE: {deck_name} (user selected - search for "{deck_query}" to get full deck content)

Follow the complete workflow:
1. Check if a SPECIFIC company name OR website URL is mentioned
   - If company URL (starts with http:// or https://): call research_company with the COMPLETE URL unchanged
   - If company name only (like "Acme Corp" or "Amazon"): call research_company with the company name
   - If neither: skip research_company
   - CRITICAL: If you see a URL, DO NOT extract the company name - pass the ENTIRE URL

2. FETCH SELECTED DECK CONTENT:
   - Call search_relevant_projects for: "{deck_query}" (mode="detailed")
   - This gets the full {deck_name} content from Supabase

3. TWO-SWEEP CASE STUDY SEARCH (to ensure best matches):

   VALID PROJECT TYPES: BI_Analytics, Data_Engineering, Workflow_Automation, AI_ML

   SWEEP #1 - Targeted with filters (REQUIRED):
   - **If you called research_company:** Parse CompanyResearch JSON from step 1
   - Extract: industry field (e.g., "Healthcare", "E-commerce")
   - Extract keywords from business_description
   - Pick project_type from VALID list (e.g., BI_Analytics or Data_Engineering)
   - Call search_relevant_projects(query="[context from company]", industry="Healthcare", project_type="BI_Analytics", mode="detailed")
   - CRITICAL: You MUST pass industry parameter from CompanyResearch if available

   SWEEP #2 - Broader (REQUIRED):
   - Use general description keywords
   - Call search_relevant_projects(query="analytics consulting", mode="detailed")
   - CRITICAL: NO industry or project_type parameters

   COMBINE both sweeps, deduplicate, pick top 2-3

4. Use generate_content with deck content + case studies (mention "{deck_name}" in attachment)
5. Use review_and_score to validate quality

Return the final proposal with quality score.
Note: Use formal Catalant format (credentials-first, numbered projects, professional tone)."""

        else:  # outreach_email
            prompt = f"""Generate a personalized outreach email for:

{user_input}

DECK TO USE: {deck_name} (user selected - search for "{deck_query}" to get content)

Follow the complete workflow:
1. Check if a SPECIFIC company name OR website URL is mentioned
   - If company URL (starts with http:// or https://): call research_company with the COMPLETE URL unchanged
   - If company name only: call research_company with the company name
   - If neither: skip research_company
   - CRITICAL: If you see a URL, DO NOT extract the company name - pass the ENTIRE URL

2. FETCH SELECTED DECK CONTENT:
   - Call search_relevant_projects for: "{deck_query}" (mode="detailed")

3. TWO-SWEEP CASE STUDY SEARCH (YOU MUST DO BOTH SWEEPS):
   VALID PROJECT TYPES: BI_Analytics, Data_Engineering, Workflow_Automation, AI_ML

   SWEEP #1 - Targeted with filters (REQUIRED):
   - Parse the CompanyResearch JSON you received in step 1
   - Extract: industry field (e.g., "Healthcare", "E-commerce")
   - Create query from their business_description or pain_points
   - Call search_relevant_projects(query="healthcare analytics", industry="Healthcare", project_type="BI_Analytics", mode="detailed")
   - CRITICAL: You MUST pass industry parameter from CompanyResearch

   SWEEP #2 - Broader no filters (REQUIRED):
   - Call search_relevant_projects(query="data analytics", mode="detailed")
   - NO industry, NO project_type parameters

   COMBINE both results, deduplicate

4. Use generate_content with deck content + case studies
5. Use review_and_score to validate quality

Return the final email with quality score."""

        # Run the agent
        try:
            print(f"\n{'='*60}")
            print(f"STARTING AGENT RUN")
            print(f"Prompt length: {len(prompt)} chars")
            print(f"{'='*60}\n")

            result = await agent.run(prompt, deps=agent_deps)

            print(f"\n{'='*60}")
            print(f"AGENT RUN COMPLETED SUCCESSFULLY")
            print(f"{'='*60}\n")

            return result.output

        except Exception as e:
            import traceback
            print(f"\n{'='*60}")
            print(f"ERROR IN AGENT.RUN()")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"\nFull traceback:")
            traceback.print_exc()
            print(f"{'='*60}\n")
            raise


def display_quality_score(score):
    """Display quality score with color coding."""
    if score >= 8.0:
        st.markdown(f'<p class="quality-score-high">✓ Quality Score: {score}/10</p>', unsafe_allow_html=True)
    elif score >= 6.0:
        st.markdown(f'<p class="quality-score-medium">⚠ Quality Score: {score}/10</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="quality-score-low">✗ Quality Score: {score}/10</p>', unsafe_allow_html=True)


def main():
    """Main Streamlit application."""

    # Header
    st.markdown('<h1 class="main-header">🎯 Brainforge Proposal Writer</h1>', unsafe_allow_html=True)
    st.markdown("Generate personalized Upwork proposals and outreach emails in under 5 minutes")

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key status
        brave_key = os.getenv("BRAVE_API_KEY", "")
        if brave_key:
            st.success("✓ Brave API configured")
        else:
            st.warning("⚠ Brave API key not configured")

        supabase_url = os.getenv("SUPABASE_URL", "")
        if supabase_url:
            st.success("✓ Supabase configured")
        else:
            st.error("✗ Supabase not configured")

        st.divider()
        st.subheader("📊 Session Stats")
        if "proposals_generated" not in st.session_state:
            st.session_state.proposals_generated = 0
        st.metric("Proposals Generated", st.session_state.proposals_generated)

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Input")

        # Mode selector
        content_type = st.radio(
            "Select Platform:",
            options=["upwork_proposal", "catalant_proposal", "outreach_email"],
            format_func=lambda x: {
                "upwork_proposal": "🎯 Upwork Proposal",
                "catalant_proposal": "💼 Catalant Proposal",
                "outreach_email": "📧 Outreach Email"
            }[x],
            horizontal=True
        )

        # Deck selector
        deck_type = st.radio(
            "Capabilities Deck:",
            options=["ai", "data"],
            format_func=lambda x: "🤖 AI Capabilities" if x == "ai" else "📊 Data Capabilities",
            horizontal=True,
            help="Choose which deck to include as proof of capabilities"
        )

        # Input text area
        if content_type == "upwork_proposal":
            placeholder = "Paste the Upwork job posting here...\n\nExample:\nLooking for a data analyst to build dashboards using Tableau and Snowflake for our e-commerce company..."
            help_text = "Paste the full Upwork job posting. Include company name if mentioned."
        elif content_type == "catalant_proposal":
            placeholder = "Paste the Catalant project brief here...\n\nExample:\nSeeking analytics architect to consolidate fragmented data sources and build a single source of truth..."
            help_text = "Paste the full Catalant project description."
        else:
            placeholder = "Enter company name or target information...\n\nExample:\nAcme Corp - e-commerce company looking to improve their analytics"
            help_text = "Provide company name and context for personalized outreach."

        user_input = st.text_area(
            "Input:",
            height=300,
            placeholder=placeholder,
            help=help_text
        )

        # Generate button
        generate_button = st.button(
            "🚀 Generate Proposal" if content_type == "upwork_proposal" else "🚀 Generate Email",
            type="primary",
            disabled=not user_input or len(user_input.strip()) < 20
        )

    with col2:
        st.subheader("📤 Output")

        # Initialize session state for generated content
        if "generated_content" not in st.session_state:
            st.session_state.generated_content = None
        if "generation_in_progress" not in st.session_state:
            st.session_state.generation_in_progress = False

        # Handle generation
        if generate_button and not st.session_state.generation_in_progress:
            st.session_state.generation_in_progress = True

            with st.spinner("🔍 Researching company and finding relevant projects..."):
                try:
                    # Run the workflow
                    result = asyncio.run(run_proposal_workflow(content_type, user_input, deck_type))

                    st.session_state.generated_content = result
                    st.session_state.proposals_generated += 1
                    st.session_state.generation_in_progress = False
                    st.rerun()

                except Exception as e:
                    st.error(f"Error generating content: {str(e)}")
                    st.session_state.generation_in_progress = False

        # Display generated content
        if st.session_state.generated_content:
            content = st.session_state.generated_content

            # Display the generated text
            st.markdown("### Generated Content")
            st.text_area(
                "Content:",
                value=content,
                height=300,
                key="content_display",
                label_visibility="collapsed"
            )

            # Action buttons
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if st.button("📋 Copy to Clipboard"):
                    st.code(content, language=None)
                    st.success("✓ Content ready to copy!")

            with col_b:
                if st.button("🔄 Regenerate"):
                    st.session_state.generated_content = None
                    st.rerun()

            with col_c:
                if st.button("💾 Download"):
                    st.download_button(
                        label="Download as .txt",
                        data=content,
                        file_name=f"{'proposal' if content_type == 'upwork_proposal' else 'email'}_{st.session_state.proposals_generated}.txt",
                        mime="text/plain"
                    )

            # Show editing option
            with st.expander("✏️ Edit Content"):
                edited_content = st.text_area(
                    "Edit your content:",
                    value=content,
                    height=300
                )
                if st.button("Save Edits"):
                    st.session_state.generated_content = edited_content
                    st.success("✓ Edits saved!")
                    st.rerun()

        else:
            st.info("Enter input and click Generate to create your proposal or email.")

    # Show instructions
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        ### Upwork Proposal Mode
        1. Copy and paste the full Upwork job posting
        2. Click "Generate Proposal"
        3. Review the generated proposal
        4. Copy to clipboard and paste into Upwork

        **Features:**
        - Automatic company research
        - Relevant project matching
        - Specific metrics and examples
        - Quality scoring

        ### Outreach Email Mode
        1. Enter the target company name and context
        2. Click "Generate Email"
        3. Review the personalized email
        4. Copy and send

        **Features:**
        - Company intelligence gathering
        - Case study matching
        - Professional tone
        - Call-to-action inclusion

        ### Tips for Best Results
        - Include company name when available
        - Mention specific technologies
        - Provide industry context
        - Review and customize before sending
        """)

    # Footer
    st.divider()
    st.caption("🤖 Powered by Brainforge | Built by Ryan Brosas")


if __name__ == "__main__":
    main()
