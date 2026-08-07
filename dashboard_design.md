# Dashboard Design Documentation

## Information Hierarchy Applied

The dashboard layout strictly adheres to the four-level information hierarchy, structuring data from high-level executive summary down to granular operational details:

- **Level 1 (Status): 5 KPI Summary Cards**
  - **Metrics Included:** Revenue ($5.2M | +12.5%), Active Customers (2,500 | +5.2%), Avg Order Value ($145 | +3.1%), Churn Rate (4.8% | -1.2%), NPS Score (72 | +4).
  - **Why Chosen:** Offers an immediate snapshot of top-line growth, customer acquisition, spend expansion, retention health, and brand sentiment. Answers the CEO's primary question: *"Are we on track?"*

- **Level 2 (Trends): 3 Trend Charts**
  - **Revenue Trend (Line Chart):** Illustrates monthly revenue trajectories against a $5.0M monthly target reference line, highlighting a Q3 peak at $5.5M.
  - **Customer Metrics (Dual Line Chart):** Plots Active Customers against Churned Customers on a shared time axis, revealing inverse correlation and validating that acquisition rates exceed customer churn.
  - **Avg Order Value Trend (Line Chart):** Displays steady YTD growth (+9.8%) in basket size towards the target threshold of $140.

- **Level 3 (Segments): Revenue by Segment Comparison Chart**
  - **Chart Type:** Horizontal Bar Chart with formatted data labels ($2.1M, $1.5M, $1.0M, $0.6M).
  - **Insights Revealed:** Enterprise accounts represent 40.4% of total revenue ($2.1M), highlighting Mid-Market as the key expansion engine while Starter accounts require automated onboarding due to lower margins.

- **Level 4 (Detail): Progressive Disclosure Explorer**
  - **Interactive Components:** Sidebar selectbox filters (Customer Segment, Churn Risk Level) and Date Range picker controlling a detailed record data table. Includes CSV download capability (`filtered_data.csv`).

---

## Design Principles Applied

1. **Progressive Disclosure:** Executive summary KPIs are visible immediately at top of page, while granular transactional logs and raw data tables remain hidden under interactive filters at the bottom, reducing cognitive load.
2. **Spatial Organisation:** Placed high-priority macro metrics (Revenue and Active Customers) top-left according to standard F-pattern scanning habits of executive leadership.
3. **Consistent Metaphor:** Maintained color semantics across all visuals:
   - Green (`#2ca02c`): Positive growth, target lines, and favorable churn reduction.
   - Red (`#d62728`): Negative trends, customer churn, and risk alerts.
4. **Context Over Numbers:** Every single metric incorporates evaluative context (period-over-period percentage change, baseline deltas, or green target reference lines).

---

## Colour Palette

- **Primary (`#1f77b4` - Blue):** Core business metrics (Revenue, Active Customers, Enterprise segment).
- **Secondary (`#ff7f0e` - Orange):** Comparison benchmarks, Average Order Value, and Mid-Market segment.
- **Success (`#2ca02c` - Green):** Target lines, positive POP deltas, and SMB segment.
- **Danger (`#d62728` - Red):** Customer churn metrics, negative indicators, and Starter segment.

---

## Target Audience

- **Primary - VP of Sales (Daily User):** Inspects Level 1 KPIs, Level 2 trends, and Level 3 segment breakdowns to monitor pipeline health and revenue distribution.
- **Secondary - CEO (Weekly Glance):** Scans Level 1 KPI cards top-row to answer *"Are we on track?"* in under 10 seconds.
- **Tertiary - Data Analysts (Operational User):** Utilizes Level 4 sidebar filters and CSV data export for deep-dive investigation and ad-hoc SQL validation.

---

## Data Sources

- **KPI Values:** Computed from `vw_monthly_revenue` and `vw_active_customers` views.
- **Trend Data:** Queried from `agg_daily_revenue` aggregated time-series table.
- **Segment Data:** Computed from `vw_customer_segments` view.
