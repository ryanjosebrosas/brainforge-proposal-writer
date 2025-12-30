---
title: "Pool Parts To Go AI Assistant"
client: "Pool Parts To Go (PPTG)"
industry: "E-commerce"
project_type: "AI_ML"
tech_stack: ["OpenAI", "Supabase", "n8n", "AWS", "SerpAPI", "Google Sheets"]
function: "Customer Support"
project_status: "Ongoing"
metrics:
  - type: "time_to_launch"
    value: 2
    unit: "weeks"
  - type: "time_saved"
    value: 20
    unit: "hours_per_week"
  - type: "success_rate"
    value: 90
    unit: "percent"
testimonial: false
team: ["Project Manager", "AI Engineer"]
duration: "Ongoing"
---

# Pool Parts To Go AI Assistant

## Context
[START OF SECTION]
Pool Parts To Go (PPTG) is a national ecommerce brand that sells high-quality, affordable pool equipment to thousands of residential customers across the United States. Many of their customers are non-technical homeowners who need help choosing, installing, or maintaining complex pool equipment.

Without a digital assistant, customers turned to online forums like Reddit or abandoned purchases altogether when they couldn't find reliable answers. PPTG needed a scalable solution that could provide instant, trustworthy guidance on pool chemistry, product fit, and DIY installations without requiring customers to call support.

![AI Assistant Interface Screenshot](image-placeholder-01.png)
> Screenshot showing the PPTG AI assistant (named "Alex") diagnosing a green pool water problem. The interface displays a chat conversation where the assistant identifies an algae problem due to insufficient chlorine levels, unbalanced pH, or malfunctioning filtration. It requests water test results (chlorine level, pH level, alkalinity, cyanuric acid) and provides immediate recommendations: brushing pool walls, checking filtration system, and considering shock treatment.
[END OF SECTION]

## Challenge
[START OF SECTION]
PPTG faced several critical obstacles in serving their customer base effectively:

- **Unreliable External Information**: Forum answers from Reddit and Facebook were often inaccurate, off-brand, or even unsafe for pool maintenance and equipment installation
- **Support Team Scalability**: The existing support team couldn't scale to cover product fit questions, installation issues, and ongoing customer education needs
- **Lost Revenue Opportunities**: Missed context and inadequate guidance led to lost sales, increased product returns, and significant customer frustration
- **Knowledge Gap**: Non-technical homeowners struggled with complex pool chemistry and equipment compatibility without accessible expert guidance

The combination of these challenges meant customers either made uninformed purchases (leading to returns) or abandoned their carts entirely when they couldn't get reliable answers quickly.
[END OF SECTION]

## Solution
[START OF SECTION]
Brainforge built PPTG a branded, always-on AI assistant designed to guide pool owners through product selection, installation processes, and chemistry troubleshooting.

**Core Capabilities:**

1. **Knowledge Base Training**: The assistant was trained on cleaned and customized data from multiple sources including Reddit discussions, Facebook community posts, official product manuals, and installation guides

2. **Visual Troubleshooting**: Supports image uploads for troubleshooting scenarios, enabling step-by-step walkthroughs based on photos of pool equipment or water conditions

3. **Product Intelligence**: Integrated SerpAPI for real-time product lookup and store availability checks, ensuring customers get accurate inventory information

**Technology Stack:**

- **OpenAI** - Core AI/LLM capabilities for natural language understanding and generation
- **Supabase** - Database and backend infrastructure
- **n8n** - Workflow automation and orchestration
- **Amazon S3** - Storage for training data and assets
- **SerpAPI** - Product search and availability lookup
- **Google Sheets** - Data management and analytics tracking

![Tools Used](image-placeholder-02.png)
> Technology logos displayed: OpenAI, Supabase, n8n, Amazon S3, SerpAPI, Google Sheets

**Project Goals:**

- Give customers a faster path to success without relying on Reddit or call center representatives
- Reduce returns and confusion by guiding users through installation flows and compatibility checks
- Build a durable AI layer that scales with PPTG's product catalog and evolving support needs
[END OF SECTION]

## Results
[START OF SECTION]
With a working MVP and comprehensive test coverage, PPTG is primed for full launch. The AI assistant is built to deflect support tickets, drive customer confidence, and guide pool owners at scale.

**Key Metrics Achieved:**

- **Less than 2 weeks** to launch a fully working MVP with search functionality, computer vision capabilities, and analytics tracking
- **20 hours per week** in expected customer service representative time savings once fully deployed
- **90%+ success rate** on installation and chemistry queries compared to forum-sourced answers

The assistant handles complex multi-turn conversations, requests specific water chemistry readings when needed, and provides actionable step-by-step guidance. It successfully addresses common pool problems including algae treatment, chemical balancing, equipment compatibility, and installation procedures.

The solution positions PPTG to scale their customer service capabilities without proportionally scaling headcount, creating a sustainable competitive advantage in the pool equipment ecommerce space.
[END OF SECTION]
