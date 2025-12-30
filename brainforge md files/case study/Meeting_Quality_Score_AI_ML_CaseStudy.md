---
title: "AI Meeting Quality Scoring System"
client: "Brainforge (Internal)"
industry: "Internal Operations"
project_type: "AI_ML"
tech_stack: ["OpenAI", "n8n", "Zoom", "Slack"]
function: "Project Management"
project_status: "Ongoing"
metrics:
  - type: "time_saved"
    value: 3
    unit: "hours_per_week_per_pm"
  - type: "coverage"
    value: 100
    unit: "percent"
location: "Remote / USA-based"
team: ["Project Manager", "AI Engineer"]
testimonial: false
---

# AI Meeting Quality Scoring System

## Context
[START OF SECTION]
Brainforge's internal PM team runs a high volume of high-stakes meetings, both client-facing and internal. However, without quality metrics, outcomes and feedback were unclear, making it hard to know which meetings were worth the time.

The team needed a systematic approach to evaluate meeting effectiveness and identify opportunities to improve or eliminate low-value meetings.
[END OF SECTION]

## Challenge
[START OF SECTION]
Without a structured way to score meeting value, the PM team faced several critical issues:

- PMs couldn't flag low-impact calls before they became permanent fixtures on calendars
- There was no feedback loop to improve meeting quality or cut waste
- Time kept disappearing into recurring meetings that weren't aligned to priorities
- No visibility into which meetings were driving value versus consuming resources
[END OF SECTION]

## Solution
[START OF SECTION]
Brainforge built a Meeting Quality Scoring System—an AI-powered scoring layer integrated inside the existing Zoom summarizer workflow.

**Key Components:**

1. **Scoring in Context:** An AI model (Azure OpenAI) evaluates each meeting on five core dimensions, providing objective quality metrics.

2. **Consistent Measurement:** Clear 0–5 definitions for each scoring category ensure standardized evaluation across all meetings.

3. **Right Where PMs Work:** Scores post directly in the Slack meeting thread alongside the AI summary, eliminating the need to check separate dashboards or reports.

**Technical Architecture:**
- Azure OpenAI powers the natural language analysis and scoring engine
- n8n orchestrates the workflow automation between Zoom, the AI model, and Slack
- Zoom provides meeting transcripts and metadata
- Slack serves as the delivery channel for scores and summaries

![Meeting Quality Score System Architecture](image-placeholder-01.png)
> Visual: Case study infographic showing the workflow from Zoom meetings through AI scoring to Slack delivery, with "At a Glance" metadata panel and Results metrics (3 hrs/wk recovered, 100% meetings scored).
[END OF SECTION]

## Results
[START OF SECTION]
After proof-of-concept deployment, the system delivered measurable improvements:

- **3 hours per week recovered** per PM by removing follow-up "meetings about meetings"
- **100% of PM-led meetings** scored and logged in the system

**Current Status:**
The system is fully deployed in Slack and running on live meetings, with strong adoption potential identified among PMs.

**Future Enhancements Planned:**
- Automatic alerts for low-scoring meetings
- Historical dashboards to track meeting quality trends over time
- Expanded scoring dimensions based on team feedback
[END OF SECTION]

## Tools Used
[START OF SECTION]
| Tool | Purpose |
|------|---------|
| OpenAI (Azure) | AI-powered meeting analysis and scoring engine |
| n8n | Workflow orchestration and automation |
| Zoom | Meeting platform and transcript source |
| Slack | Score and summary delivery channel |
[END OF SECTION]
