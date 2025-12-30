---
title: "From Sprawl to Signal: UrbanStems' BI Reset"
client: "UrbanStems"
industry: "E-commerce"
project_type: "BI_Analytics"
tech_stack: ["Amazon Redshift", "Looker", "dbt"]
function: "Data Analytics"
project_status: "Completed"
metrics:
  - type: "dashboard_reduction"
    value: 88
    unit: "percent"
  - type: "assets_eliminated"
    value: 741
    unit: "dashboards"
  - type: "trusted_assets_retained"
    value: 95
    unit: "dashboards"
testimonial: false
team: ["Project Manager", "Data Engineer"]
duration: "7 months"
location: "USA"
---

# From Sprawl to Signal: UrbanStems' BI Reset

[START OF SECTION]
## Context

UrbanStems, a fast-growing direct-to-consumer (DTC) flower company, had accumulated over 800 Looker assets with little pruning or governance. Stale logic and unclear ownership left analysts wasting time chasing the "right" numbers. The lack of documentation and asset management created an environment where finding reliable data became increasingly difficult as the company scaled.

[END OF SECTION]

[START OF SECTION]
## Challenge

Instead of clarity, teams faced dashboard sprawl, duplicate reports, and conflicting KPIs that slowed decisions. Critical workflows like inventory management, audits, and risk reviews dragged under the weight of BI chaos and second-guessing. Key pain points included:

- **836+ unmanaged Looker assets** with no clear ownership or maintenance schedule
- **Duplicate and conflicting reports** causing confusion across teams
- **Stale logic** embedded in dashboards producing unreliable metrics
- **Slow decision-making** as analysts spent excessive time hunting for the "right" numbers
- **No governance framework** to prevent future asset sprawl

[END OF SECTION]

[START OF SECTION]
## Solution

Brainforge led a Looker de-bloat and ETL hygiene sprint to reset the system. The approach included three core workstreams:

### Full Audit + Deprecation Rules
Scored each asset by usage, ownership, health, and activity to create an objective framework for retention decisions.

### Establish Decision Layer
Implemented clear criteria to keep recent and healthy assets while cutting stale or unused ones. This created a defensible, repeatable process for ongoing governance.

### Reorganized Catalog
Regrouped the remaining 95 dashboards into a trusted library with clear naming conventions, ownership tags, and documentation.

**Technologies Used:**
- **Amazon Redshift** — Data warehouse infrastructure
- **Looker** — Business intelligence platform (target of cleanup)
- **dbt** — Data transformation and ETL hygiene

![Tools Used](image-placeholder-01.png)
> Visual reference: Logos for Amazon Redshift, Looker, and dbt representing the core technology stack.

[END OF SECTION]

[START OF SECTION]
## Results

After 7 months of implementation:

- **88% dashboard reduction** — Assets cut from 836 to 95 trusted dashboards
- **741 stale assets deprecated** — Eliminated duplicate, broken, and unused reports
- **Trusted catalog established** — 95 dashboards regrouped into an organized, governed library
- **Reduced data risk** — Clean semantic layer minimizes conflicting KPIs
- **Foundation for AI copilots** — The cleanup created the semantic layer needed for guided workflows and AI-assisted analytics

UrbanStems analysts now move faster with a trusted catalog, spending less time hunting and more time analyzing. The cleanup not only reduced data risk but also created the foundation for AI copilots and guided workflows built on a clean semantic layer.

![Results Visualization](image-placeholder-02.png)
> Visual reference: Bar chart showing dashboard reduction from 836 to 95, representing 88% decrease.

[END OF SECTION]

[START OF SECTION]
## Related Case Studies

- CDP Tool Comparison Diagram
- Vita Coco Gains 900+ Store Stockout Visibility
- 2-Week Turnaround for Amazon BI Dashboards

[END OF SECTION]
