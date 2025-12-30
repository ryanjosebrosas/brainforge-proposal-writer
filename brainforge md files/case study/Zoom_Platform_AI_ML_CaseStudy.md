---
title: "The Source of Truth for Every Meeting"
client: "Brainforge (Internal)"
industry: "SaaS"
project_type: "AI_ML"
tech_stack: ["OpenAI", "n8n", "Supabase", "Windmill", "AWS", "Python", "Zoom"]
function: "Operations"
project_status: "Completed"
metrics:
  - type: "context_pings_reduction"
    value: 70
    unit: "percent"
  - type: "time_saved"
    value: 40
    unit: "hours_per_month"
  - type: "adoption_rate"
    value: 100
    unit: "percent"
testimonial: false
team: ["Project Mgr", "AI Engineer", "AI Engineer", "AI Engineer"]
duration: "2 months"
location: "Remote / USA-based"
---

# The Source of Truth for Every Meeting

## Context
[START OF SECTION]
Brainforge's async team relied on Zoom for decisions, but those conversations quickly got buried. Transcripts were scattered across Slack, Notion, and inboxes—and Zoom's built-in recordings were rarely touched or reused. Valuable knowledge was getting lost, and repeat work crept in.

The team needed a centralized, AI-searchable source of truth that could turn every Zoom meeting into accessible knowledge without adding new tools or licenses. The goal was to auto-ingest recordings, summarize key moments, and let teammates ask questions like "What did we decide on pricing last month?" The platform would become the go-to knowledge hub for leadership, product, and ops teams.
[END OF SECTION]

## Challenge
[START OF SECTION]
Leadership kept getting pinged for repeat context. Finding past decisions meant chasing Slack threads or rewatching full meetings—a time-consuming and frustrating process. Previous attempts to fix this with Slack-based AI agents failed due to low adoption.

Key pain points included:

- Endless cycle of Slack ping-pong, repeated questions, and buried meeting notes
- No reliable way to turn raw Zoom recordings into trusted, searchable knowledge
- Leadership context was inaccessible without slowing them down
- External tools required new licenses and created adoption friction

What the team needed was simple: a private, reliable way to find past decisions fast.
[END OF SECTION]

## Solution
[START OF SECTION]
Brainforge built a streamlined, private interface that auto-ingests Zoom recordings and unlocks instant meeting recall. The solution combined several technologies into a cohesive platform:

**Data Ingestion Pipeline:**
Auto-recorded Zoom calls are pulled into Amazon S3 and summarized via Python workflows in Windmill. This creates an automated pipeline that requires no manual intervention.

**Knowledge Storage:**
Transcripts and metadata are stored in Supabase, making them searchable via natural language queries. The database structure supports fast retrieval and context-aware search.

**User Interface:**
A custom chat interface mimics the familiar Zoom experience but adds context-aware search across Slack and meeting history. Users can ask questions and get instant answers from past meetings.

![Platform Interface Screenshot](image-placeholder-01.png)
> Screenshot showing the platform interface with two panels: a meeting details view on the left (showing participants, recording info, and summary/transcript tabs) and an AI Meeting Assistant chat interface on the right where users can ask questions about meeting content and get summarized decisions.

**Tools Used:**
- OpenAI for natural language processing and summarization
- n8n for workflow automation
- Supabase for transcript and metadata storage
- Windmill for Python workflow orchestration
- Amazon S3 for recording storage
- Zoom API for recording ingestion
[END OF SECTION]

## Results
[START OF SECTION]
After 2 months of implementation, the platform achieved remarkable results:

- **70% decrease** in context pings to leadership
- **40+ hours per month saved** in manual meeting review
- **100% adoption** within 3 weeks of launch

Now the team gets meeting answers in seconds. No downloads, no chasing links, no second-guessing, and no more asking leadership for the same context twice.

The platform has become the go-to knowledge hub for leadership, product, and operations teams—delivering on the original promise of turning every Zoom meeting into a trusted, AI-searchable source of truth.
[END OF SECTION]

## Goals Achieved
[START OF SECTION]
The project successfully met all three original objectives:

1. **Ended the cycle of Slack ping-pong** — Repeated questions and buried meeting notes are now a thing of the past
2. **Transformed raw Zoom recordings** — Meetings are now trusted, searchable knowledge without relying on external tools
3. **Made leadership context accessible** — Information is available instantly without slowing down executives
[END OF SECTION]
