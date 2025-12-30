# 📊 Data Preparation Guide - Case Studies for RAG

Complete guide for converting your case studies into the format required by the Brainforge Proposal Writer's RAG system.

---

## Table of Contents

1. [Overview](#overview)
2. [Required Format](#required-format)
3. [Metadata Schema Reference](#metadata-schema-reference)
4. [Conversion Process](#conversion-process)
5. [Quality Standards](#quality-standards)
6. [RAG Ingestion](#rag-ingestion)
7. [Example Templates](#example-templates)
8. [Validation](#validation)

---

## Overview

### Why Proper Formatting Matters

The proposal writer uses **Retrieval Augmented Generation (RAG)** to find relevant case studies. Proper formatting ensures:

- ✅ **Accurate Matching:** Filters work correctly (tech_stack, industry, project_type)
- ✅ **Better Quality:** Agent can extract specific metrics and outcomes
- ✅ **Higher Scores:** Generated proposals reference concrete examples
- ✅ **Faster Search:** Metadata filters reduce irrelevant results

### What You Need to Provide

**Capability Decks:**
- **1-2 AI/ML capabilities decks** - Showcase AI, automation, chatbot capabilities
- **1-2 Data/Analytics decks** - Showcase BI, analytics, data engineering capabilities
- **Optional:** General capabilities overview deck

**Case Studies:**
- **Minimum:** 10-15 case studies
- **Recommended:** 50+ case studies
- **Ideal:** 100+ case studies across industries

Each document should be:
1. Converted to **Markdown format** (.md file)
2. Include **YAML frontmatter** with metadata
3. Have **structured sections** (Context, Challenge, Solution, Results)
4. Contain **specific metrics** in the Results section (case studies only)

---

## Required Format

### File Structure

#### For Capability Decks:

```markdown
---
title: "Brainforge AI & Automation Capabilities"  # Or "Data & Analytics Capabilities"
client: "Brainforge"
industry: "Multi-Industry"
project_type: "AI_ML"  # Or "BI_Analytics" for data decks
tech_stack: ["Python", "OpenAI", "LangChain", "FastAPI", "n8n"]
function: "AI/ML Engineering"  # Or "Data Analytics"
project_status: "Ongoing"
testimonial: false
---

# Brainforge [AI/Data] Capabilities

## Overview
High-level description of Brainforge's capabilities in this domain...

## Core Capabilities
List of key services and expertise areas...

## Technologies & Tools
Comprehensive tech stack...

## Example Use Cases
3-5 sample applications with brief metrics...

## Why Choose Brainforge
Unique value propositions...
```

**Naming Convention for Decks:**
- `Brainforge_AI_Capabilities.md` - For AI/ML/automation focused decks
- `Brainforge_Data_Capabilities.md` - For data/analytics focused decks
- `Brainforge_Capabilities_Overview.md` - For general overview

#### For Case Studies:

```markdown
---
title: "Project Name"
client: "Client Company Name"
industry: "E-commerce"
project_type: "BI_Analytics"
tech_stack: ["Snowflake", "dbt", "Tableau"]
function: "Data Analytics"
project_status: "Completed"
metrics:
  - type: "win_rate"
    value: 33
    unit: "percent"
  - type: "time_saved"
    value: 50
    unit: "hours_per_week"
testimonial: true
---

# Project Name

## Context
Brief background about the client and their business situation...

## Challenge
What problem were they facing? Be specific...

## Solution
What did Brainforge build? Include technologies and approach...

## Results
Concrete outcomes and metrics achieved...

## Testimonial (Optional)
"Quote from client contact..." - Name, Title, Company
```

### YAML Frontmatter (Metadata)

**Required Fields:**
- `title` - Project name (string)
- `client` - Client company name (string)
- `industry` - Industry category (string)
- `project_type` - Type of project (string)
- `tech_stack` - Technologies used (array of strings)

**Optional Fields:**
- `function` - Business function (string)
- `project_status` - Status (string: "Completed", "Ongoing", "Paused")
- `metrics` - Quantified outcomes (array of objects)
- `testimonial` - Whether client quote included (boolean)
- `team` - Brainforge team members (array of strings)
- `duration` - Project length (string)
- `budget_range` - Approximate budget (string)

---

## Metadata Schema Reference

### Industry Values

Use consistent industry labels across all case studies:

```yaml
# Recommended Industry Values
industry: "E-commerce"          # Online retail, marketplaces
industry: "Home Services"       # HVAC, plumbing, contracting
industry: "Healthcare"          # Medical, healthcare tech
industry: "SaaS"                # Software companies
industry: "Manufacturing"       # Physical goods production
industry: "Finance"             # Banking, fintech, insurance
industry: "Education"           # EdTech, training, universities
industry: "Real Estate"         # Property management, construction
industry: "Retail"              # Brick-and-mortar stores
industry: "Logistics"           # Transportation, supply chain
industry: "Marketing"           # Agencies, martech
industry: "Hospitality"         # Hotels, restaurants, tourism
industry: "Media"               # Publishing, broadcasting
industry: "Non-Profit"          # NGOs, associations
```

### Project Type Values

```yaml
# Recommended Project Type Values
project_type: "BI_Analytics"           # Dashboards, reporting, viz
project_type: "Data_Engineering"       # Pipelines, ETL, warehousing
project_type: "Workflow_Automation"    # n8n, Zapier, RPA
project_type: "AI_ML"                  # Machine learning, NLP, computer vision
project_type: "Web_Development"        # Full-stack apps, websites
project_type: "Mobile_App"             # iOS, Android apps
project_type: "Database_Design"        # Schema design, optimization
project_type: "Cloud_Migration"        # AWS, Azure, GCP migrations
project_type: "API_Integration"        # Third-party API work
project_type: "Process_Optimization"   # Business process improvement
project_type: "Data_Migration"         # Moving data between systems
project_type: "Custom_Tool"            # Internal tools, scripts
```

### Tech Stack Values

Use official technology names consistently:

```yaml
tech_stack:
  # Databases
  - "PostgreSQL"
  - "MySQL"
  - "MongoDB"
  - "Snowflake"
  - "BigQuery"
  - "Supabase"

  # Data Tools
  - "dbt"
  - "Apache Airflow"
  - "Fivetran"
  - "Airbyte"

  # Visualization
  - "Tableau"
  - "Power BI"
  - "Looker"
  - "Metabase"

  # Automation
  - "n8n"
  - "Zapier"
  - "Make"

  # Languages
  - "Python"
  - "JavaScript"
  - "TypeScript"
  - "SQL"

  # Frameworks
  - "React"
  - "Next.js"
  - "FastAPI"
  - "Django"

  # Cloud
  - "AWS"
  - "Azure"
  - "Google Cloud"

  # AI/ML
  - "OpenAI"
  - "LangChain"
  - "HuggingFace"
```

### Metrics Schema

Each metric should have:
- `type` - Category of metric (string)
- `value` - Numeric value (number)
- `unit` - Unit of measurement (string)

```yaml
metrics:
  # Time Savings
  - type: "time_saved"
    value: 50
    unit: "hours_per_week"

  # Error Reduction
  - type: "error_reduction"
    value: 90
    unit: "percent"

  # Revenue Impact
  - type: "revenue_increase"
    value: 250000
    unit: "dollars_per_year"

  # Cost Savings
  - type: "cost_savings"
    value: 120000
    unit: "dollars_per_year"

  # Performance
  - type: "speed_improvement"
    value: 75
    unit: "percent"

  # User Satisfaction
  - type: "satisfaction_score"
    value: 4.8
    unit: "out_of_5"

  # Efficiency
  - type: "process_efficiency"
    value: 300
    unit: "percent"

  # Conversion
  - type: "conversion_rate_lift"
    value: 45
    unit: "percent"
```

### Function Values

```yaml
function: "Data Analytics"
function: "Customer Support"
function: "Sales & Marketing"
function: "Operations"
function: "Finance"
function: "Product Management"
function: "Engineering"
function: "Human Resources"
```

---

## Conversion Process

### Step 1: Gather Source Materials

Collect your case studies from:
- PDF case studies
- PowerPoint presentations
- Word documents
- Client project reports
- Internal documentation

### Step 2: Extract Core Information

For each case study, identify:

**Basic Info:**
- Project name
- Client name (anonymize if needed)
- When it was completed
- Which team members worked on it

**Context:**
- What was the client's business?
- What was their situation before Brainforge?
- Why did they need help?

**Challenge:**
- What specific problem did they face?
- What was the impact of this problem?
- What had they tried before?

**Solution:**
- What did Brainforge build?
- What technologies were used?
- What was the approach/methodology?

**Results:**
- What metrics improved? (Be specific!)
- What feedback did the client give?
- Are they still using the solution?

### Step 3: Create Markdown File

1. Create a new `.md` file in the `Files/` directory
2. Name it descriptively: `ClientName_ProjectType_CaseStudy.md`
   - Example: `ABC_Home_Workflow_Automation.md`
   - Example: `Fashion_Retailer_BI_Analytics.md`

### Step 4: Add YAML Frontmatter

At the very top of the file, add metadata:

```markdown
---
title: "ABC Home Workflow Automation"
client: "ABC Home Services"
industry: "Home Services"
project_type: "Workflow_Automation"
tech_stack: ["n8n", "Python", "PostgreSQL", "Supabase"]
function: "Customer Support"
project_status: "Ongoing"
metrics:
  - type: "error_reduction"
    value: 90
    unit: "percent"
  - type: "time_saved"
    value: 50
    unit: "hours_per_week"
testimonial: true
team: ["Alice", "Bob"]
duration: "3 months"
---
```

### Step 5: Write Structured Content

Use Markdown headers (`##`) for each section:

```markdown
# ABC Home Workflow Automation

## Context
ABC Home Services is a regional HVAC and plumbing company with 45 technicians
serving 3,000+ customers. They were managing service calls through a
combination of phone, email, and spreadsheets...

## Challenge
- Manual data entry led to 15% error rate in customer records
- Dispatchers spent 25 hours/week on administrative tasks
- No visibility into technician availability or job status
- Customer satisfaction scores were declining (3.2/5)

## Solution
Brainforge built an automated workflow system using n8n and Python:
1. **Intake Automation:** Phone calls → automated transcription → CRM entry
2. **Smart Dispatching:** Algorithm matches technicians to jobs based on...
3. **Real-time Updates:** Supabase database with live job tracking...

Technologies:
- n8n for workflow orchestration
- Python scripts for business logic
- PostgreSQL + Supabase for data storage
- Twilio API for SMS notifications

## Results
After 3 months of implementation:

- **90% reduction** in data entry errors (15% → 1.5%)
- **50 hours/week saved** in dispatcher time
- **4.8/5 customer satisfaction** rating (up from 3.2)
- **23% increase** in jobs completed per technician

The system now handles 200+ service calls per day automatically.

## Testimonial
"This automation has transformed our operations. Our dispatchers can now
focus on complex issues instead of data entry. It's been a game-changer."
- Sarah Johnson, Operations Manager, ABC Home Services
```

### Step 6: Add Specific Metrics

**Always include concrete numbers:**

✅ **Good:**
- "90% reduction in data entry errors"
- "Saved 50 hours per week"
- "$120,000 annual cost savings"
- "4.8/5 customer satisfaction rating"

❌ **Bad:**
- "Significant improvement"
- "Much faster"
- "Happier customers"
- "Better efficiency"

### Step 7: Review for Quality

Checklist before saving:
- [ ] YAML frontmatter is valid (check indentation!)
- [ ] All required metadata fields present
- [ ] Tech stack uses official names
- [ ] At least 2 specific metrics in Results section
- [ ] Sections use `##` headers
- [ ] No placeholder text or "TODO" items
- [ ] Client name is consistent throughout

---

## Quality Standards

### Minimum Quality Criteria

**For the RAG system to work well:**

1. **Specificity:**
   - ✅ "Reduced errors by 90%"
   - ❌ "Reduced errors significantly"

2. **Completeness:**
   - All 4 sections present (Context, Challenge, Solution, Results)
   - At least 100 words per section

3. **Metadata Accuracy:**
   - Tech stack matches what's mentioned in Solution
   - Metrics match what's stated in Results
   - Industry/type are searchable categories

4. **Consistency:**
   - Use same industry labels across all case studies
   - Use same tech names (e.g., "PostgreSQL" not "Postgres" or "psql")
   - Use same metric types

### Best Practices

**DO:**
- Use real client names (or consistent pseudonyms)
- Include testimonials when available
- Add team members for credit
- Use percentages AND absolute numbers
- Keep format consistent across all case studies

**DON'T:**
- Mix different naming conventions
- Use vague metrics ("improved performance")
- Skip the YAML frontmatter
- Use different section names
- Include sensitive client data

---

## RAG Ingestion

### Local Files Pipeline

Once your case studies are ready:

1. **Place files in the `Files/` directory**
```bash
Files/
├── ABC_Home_Workflow_Automation.md
├── Fashion_Retailer_BI_Analytics.md
├── Healthcare_Data_Migration.md
└── ... (more case studies)
```

2. **Run the ingestion pipeline**
```bash
cd RAG_Pipeline
python Local_Files/main.py --directory "../Files"
```

3. **Monitor progress**
```
Processing: ABC_Home_Workflow_Automation.md
  Extracting text... ✓
  Chunking (400 chars)... ✓
  Generating embeddings... ✓
  Uploading to Supabase... ✓

Processed 1/50 files...
```

4. **Verify in Supabase**
- Open your Supabase project
- Navigate to Table Editor → `documents`
- Check that rows exist with your case study metadata

### Google Drive Pipeline (Optional)

If you prefer storing case studies in Google Drive:

1. **Set up Google Drive API credentials** (see RAG_Pipeline/README.md)

2. **Place files in a Drive folder**

3. **Run the Drive watcher**
```bash
python RAG_Pipeline/Google_Drive/main.py --folder-id "your-folder-id"
```

4. **Auto-sync**
- Pipeline watches for new/updated files
- Automatically re-ingests on changes

### Troubleshooting Ingestion

**"No files processed"**
- Check file paths are correct
- Verify `.md` extension
- Check file permissions (must be readable)

**"YAML parsing error"**
- Validate YAML syntax at https://www.yamllint.com/
- Check indentation (must be 2 spaces)
- Ensure colons have spaces after them: `title: "Name"` not `title:"Name"`

**"Embedding generation failed"**
- Check `EMBEDDING_API_KEY` in `.env`
- Verify Supabase connection
- Check API quota limits

---

## Example Templates

### Template 0: Capability Deck (AI/ML Focus)

```markdown
---
title: "Brainforge AI & Automation Capabilities"
client: "Brainforge"
industry: "Multi-Industry"
project_type: "AI_ML"
tech_stack: ["Python", "OpenAI", "LangChain", "FastAPI", "n8n", "Anthropic"]
function: "AI/ML Engineering"
project_status: "Ongoing"
testimonial: false
---

# Brainforge AI & Automation Capabilities

## Overview
Brainforge specializes in building production-ready AI agents and workflow automation
systems that integrate seamlessly with existing business processes.

## Core Capabilities

### AI Agent Development
- Custom AI agents using GPT-4, Claude, and open-source models
- Multi-tool orchestration with function calling
- RAG (Retrieval Augmented Generation) systems
- Conversational interfaces and chatbots

### Workflow Automation
- n8n workflow design and implementation
- API integrations and webhooks
- Process automation and optimization
- Event-driven architectures

### Technologies & Frameworks
- **LLMs:** OpenAI GPT-4, Anthropic Claude, Ollama (local models)
- **Agent Frameworks:** LangChain, PydanticAI, AutoGen
- **Automation:** n8n, Zapier, Make
- **Infrastructure:** FastAPI, Docker, PostgreSQL, Supabase

## Example Use Cases
- Customer support automation (85% call handling automation)
- Document processing and analysis (10x faster processing)
- Intelligent routing and triage systems
- Knowledge base Q&A systems

## Why Choose Brainforge
- **Production-Ready:** Enterprise-grade reliability and security
- **Fast Delivery:** MVP in 2-4 weeks
- **Deep Expertise:** 50+ AI/automation projects delivered
- **Full Stack:** From research to deployment and monitoring
```

### Template 0b: Capability Deck (Data/Analytics Focus)

```markdown
---
title: "Brainforge Data & Analytics Capabilities"
client: "Brainforge"
industry: "Multi-Industry"
project_type: "BI_Analytics"
tech_stack: ["Snowflake", "dbt", "Tableau", "Power BI", "Python", "Airflow"]
function: "Data Analytics"
project_status: "Ongoing"
testimonial: false
---

# Brainforge Data & Analytics Capabilities

## Overview
Brainforge builds modern data stacks that transform raw data into actionable insights,
enabling data-driven decision making across organizations.

## Core Capabilities

### Data Engineering
- Cloud data warehouse setup (Snowflake, BigQuery, Redshift)
- ETL/ELT pipeline development with dbt
- Data orchestration with Apache Airflow
- Real-time data streaming

### Business Intelligence
- Interactive dashboards (Tableau, Power BI, Looker)
- Executive reporting and KPI tracking
- Self-service analytics platforms
- Custom visualization development

### Technologies & Tools
- **Warehouses:** Snowflake, BigQuery, PostgreSQL
- **Transformation:** dbt, SQL, Python
- **Visualization:** Tableau, Power BI, Metabase
- **Orchestration:** Airflow, Dagster, Prefect
- **Integration:** Fivetran, Airbyte, custom APIs

## Example Use Cases
- E-commerce analytics dashboards (75% faster decision-making)
- Marketing attribution modeling (350K revenue increase)
- Supply chain optimization (40% cost reduction)
- Customer cohort analysis and retention tracking

## Why Choose Brainforge
- **Modern Stack:** Latest cloud-native technologies
- **Fast ROI:** Insights delivered in weeks, not months
- **Proven Results:** 50+ data projects with measurable impact
- **Full Service:** Strategy, implementation, training, and support
```

### Template 1: BI/Analytics Project

```markdown
---
title: "E-commerce Analytics Dashboard"
client: "GreenLeaf Organics"
industry: "E-commerce"
project_type: "BI_Analytics"
tech_stack: ["Snowflake", "dbt", "Tableau", "Fivetran"]
function: "Data Analytics"
project_status: "Completed"
metrics:
  - type: "decision_speed"
    value: 75
    unit: "percent_faster"
  - type: "revenue_increase"
    value: 350000
    unit: "dollars_per_year"
testimonial: true
duration: "4 months"
---

# E-commerce Analytics Dashboard for GreenLeaf Organics

## Context
GreenLeaf Organics is a sustainable products e-commerce company with
$10M annual revenue and 50 employees. They were using Google Analytics
and spreadsheets for reporting, leading to delayed decision-making.

## Challenge
- Data scattered across 5 systems (Shopify, GA, Klaviyo, Facebook Ads, Google Ads)
- Monthly reports took 2 weeks to compile manually
- No real-time visibility into product performance
- Marketing team couldn't optimize campaigns quickly

## Solution
Brainforge built a modern data stack:
1. **Data Ingestion:** Fivetran to pull from all sources → Snowflake
2. **Transformations:** dbt models for clean, business-ready data
3. **Visualization:** Tableau dashboards for executives and marketing team

Key features:
- Real-time product performance tracking
- Customer cohort analysis
- Marketing attribution modeling
- Automated daily email reports

## Results
After 4 months:
- **75% faster decision-making** (2 weeks → 2 days for insights)
- **$350K revenue increase** from optimized marketing spend
- **100% data accuracy** (vs 85% with spreadsheets)
- **4.9/5 stakeholder satisfaction** with dashboard quality

## Testimonial
"The dashboards have completely changed how we run the business. We make
data-driven decisions daily instead of monthly."
- Michael Chen, CEO, GreenLeaf Organics
```

### Template 2: Workflow Automation

```markdown
---
title: "Customer Support Automation"
client: "TechStart SaaS"
industry: "SaaS"
project_type: "Workflow_Automation"
tech_stack: ["n8n", "OpenAI", "Supabase", "Slack"]
function: "Customer Support"
project_status: "Ongoing"
metrics:
  - type: "response_time"
    value: 85
    unit: "percent_reduction"
  - type: "resolution_rate"
    value: 40
    unit: "percent_increase"
  - type: "cost_savings"
    value: 180000
    unit: "dollars_per_year"
testimonial: false
team: ["Sarah", "Dev"]
---

# Customer Support Automation for TechStart SaaS

## Context
TechStart SaaS provides project management software to 5,000+ customers.
Their support team of 12 was overwhelmed with repetitive questions...

[Continue with Challenge, Solution, Results sections...]
```

### Template 3: Data Migration

```markdown
---
title: "Legacy System Migration to Cloud"
client: "Regional Hospital Network"
industry: "Healthcare"
project_type: "Data_Migration"
tech_stack: ["Python", "PostgreSQL", "AWS", "Apache Airflow"]
function: "Engineering"
project_status: "Completed"
metrics:
  - type: "migration_accuracy"
    value: 99.97
    unit: "percent"
  - type: "downtime"
    value: 4
    unit: "hours"
  - type: "cost_savings"
    value: 500000
    unit: "dollars_per_year"
testimonial: true
duration: "6 months"
budget_range: "$100k-$250k"
---

[Rest of case study...]
```

---

## Validation

### Automated Validation

Create a validation script (`validate_case_studies.py`):

```python
import yaml
from pathlib import Path

def validate_case_study(file_path):
    """Validate a case study file."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Check for YAML frontmatter
    if not content.startswith('---'):
        return False, "Missing YAML frontmatter"

    # Extract YAML
    parts = content.split('---', 2)
    try:
        metadata = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {e}"

    # Check required fields
    required = ['title', 'client', 'industry', 'project_type', 'tech_stack']
    for field in required:
        if field not in metadata:
            return False, f"Missing required field: {field}"

    # Check metrics structure
    if 'metrics' in metadata:
        for metric in metadata['metrics']:
            if not all(k in metric for k in ['type', 'value', 'unit']):
                return False, "Invalid metric structure"

    return True, "Valid"

# Run validation
files_dir = Path("Files")
for md_file in files_dir.glob("*.md"):
    valid, message = validate_case_study(md_file)
    print(f"{md_file.name}: {message}")
```

### Manual Checklist

For each case study:

- [ ] File is in `Files/` directory
- [ ] Filename is descriptive (Client_Type.md)
- [ ] YAML frontmatter present and valid
- [ ] All required metadata fields filled
- [ ] Tech stack uses official names
- [ ] At least 2 metrics in YAML
- [ ] All 4 sections present (Context, Challenge, Solution, Results)
- [ ] Specific numbers in Results section
- [ ] No placeholder text
- [ ] File runs through ingestion pipeline without errors

---

## Next Steps

1. **Convert 10-15 case studies** to start
2. **Run ingestion pipeline** to test
3. **Generate a test proposal** to verify quality
4. **Gradually add more case studies** (aim for 50+)
5. **Maintain consistency** in metadata across all files

---

**Need Help?**
- Check example case studies in `Files/` directory
- Review RAG_Pipeline/README.md for ingestion details
- See USER_GUIDE.md for testing proposals with your case studies

**Good luck! 📊**
