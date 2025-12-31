# 📖 Brainforge Proposal Writer - User Guide

Complete guide for using the Brainforge Proposal & Outreach Writer to generate high-quality proposals in under 5 minutes.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Template Customization](#template-customization) **NEW**
3. [Upwork Proposal Mode](#upwork-proposal-mode)
4. [Outreach Email Mode](#outreach-email-mode)
5. [Understanding Quality Scores](#understanding-quality-scores)
6. [Tips for Best Results](#tips-for-best-results)
7. [Troubleshooting](#troubleshooting)
8. [Example Workflows](#example-workflows)
9. [FAQ](#faq)

---

## Getting Started

### Launching the Application

1. **Activate your virtual environment**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. **Start Streamlit**
```bash
streamlit run streamlit_ui.py
```

3. **Open in browser**
- Streamlit will automatically open `http://localhost:8501`
- If not, manually navigate to that URL

### First-Time Setup Checklist

Before generating your first proposal:

- ✅ **Environment configured:** `.env` file has all required API keys
- ✅ **Supabase connected:** Database URL and service key are valid
- ✅ **Case studies ingested:** At least 5-10 case studies in Supabase
- ✅ **Brave API active:** (Optional) For company research
- ✅ **Test connection:** Check sidebar shows "✓ Brave API configured" and "✓ Supabase configured"

---

## Template Customization

### Overview

The proposal writer now supports customizable templates, tones, and content restrictions to match your brand voice and organizational guidelines.

**12 Combinations Available:**
- 3 Templates × 4 Tones = 12 unique writing styles

### Templates

#### 🔧 Technical Template
**Best for:** Engineering-heavy clients, technical stakeholders

**Characteristics:**
- Deep technical focus with detailed solution architecture
- High technical detail level
- Problem-solution opening style
- Section allocation: Context 10%, Challenge 15%, Solution 50%, Results 25%
- Metrics priority: Technical achievements

**Example Output:**
> "Our solution leverages a microservices architecture with Kubernetes orchestration, implementing a real-time data pipeline using Apache Kafka for event streaming..."

#### 💼 Consultative Template
**Best for:** C-level stakeholders, strategic engagements

**Characteristics:**
- Business-value driven with strategic insights
- Medium technical detail level
- Insight-first opening style
- Section allocation: Context 20%, Challenge 30%, Solution 30%, Results 20%
- Metrics priority: Business outcomes

**Example Output:**
> "We identified three key inefficiencies costing your organization $1.2M annually. Our strategic approach combines process optimization with targeted automation..."

#### ⚡ Quick Win Template
**Best for:** Urgent projects, fast turnarounds

**Characteristics:**
- Fast, results-focused highlighting quick delivery
- Low technical detail level
- Results-first opening style
- Section allocation: Context 5%, Challenge 15%, Solution 30%, Results 50%
- Metrics priority: Time savings

**Example Output:**
> "Delivered a 90% error reduction in just 2 weeks. Our rapid deployment methodology ensures immediate value while setting foundation for long-term success..."

### Tone Presets

#### 📋 Professional Tone
**Characteristics:**
- High formality level
- No contractions ("do not" vs "don't")
- Complex sentence structure
- Formal vocabulary
- Third-person perspective

**Example:** "The organization would benefit significantly from the implementation of these strategies."

#### 💬 Conversational Tone
**Characteristics:**
- Medium formality level
- Uses contractions naturally
- Varied sentence structure
- Accessible vocabulary
- First-person perspective

**Example:** "We've found that this approach works really well for teams like yours."

#### 🖥️ Technical Tone
**Characteristics:**
- Medium formality level
- No contractions
- Precise sentence structure
- Technical vocabulary and jargon
- First-person plural ("we")

**Example:** "We implemented a RESTful API architecture with JWT authentication, ensuring secure endpoint access."

#### 😊 Friendly Tone
**Characteristics:**
- Low formality level
- Uses contractions frequently
- Simple sentence structure
- Casual vocabulary
- Second-person ("you") perspective

**Example:** "You're going to love how easy this makes your workflow!"

### Content Restrictions

#### Forbidden Phrases
Block specific words or phrases from appearing in proposals.

**Use cases:**
- Competitor name blocking
- Overpromising language ("guaranteed", "100%")
- Casual language in formal contexts

**Wildcard Support:**
```sql
-- Block all phrases starting with "very"
forbidden_phrases: ["very *"]

-- Blocks: "very good", "very bad", "very effective"
```

#### Required Elements
Enforce that certain elements MUST appear in proposals.

**Use cases:**
- Mandatory credential mentions ("ISO 27001 certified")
- Required methodologies ("Agile", "Scrum")
- Compliance requirements

**Regex Support:**
```sql
-- Require at least one of these
required_elements: ["Python|JavaScript|TypeScript"]

-- Require specific phrase
required_elements: ["experience with data warehousing"]
```

#### Custom Word Counts
Override default word count ranges per content type.

**Defaults:**
- Upwork Proposals: 150-300 words
- Outreach Emails: 100-200 words

**Custom Example:**
```json
{
  "upwork_proposal": {"min": 200, "max": 400},
  "outreach_email": {"min": 150, "max": 250}
}
```

### How to Configure (Current Method: SQL)

**Note:** Settings UI is planned but not yet implemented. For now, use Supabase SQL Editor.

#### 1. View Available Templates
```sql
-- See all templates
SELECT id, name, template_type, description
FROM proposal_templates;

-- See all tones
SELECT id, name, tone_type, description
FROM tone_presets;
```

#### 2. Set Your Preferences
```sql
-- Set template and tone for default user
INSERT INTO user_preferences (user_id, template_id, tone_id)
VALUES ('default_user', 'consultative-001', 'conversational-001')
ON CONFLICT (user_id)
DO UPDATE SET
  template_id = EXCLUDED.template_id,
  tone_id = EXCLUDED.tone_id;
```

#### 3. Add Content Restrictions (Optional)
```sql
-- Add restrictions for default user
INSERT INTO content_restrictions (
  user_id,
  forbidden_phrases,
  required_elements,
  word_count_overrides
)
VALUES (
  'default_user',
  '["competitor_name", "guaranteed", "very *"]',
  '["Python", "Agile|Scrum", "AWS|Azure|GCP"]',
  '{"upwork_proposal": {"min": 200, "max": 400}}'
)
ON CONFLICT (user_id)
DO UPDATE SET
  forbidden_phrases = EXCLUDED.forbidden_phrases,
  required_elements = EXCLUDED.required_elements,
  word_count_overrides = EXCLUDED.word_count_overrides;
```

#### 4. Verify Configuration
```sql
-- Check your settings
SELECT
  up.user_id,
  pt.name as template_name,
  tp.name as tone_name,
  cr.forbidden_phrases,
  cr.required_elements,
  cr.word_count_overrides
FROM user_preferences up
LEFT JOIN proposal_templates pt ON up.template_id = pt.id
LEFT JOIN tone_presets tp ON up.tone_id = tp.id
LEFT JOIN content_restrictions cr ON up.user_id = cr.user_id
WHERE up.user_id = 'default_user';
```

### Testing Your Configuration

1. **Generate a test proposal** with your new settings
2. **Check the output style** matches your selected template/tone
3. **Verify restrictions** - Look for forbidden phrases in output
4. **Check word count** - Should match your custom range
5. **Review quality score** - Restrictions affect scoring

### Template Selection Guide

| Client Type | Recommended Template | Recommended Tone |
|-------------|---------------------|------------------|
| Enterprise CTO | Technical | Professional |
| Startup Founder | Quick Win | Conversational |
| VC/Investor | Consultative | Professional |
| Technical Manager | Technical | Technical |
| Business Analyst | Consultative | Conversational |
| Small Business Owner | Quick Win | Friendly |
| Product Manager | Consultative | Conversational |
| DevOps Team | Technical | Technical |

---

## Upwork Proposal Mode

### When to Use
- Responding to Upwork job postings
- Creating detailed proposals (400-600 words)
- When you have a specific job description
- When company name is mentioned in posting

### How to Use

#### Step 1: Select Mode
- Click the "📝 Upwork Proposal" radio button at the top

#### Step 2: Prepare Your Input
Copy the **entire Upwork job posting** including:
- Job title
- Job description
- Required skills/technologies
- Company name (if mentioned)
- Budget/timeline
- Any specific requirements

**Example Input:**
```
Title: Data Analytics Migration Specialist Needed

We're looking for an experienced data analyst to help us migrate our
e-commerce analytics from Google Analytics to a modern data warehouse.

Requirements:
- 3+ years experience with Snowflake
- Proficiency in dbt for data transformations
- Tableau dashboard creation
- Experience with e-commerce data

About us: GreenLeaf Organics is a growing sustainable products company
with 50+ employees and $10M annual revenue.

Budget: $5,000-$10,000
Timeline: 6-8 weeks
```

#### Step 3: Paste & Generate
1. Paste the job posting into the input text area
2. Click **"🚀 Generate Proposal"**
3. Wait 2-5 minutes while the agent works

#### Step 4: Monitor Progress
Watch the status updates:
- 🔍 Researching company...
- 🔍 Finding relevant projects...
- ✍️ Generating content...
- ✅ Reviewing quality...

#### Step 5: Review Output
Check the generated proposal for:
- **Company Context:** Does it mention GreenLeaf Organics specifically?
- **Relevant Projects:** Are 1-2 similar projects referenced?
- **Specific Metrics:** Do you see concrete numbers (e.g., "90% error reduction")?
- **Quality Score:** Is it ≥8/10?
- **Word Count:** 400-600 words?

#### Step 6: Copy & Customize
1. Click **"📋 Copy to Clipboard"**
2. Paste into Upwork proposal form
3. Add any personal touches or specific questions
4. Submit!

### What the Agent Does Behind the Scenes

```
1. research_company("GreenLeaf Organics")
   ↓ Finds: Industry (E-commerce), Size (SMB), Tech stack hints

2. search_relevant_projects(
     query="e-commerce analytics Snowflake dbt Tableau",
     tech_filter=["Snowflake", "dbt", "Tableau"],
     industry="E-commerce"
   )
   ↓ Matches: ABC Home case study (90% error reduction), Fashion retailer project

3. get_project_details(project_id="abc-home-001")
   ↓ Retrieves: Full case study with metrics, testimonial, tech stack

4. generate_content(
     content_type="upwork_proposal",
     company_research=...,
     relevant_projects=...,
     user_context=job_posting
   )
   ↓ Creates: 450-word proposal with specific examples

5. review_and_score(content=..., content_type="upwork_proposal")
   ↓ Scores: 8.5/10 (passes threshold)
   ↓ Returns: Final proposal
```

---

## Outreach Email Mode

### When to Use
- Cold outreach to potential clients
- Creating brief introductions (100-200 words)
- When you only have company name
- Follow-up emails after networking events

### How to Use

#### Step 1: Select Mode
- Click the "📧 Outreach Email" radio button

#### Step 2: Prepare Your Input
Provide **company name** and any additional context:

**Example Input:**
```
Company: DataCorp Solutions
Context: Met CEO Sarah Chen at TechCrunch Disrupt. They mentioned
struggling with data pipeline reliability. Focus on workflow automation.
```

**Minimal Input:**
```
Company: Acme Manufacturing
```

#### Step 3: Generate Email
1. Enter company info in the text area
2. Click **"🚀 Generate Email"**
3. Wait 2-3 minutes

#### Step 4: Review Output
Check the email for:
- **Personalized Greeting:** Uses contact name if found
- **Company Context:** References their industry/tech stack
- **Pain Point:** Mentions relevant challenge
- **Case Study:** 1 brief example with outcome
- **Call-to-Action:** Clear next step (usually Calendly link)
- **Length:** 100-200 words

#### Step 5: Customize & Send
1. Add recipient's name if not auto-detected
2. Update Calendly link to your actual link
3. Adjust tone if needed
4. Copy and send via email or LinkedIn

### Example Output

```
Subject: Workflow Automation for DataCorp Solutions

Hi Sarah,

Great meeting you at TechCrunch Disrupt! I enjoyed our conversation about
your data pipeline challenges.

At Brainforge, we specialize in workflow automation for data-intensive
companies. Recently, we helped ABC Home reduce their data processing errors
by 90% using n8n and Python-based automation—saving their team 50 hours/week.

I'd love to explore how we could help DataCorp improve pipeline reliability
and free up your engineering team's time.

Would you be open to a 20-minute call next week? You can grab a time here:
[Calendly link]

Best,
[Your name]
Brainforge
```

---

## Understanding Quality Scores

### Score Breakdown

Quality scores range from **1.0 to 10.0**. The agent **enforces a minimum of 8.0/10**.

| Score | Meaning | Action |
|-------|---------|--------|
| 9.0-10.0 | Excellent | Ready to send as-is |
| 8.0-8.9 | Good | Minor tweaks recommended |
| 6.0-7.9 | Fair | Agent auto-revises once |
| 1.0-5.9 | Poor | Needs significant revision |

### Scoring Criteria

**Specificity (40% weight)**
- ✅ Contains concrete metrics (percentages, dollar amounts, time saved)
- ✅ References specific projects by name
- ✅ Mentions exact technologies/tools used
- ❌ Generic claims without evidence

**Personalization (30% weight)**
- ✅ Company name mentioned 2+ times
- ✅ Industry-specific context
- ✅ Company's tech stack referenced
- ✅ Pain points identified
- ❌ Could apply to any company

**Structure (20% weight)**
- ✅ Professional tone
- ✅ Proper greeting and closing
- ✅ Logical flow (problem → solution → results)
- ✅ Clear call-to-action
- ❌ Grammatical errors or awkward phrasing

**Length (10% weight)**
- ✅ Upwork proposals: 400-600 words
- ✅ Outreach emails: 100-200 words
- ❌ Too brief or overly verbose

### What Happens If Score <8?

1. **First Review:** Agent identifies specific issues
2. **Auto-Revision:** Agent regenerates content with improvements
3. **Second Review:** New score calculated
4. **If still <8:** You see both versions + suggestions for manual editing

### Reading the Quality Report

When you expand the quality score section, you'll see:

**Passed Checks:**
- ✅ Has specific metrics
- ✅ References projects
- ✅ Proper word count
- ✅ Professional tone
- ✅ Has call-to-action

**Failed Checks:**
- ❌ Missing company context

**Specific Issues:**
```
Category: Personalization
Severity: Medium
Description: Company name mentioned only once
Suggestion: Add company-specific pain points or industry context
```

---

## Tips for Best Results

### 1. Input Quality Matters

**Good Inputs:**
- ✅ Complete job postings (don't edit/summarize)
- ✅ Include company name when available
- ✅ Mention specific technologies
- ✅ Include industry context

**Poor Inputs:**
- ❌ "Need help with data"
- ❌ Just a job title with no description
- ❌ Missing tech stack requirements

### 2. Case Study Preparation

The quality of your output depends on your case study library:

**Minimum:** 10-15 case studies
**Recommended:** 50+ case studies
**Ideal:** 100+ case studies across industries

Ensure case studies have:
- ✅ YAML frontmatter with metadata
- ✅ Specific metrics in the Results section
- ✅ Client testimonials when available
- ✅ Technology stack documented

See [DATA_PREPARATION.md](DATA_PREPARATION.md) for details.

### 3. Company Research

**With Brave API (Recommended):**
- More personalized proposals
- Industry and tech stack auto-detected
- Recent news and pain points discovered
- Higher quality scores

**Without Brave API:**
- Generic company context
- Relies only on what's in job posting
- Lower personalization scores
- Still functional, but less impressive

### 4. Iteration Strategy

If quality score is 7.5-7.9:
1. Let agent auto-revise
2. Review both versions
3. Cherry-pick best parts from each

If quality score is consistently low:
1. Check case study data quality
2. Ensure Brave API is configured
3. Verify job posting has enough detail

### 5. Post-Generation Editing

**Always customize:**
- Add personal anecdotes or connections
- Update Calendly links to your actual link
- Adjust tone for specific recipients
- Add specific questions about their needs

**Never change:**
- Specific metrics (they're validated from case studies)
- Project names (clients may verify)
- Technical details (must be accurate)

---

## Troubleshooting

### Issue: "No matching projects found"

**Cause:** RAG search didn't find relevant case studies

**Solutions:**
1. Check case studies are ingested:
   ```bash
   python RAG_Pipeline/Local_Files/main.py --directory "./Files"
   ```
2. Verify Supabase `documents` table has data
3. Broaden search by removing restrictive filters
4. Add more case studies to your library

### Issue: "Company research unavailable"

**Cause:** Brave API key missing or invalid

**Solutions:**
1. Check `.env` has `BRAVE_API_KEY=your-key`
2. Verify API key at https://api.search.brave.com/app/keys
3. Check API quota hasn't been exceeded
4. Fallback: Agent uses job posting context only

### Issue: "Quality score stuck at 6-7"

**Cause:** Insufficient personalization or specificity

**Solutions:**
1. Enable Brave API for better company research
2. Add more case studies with concrete metrics
3. Ensure YAML frontmatter has metrics field:
   ```yaml
   metrics:
     - type: "error_reduction"
       value: 90
       unit: "percent"
   ```
4. Manually edit to add missing details

### Issue: "Generation takes >10 minutes"

**Cause:** Network latency or API rate limits

**Solutions:**
1. Use `response_format="concise"` in research_company
2. Reduce `max_results` in search (default is 5)
3. Check internet connection
4. Switch to faster LLM (e.g., gpt-4o-mini vs gpt-4o)

### Issue: "Streamlit crashes or freezes"

**Cause:** Memory/resource issues

**Solutions:**
1. Restart Streamlit
2. Clear cache: Delete `.streamlit/` folder
3. Check Python memory usage
4. Reduce concurrent requests

### Issue: "Tools not being called"

**Cause:** Agent configuration or system prompt issue

**Solutions:**
1. Verify all tools registered:
   ```python
   python -c "from agent import agent; print(len(agent._function_tools))"
   # Should print: 10
   ```
2. Check prompt.py has correct workflow instructions
3. Restart Streamlit to reload agent

---

## Example Workflows

### Workflow 1: Quick Upwork Proposal (No Company)

**Input:**
```
Looking for React developer to build dashboard. Need charts, tables,
real-time updates. Must know TypeScript and Tailwind CSS.
```

**Agent Actions:**
1. ~~Skip research_company~~ (no company mentioned)
2. search_relevant_projects(query="React dashboard TypeScript", tech_filter=["React", "TypeScript"])
3. get_project_details for 2 matches
4. generate_content (upwork_proposal)
5. review_and_score

**Time:** ~3 minutes

### Workflow 2: Detailed Upwork Proposal (With Company)

**Input:**
```
[Full 500-word job posting from Shopify merchant about inventory system,
company name: "Urban Threads Boutique"]
```

**Agent Actions:**
1. research_company("Urban Threads Boutique") → Industry: E-commerce/Fashion
2. search_relevant_projects(query="inventory system e-commerce", industry="E-commerce")
3. get_project_details for top 3 matches
4. generate_content with full company context
5. review_and_score → 9.2/10

**Time:** ~5 minutes

### Workflow 3: Outreach Email

**Input:**
```
Company: Acme Manufacturing
Context: Saw they're hiring data engineers. Probably need pipeline automation.
```

**Agent Actions:**
1. research_company("Acme Manufacturing") → Industry, size, tech stack
2. search_relevant_projects(query="data pipeline automation", industry="Manufacturing")
3. get_project_details (1 best match)
4. generate_content (outreach_email)
5. review_and_score → 8.7/10

**Time:** ~2 minutes

---

## FAQ

### Q: Can I edit the generated content?

**A:** Absolutely! Click the "✏️ Edit Content" expander to modify. The content is meant to be a strong first draft—always customize for your voice and specific situation.

### Q: How many case studies do I need?

**A:** Minimum 10-15, but 50+ is ideal. More case studies = better matches = higher quality proposals.

### Q: What if the company name isn't mentioned?

**A:** The agent will skip research_company and focus on tech stack matching. You'll still get a good proposal, just less personalized.

### Q: Can I use this for other content types?

**A:** Yes! The system supports:
- `upwork_proposal` (400-600 words)
- `outreach_email` (100-200 words)
- `rfp_response` (formal RFP format)

You can extend it by adding templates in `proposal_tools.py`.

### Q: Does this work offline?

**A:** Partially. If you use Ollama for LLM + embeddings and disable Brave API, it works offline. But Supabase requires internet.

### Q: How do I add my Calendly link?

**A:** Edit `proposal_tools.py` around line 380 and add your Calendly URL to the email template. Or manually replace it post-generation.

### Q: Can I change the word count limits?

**A:** Yes, use the `word_limit` parameter in generate_content, or modify the templates in `proposal_tools.py`.

### Q: What LLM should I use?

**A:**
- **Best quality:** `gpt-4o` or `claude-sonnet-4.5`
- **Best speed:** `gpt-4o-mini`
- **Local/Free:** Ollama with `qwen2.5:14b-instruct`

### Q: Is my data secure?

**A:** Your case studies are stored in your own Supabase instance. API calls go to OpenAI/Brave/etc. Never commit your `.env` file.

### Q: Can multiple people use this?

**A:** Yes, but each needs their own API keys and Supabase project (or share one Supabase project with separate data).

---

## Next Steps

- **Prepare Your Case Studies:** [DATA_PREPARATION.md](DATA_PREPARATION.md)
- **Deploy to Production:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Customize Tools:** See [CLAUDE.md](CLAUDE.md) for development guide

---

**Need Help?**
- Check [Troubleshooting](#troubleshooting) section
- Review [README.md](README.md) for setup issues
- Open an issue on GitHub

**Happy Proposing! 🎯**
