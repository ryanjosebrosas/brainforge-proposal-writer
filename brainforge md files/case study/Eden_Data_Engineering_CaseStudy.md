---
title: "Eden Data Operating System - From Static Spreadsheets to a Live Command Center"
client: "Eden"
industry: "Healthcare"
project_type: "Data_Engineering"
tech_stack: ["BigQuery", "dbt", "Tableau", "Segment", "Mixpanel", "Polytomic", "Braze", "Northbeam"]
function: "Data Analytics"
project_status: "Completed"
metrics:
  - type: "cost_savings"
    value: 20000
    unit: "dollars_per_year"
  - type: "data_accuracy"
    value: 100
    unit: "percent"
  - type: "query_response_time"
    value: 15
    unit: "minutes_or_less"
testimonial: false
team: ["Project Manager", "Product Analyst", "Data Engineer", "Data Analyst"]
duration: "6 months"
location: "Remote / USA-based"
---

# Eden Data Operating System - From Static Spreadsheets to a Live Command Center

## Context

[START OF SECTION]

Eden is a fast-growing telehealth company specializing in personalized metabolic health plans. The company was scaling rapidly across products, channels, and customers, with data spread across more than 20 different tools and platforms. This pace of growth put significant pressure on marketing, operations, and leadership teams to make faster, more confident decisions.

However, with a mix of stakeholders and no clear data ownership, their systems had not kept up with the increasing complexity of their business. Before engaging Brainforge, Eden relied on a combination of brittle spreadsheets and a rigid Electronic Health Record (EMR) system that could not adapt to their evolving needs.

**Data Sources Involved:**
- Northbeam (marketing attribution)
- Google Sheets (manual tracking)
- Typeform (surveys and intake)
- Zendesk (customer support)
- Shippo (shipping/logistics)
- Segment (customer data platform)
- Facebook Ads and Google Ads (paid marketing)

[END OF SECTION]

## Challenge

[START OF SECTION]

With no unified data model, Eden relied on disconnected systems and stale data exports that created multiple operational bottlenecks:

- **Data Fragmentation:** Information scattered across 20+ tools with no single source of truth
- **Delayed Issue Detection:** Problems and delays surfaced only after customer complaints, not proactively
- **Basic Segmentation:** Customer segmentation was rudimentary, limiting personalization and targeting capabilities
- **Locked Operational Data:** Key operational data was trapped in a rigid EMR system that could not be easily queried or integrated
- **Slow Reporting:** Teams waited weeks for reports that should have been available in real-time
- **No Strategic Visibility:** Leadership lacked the full-funnel visibility needed to act quickly or strategically on business metrics

The lack of trustworthy LTV:CAC (Lifetime Value to Customer Acquisition Cost) benchmarks meant Eden could not confidently allocate marketing spend or measure true customer profitability.

[END OF SECTION]

## Solution

[START OF SECTION]

Brainforge built a **data operating system** for Eden: a vendor-proof, tool-agnostic platform designed for speed and clarity. The solution addressed Eden's three core goals:

### 1. Data Consolidation
All marketing, sales, operations, and support data was centralized in **Google BigQuery**, creating a single source of truth. Data was ingested from multiple sources using **Polytomic** and **Segment** for real-time data synchronization.

### 2. Modeled Data Marts
Using **dbt** (data build tool), Brainforge created structured data marts for:
- Sales performance tracking
- Marketing attribution and ROI analysis
- Customer support metrics

These marts power live dashboards in **Tableau** and feed analytics tools like **Mixpanel**.

### 3. Unified Customer Journey
Acquisition, orders, spend, and support data were combined into a single unified customer profile, enabling:
- Full-funnel visibility from first touch to retention
- Accurate LTV:CAC calculations
- Cohort-based analysis

### 4. Activation & Flexibility
The platform enables:
- **Self-serve analytics:** Teams can answer their own questions without waiting for analysts
- **Targeted marketing:** Integrated with **Braze** for personalized campaigns based on unified customer data
- **Vendor-proof architecture:** The EMR-agnostic design means Eden can migrate to a new EMR system without losing their data foundation

![Architecture Diagram](image-placeholder-01.png)
> Architecture diagram showing data flow: Raw Data Sources (Northbeam, Google Sheets, Typeform, Zendesk, Shippo, Segment, Facebook Ads, Google Ads) → Data Ingestion Tools (Google Cloud Functions, Polytomic, Webhooks, Segment) → Data Warehouse (Google BigQuery with dbt transformations, GitHub version control) → Activation (Mixpanel, Tableau, Customer.io, Facebook, Braze for marketing tools)

[END OF SECTION]

## Results

[START OF SECTION]

Eden transformed from slow, reactive reporting to real-time, full-funnel visibility that improved marketing ROI, customer retention, and operational efficiency.

### Key Metrics Achieved:

| Metric | Result |
|--------|--------|
| **Tooling Cost Reduction** | $20,000/year savings |
| **LTV:CAC Benchmark Accuracy** | 100% accurate benchmarks |
| **Data Query Response Time** | <15 minutes to answer common data questions |

### Business Impact:

- **Marketing ROI Optimization:** Trustworthy LTV:CAC and payback benchmarks now give Eden the full story, enabling them to shift spend toward profit and long-term growth
- **Operational Efficiency:** Teams no longer wait weeks for reports—common questions are answered in under 15 minutes
- **Customer Retention:** Full-funnel visibility enables proactive intervention when customers show signs of churn
- **Strategic Decision-Making:** Leadership can now make data-driven decisions in real-time instead of relying on outdated spreadsheet exports
- **Vendor Independence:** The vendor-proof architecture positions Eden for seamless EMR migration without data disruption

[END OF SECTION]

## Tools Used

[START OF SECTION]

| Category | Tools |
|----------|-------|
| **Data Warehouse** | Google BigQuery |
| **Data Transformation** | dbt |
| **Data Ingestion** | Polytomic, Segment, Webhooks |
| **Visualization** | Tableau |
| **Product Analytics** | Mixpanel |
| **Marketing Attribution** | Northbeam |
| **Marketing Automation** | Braze, Customer.io |
| **Version Control** | GitHub |

[END OF SECTION]
