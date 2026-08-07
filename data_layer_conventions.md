# Clean Data Layer Naming Conventions

## Architecture Overview

To eliminate metric drift across Sales, Customer Success, and Operations dashboards, the database layer serves as the single source of truth. All core metrics are encapsulated within standard database views (`vw_`) or served via pre-aggregated summary tables (`agg_`).

---

## Naming Conventions & Standards

### 1. Database Views
- **Prefix:** `vw_`
- **Pattern:** `vw_[business_entity]_[metric_or_context]`
- **Rules:** 
  - Must represent dynamically calculated business metrics.
  - Must encapsulate JOINs and predicate filtering so downstream apps do not rewrite business rules.
- **Examples:**
  - `vw_active_customers` - Encapsulates 30-day active customer counts, revenue, and days since last order.
  - `vw_product_performance` - Encapsulates unit sales, revenue, and customer reach per product catalog item.

### 2. Pre-Aggregated Summary Tables
- **Prefix:** `agg_`
- **Pattern:** `agg_[frequency_grain]_[subject_or_metric]`
- **Rules:**
  - Must explicitly state the aggregation time grain (`daily`, `hourly`, `monthly`).
  - Populated via scheduled background ETL jobs for sub-millisecond dashboard reporting.
- **Examples:**
  - `agg_daily_metrics` - Summarizes total revenue and order counts per calendar day.

### 3. Mandatory Audit & Metadata Columns
Every pre-aggregated table (`agg_`) MUST include the following three standard audit columns:
1. `updated_at` (or `created_at`): Timestamp indicating when the aggregation job ran.
2. `row_count`: Count of raw transactional records aggregated into the summary row (used for audit reconciliation).
3. Grain Column: Explicit time or entity key (`aggregation_date`, `hour_timestamp`, `customer_id`).

---

## Applied Conventions Mapping

| Object Name | Object Type | Grain / Frequency | Business Question Answered |
| :--- | :--- | :--- | :--- |
| **`vw_active_customers`** | SQL View | Customer Level (Dynamic) | *"Which customers are active in the last 30 days and what is their spend?"* |
| **`vw_product_performance`** | SQL View | Product Catalog Item (Dynamic) | *"Which products generate the highest revenue and unit volume?"* |
| **`agg_daily_metrics`** | Pre-Aggregated Table | Daily Calendar Grain | *"What was our total revenue and order count on any given date?"* |

---

## Business & Architectural Benefits

1. **Elimination of Metric Drift:** Business rules (e.g., definition of an "active customer") are maintained in one central database view rather than duplicated across Streamlit, Tableau, or PowerBI dashboards.
2. **Instant Dashboard Query Speeds:** Pre-aggregated tables reduce multi-million row table scans down to simple index lookups executing in **< 1 ms**.
3. **Self-Documenting Codebase:** Developers and data analysts immediately understand an object's type, grain, and purpose directly from its prefix (`vw_` vs `agg_`).

---

## Follow-Up Technical Questions

### Q1: When a view definition changes, do existing dashboards automatically use the new definition? Why or why not?
**Answer:** Yes, existing dashboards automatically adopt the updated business logic immediately on their next query execution. Because dashboards query the view name (`SELECT * FROM vw_active_customers`) rather than hardcoding underlying table joins, any update to the view definition (`CREATE OR REPLACE VIEW`) is transparently evaluated at runtime by the database query engine. No application code changes or redeployments are required.

### Q2: If an aggregated table is computed hourly, what happens to data between refresh cycles? How do you handle real-time metrics?
**Answer:** Data arriving between refresh cycles will not be reflected in `agg_` tables until the next ETL run. For real-time dashboard requirements, a **Lambda / Hybrid View Pattern** is implemented:
```sql
CREATE VIEW vw_realtime_daily_revenue AS
-- Historical closed days from pre-aggregated table
SELECT aggregation_date, metric_value as total_revenue
FROM agg_daily_metrics
WHERE aggregation_date < CURRENT_DATE

UNION ALL

-- Current open day queried dynamically from raw orders table
SELECT DATE(order_date) as aggregation_date, SUM(order_amount) as total_revenue
FROM orders
WHERE order_date >= CURRENT_DATE
GROUP BY DATE(order_date);
```
This architecture preserves sub-millisecond response times for 99% of historical data while providing zero-latency real-time updates for today's active data.

### Q3: How would you test that a view or aggregated table is correct before releasing it to dashboards?
**Answer:** A rigorous 3-step automated validation pipeline is applied:
1. **Row Count & Total Sum Parity Reconciliation:** Compare `SUM(metric_value)` from `agg_daily_metrics` against `SUM(order_amount)` from raw `orders` table to guarantee zero data loss.
2. **Null & Edge Case Checks:** Assert that key dimensions (`customer_id`, `aggregation_date`) contain no unexpected `NULL` values.
3. **Automated Data Diff Regression Testing:** Execute automated SQL assertion scripts (e.g., using `dbt test` or Python `pytest` suites) comparing new view outputs against baseline snapshot datasets before deploying schema changes to production.
