---
title: "AI Agent Performance Dashboard"
client: "ABC Home & Commercial"
industry: "Home Services"
project_type: "BI_Analytics"
tech_stack: ["n8n", "Snowflake", "Rill", "Braintrust", "Google Chat", "Linear"]
function: "Customer Support"
project_status: "Completed"
metrics:
  - type: "data_capture_rate"
    value: 100
    unit: "percent"
  - type: "feedback_capture_rate"
    value: 90
    unit: "percent"
  - type: "tracking_speed_improvement"
    value: 60
    unit: "percent"
testimonial: false
team: ["Project Manager", "AI Engineer"]
duration: "9 months"
budget_range: "[MISSING]"
---

# AI Agent Performance Dashboard for ABC Home & Commercial

## Context

[START OF SECTION]

ABC Home & Commercial is one of Texas's largest home and commercial service providers. In February 2025, Brainforge partnered with them to build a performance dashboard for their AI agent, Andi.

The dashboard was designed to give Customer Service Representatives (CSRs) a clear view of how Andi supports their work, while also providing leadership with visibility into usage, quality, and overall business impact.

This project followed the initial development of the Andi AI agent (a separate engagement), and addressed the critical need to measure and prove the AI's value to the organization.

[END OF SECTION]

## Challenge

[START OF SECTION]

CSRs wanted AI support they could count on, but there was no system in place to measure quality or usage. The organization faced several key obstacles:

- **No measurement system:** There was no way to track AI answer quality or adoption rates
- **Scattered feedback:** CSR feedback was fragmented and difficult to aggregate
- **Recurring issues unresolved:** Without systematic tracking, the same problems kept appearing
- **Leadership blind spot:** Leaders had no visibility into adoption metrics or business impact
- **Trust deficit:** Without clear metrics, the AI risked becoming another tool that promised value but never delivered

The core question became: "Does your AI agent actually work?" — and there was no data-driven way to answer it.

[END OF SECTION]

## Solution

[START OF SECTION]

Brainforge built ABC Home & Commercial a comprehensive dashboard to track AI performance end-to-end. The solution included four key components:

**1. Response Logging & Observability**
Logged all AI responses in Snowflake, creating a complete audit trail and enabling detailed analysis of agent performance over time.

**2. Real-Time Feedback Collection**
Added Google Chat integration so CSRs could rate AI answers in real time using a simple thumbs up/down system, along with detailed feedback options.

**3. Automated Issue Triage**
Routed negative feedback automatically into Linear for triage and follow-up, ensuring no quality issues fell through the cracks.

**4. Collaborative Responsibility Model**
Split responsibilities between client teams and Brainforge's internal team for faster fixes and continuous improvement cycles.

**Dashboard Features:**
- Total exchange tracking with trend visualization
- Average quality score monitoring (scale 0-10)
- Combined score metrics
- Error rate tracking
- Average execution time monitoring
- Escalation rate tracking
- Thumbs up/down counts with CSR attribution
- Detailed feedback categorization
- Conversation-level drill-down capability

![Dashboard Screenshot](image-placeholder-01.png)
> OCR/Caption: Dashboard showing AI adoption metrics including 239 total exchanges, 8.8 avg quality score (0-10), 9.1 avg combined score (0-10), error rate visualization, 5.2 avg execution time, 0% needs escalation, 62 thumbs up count, 17 thumbs down count. Right panel shows thumbs feedback breakdown (163 no feedback, 42 thumbs up, 17 thumbs down), detailed feedback categories, quality scores, combined scores, incorrect answer flags, needs escalation flags, record IDs, conversation IDs, input/output tables, username tracking, and DBTM category filtering.

**Technologies Used:**
- **n8n** — Workflow orchestration and automation
- **Snowflake** — Data warehousing and AI response logging
- **Rill** — Business intelligence and dashboard visualization
- **Braintrust** — AI evaluation and quality scoring
- **Google Chat** — Real-time CSR feedback collection
- **Linear** — Issue tracking and negative feedback triage

[END OF SECTION]

## Results

[START OF SECTION]

After implementation (Q1–Q3 2025), the dashboard delivered measurable impact across three key areas:

| Metric | Result |
|--------|--------|
| AI responses logged in Snowflake | **100%** |
| CSR feedback captured and triaged | **90%** |
| Faster tracking of business goals | **60%** |

**Qualitative Outcomes:**

With the ABC Dashboard, AI moved from being a black box to a transparent, measurable system:

- **CSR Confidence:** Representatives gained confidence in Andi's responses because they could see quality metrics and knew their feedback was being acted upon
- **Leadership Trust:** Executives trusted the metrics and could demonstrate ROI to stakeholders
- **Continuous Improvement Foundation:** The team built a foundation for ongoing AI refinement based on real usage data
- **Proof Over Hope:** Instead of hoping AI would add value, the organization could now prove and refine it with data

The dashboard highlighted training needs and upsell opportunities, giving both reps and leadership proof of real ROI from their AI investment.

[END OF SECTION]

## Related Projects

[START OF SECTION]

Brainforge has delivered similar AI-to-output transformations for other clients:

- **AI Demo Site** — AI assistants built to save time, cut chaos, and move the needle across various industries
- **Ticket Creation Automation** — Automated ticket creation directly from meetings
- **Account Based Marketing Automation** — Fully automated ABM workflow replacing a completely manual process
- **Custom Meeting Tool** — Purpose-built meeting tool developed after commercial apps failed to meet requirements

[END OF SECTION]
