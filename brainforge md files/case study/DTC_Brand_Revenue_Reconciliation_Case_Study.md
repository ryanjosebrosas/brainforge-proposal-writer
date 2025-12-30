---
title: "Revenue Reconciliation Dashboard for DTC Brand"
client: "DTC Brand"
industry: "E-commerce"
project_type: "BI_Analytics"
tech_stack: ["Snowflake", "dbt", "Tableau", "Metabase", "Fivetran", "Google Sheets", "Shopify"]
function: "Finance"
project_status: "Completed"
metrics:
  - type: "revenue_accuracy"
    value: 25
    unit: "percent_gaps_fixed"
  - type: "cost_reporting_accuracy"
    value: 42
    unit: "percent_corrected"
  - type: "cohort_margin_reporting"
    value: 100
    unit: "percent_live"
testimonial: false
team: ["Project Manager", "Analyst"]
duration: "6 months"
organization_size: "Medium Enterprise"
location: "Remote / USA-based"
---

# Revenue Reconciliation Dashboard for DTC Brand

[START OF SECTION]
## Context

A mid-sized DTC brand relied on Amplitude for finance reporting, but broken pipelines led to inflated revenue, mismatched discounts, and stalled margin analysis. Discrepancies across Shopify, Amplitude, and ERP created reporting gaps, while fragile event-based tracking couldn't scale. The finance team lacked confidence, leadership lost trust, and a full rebuild wasn't an option—they needed clarity without starting from scratch.
[END OF SECTION]

[START OF SECTION]
## Challenge

Without a reliable data model or single source of truth, the finance team couldn't trust the numbers. Revenue looked inflated, margins were unclear, and key decisions stalled. Misaligned data across Shopify, Amplitude, and the ERP made it hard to reconcile costs and discounts. With broken cohort logic and disconnected priorities between BI and Finance, dashboards went unused and trust eroded.

Key issues included:
- No single source of truth for financial data
- Revenue figures appeared inflated due to broken pipelines
- Margins were unclear and unverifiable
- Cost and discount reconciliation was unreliable
- Cohort logic was broken
- Disconnect between BI team and Finance priorities
- Existing dashboards were unused due to lack of trust
[END OF SECTION]

[START OF SECTION]
## Solution

The Brainforge team deployed a warehouse-first setup, giving finance full control over reporting, costs, and cohorts—without requiring a full platform rebuild.

**Technical Implementation:**

1. **Data Modeling:** Shopify data modeled in dbt with clean, repeatable logic
2. **Real-Time Sync:** Google Sheets synced for real-time updates and accessibility
3. **Dashboard Development:** Dashboards built from item- and order-level data by product and funnel

**Technologies Used:**
- **Data Warehouse:** Snowflake
- **Data Transformation:** dbt
- **Data Ingestion:** Fivetran
- **Visualization:** Tableau, Metabase
- **Real-Time Collaboration:** Google Sheets
- **Source Systems:** Shopify, Amplitude

![Case Study Overview](image-placeholder-01.png)
> Image description: Brainforge case study layout showing project metadata, team photos (Project Manager and Analyst), and tool logos including Amplitude, Snowflake, Metabase, Fivetran, dbt, Tableau, and Shopify.
[END OF SECTION]

[START OF SECTION]
## Results

The new reporting system became the single source of truth for Finance. With trusted numbers, better visibility, and repeatable logic, it's now core to margin tracking and planning.

**Quantified Outcomes:**

| Metric | Improvement |
|--------|-------------|
| Revenue gaps fixed | 25% |
| Shipping cost reporting corrected | 42% |
| Cohort margin reporting live | 100% |

**Business Impact:**
- Finance team now has confidence in reported numbers
- Leadership trust restored through reliable, repeatable reporting
- Margin tracking and planning enabled without full platform rebuild
- Single source of truth established across previously siloed systems
[END OF SECTION]
