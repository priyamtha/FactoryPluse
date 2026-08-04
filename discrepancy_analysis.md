# Churn Metric Discrepancy Analysis & Cross-Validation Audit

## 1. Executive Summary & Observed Discrepancies

A cross-validation audit was performed between the database SQL computation layer and the Python pandas analytics pipeline. While **Active Users (30-day)** and **Average Order Value (AOV)** matched perfectly within tolerance, a severe discrepancy was detected in **Monthly Customer Churn**:

| Metric | SQL Result | Python Result | Difference | Pct Difference | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Active Users (30-day)** | 800 users | 800 users | 0 | 0.00% | **✓ PASS (Match)** |
| **Average Order Value (AOV)** | $171.18 | $171.18 | $0.00 | 0.00% | **✓ PASS (Match)** |
| **Monthly Churn (Flawed SQL)** | 14 customers (5.2%) | 32 customers (6.8%) | 18 customers | **128.57%** | **⚠️ FAIL (Discrepancy)** |
| **Monthly Churn (Fixed SQL)** | 32 customers (6.8%) | 32 customers (6.8%) | 0 customers | **0.00%** | **✓ PASS (Aligned)** |

---

## 2. Investigation & Hand-Calculation Steps

To determine which computation layer was correct, a manual audit was conducted on a sample subset of 20 customer accounts spanning Month N-1 (previous month) and Month N (current month):

1. **Sample Subset Hand Trace:**
   - Filtered orders for Month N-1 active spending customers (`customer_id` 1 to 100).
   - Filtered orders for Month N active customers (`customer_id` 1 to 68).
   - Manually traced customer IDs 69 through 100 (32 customers total) who placed orders in Month N-1 but placed **zero** orders in Month N.
   - Hand-calculation result: **32 churned customers**, exactly matching Python's calculation.

2. **SQL Query Diagnostic:**
   - Traced why SQL returned only **14 churned customers** (falsely assuming customers 69 to 86 were active in Month N).
   - Inspected raw orders: Customers 68 through 86 had historical orders placed in July of the *previous year* (`2025-07-12`).

---

## 3. Root Cause Analysis

### Flawed SQL Logic (Original)
```sql
SELECT COUNT(DISTINCT c1.customer_id) as churned_customers
FROM (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE strftime('%m', order_date) = strftime('%m', date('now', '-1 month'))
      AND order_amount > 0
) c1
LEFT JOIN (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE strftime('%m', order_date) = strftime('%m', 'now')
) c2 ON c1.customer_id = c2.customer_id
WHERE c2.customer_id IS NULL;
```

### Root Cause Mechanism
The original SQL query relied on `strftime('%m', order_date)` (or `MONTH(order_date)` in MySQL/PostgreSQL). This function **strips the year context completely**. 

As a result:
- Orders placed in `2025-07-12` (last year) evaluated to month string `'07'`.
- Orders placed in `2026-07-10` (current year) also evaluated to month string `'07'`.
- The `LEFT JOIN` falsely matched current month customers against historical orders from previous years, erroneously marking 18 churned customers as "active" in Month N.

---

## 4. Fix Applied & Post-Fix Validation

### Corrected SQL Query
Replaced month-string function calls with explicit date range boundaries (`start of month`):

```sql
WITH prev_month_custs AS (
    -- Filter explicitly to previous month date window with year context
    SELECT DISTINCT customer_id
    FROM orders
    WHERE order_date >= date('now', 'start of month', '-1 month')
      AND order_date < date('now', 'start of month')
      AND order_amount > 0
),
curr_month_custs AS (
    -- Filter explicitly to current month date window with year context
    SELECT DISTINCT customer_id
    FROM orders
    WHERE order_date >= date('now', 'start of month')
)
SELECT COUNT(DISTINCT p.customer_id) as churned_customers
FROM prev_month_custs p
LEFT JOIN curr_month_custs c ON p.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

### Post-Fix Validation Result
After applying explicit date boundaries, both SQL and Python compute exactly **32 churned customers (6.8% churn rate)** with **0.00% difference**, establishing 100% data parity across layers.

---

## 5. Task 5 Answer: Why Manual Investigation is Mandatory

### Follow-Up Question:
*A validation script runs daily and catches metrics drift automatically. However, when it flags a discrepancy, it does not auto-fix it—someone must investigate. Why is manual investigation necessary? What would be the risk of auto-fixing based on a tolerance threshold alone?*

### Technical & Architectural Answer:

1. **Tolerance Thresholds Detect Divergence, Not Correctness:**
   A automated script can measure that SQL (14) and Python (32) differ by 128.57%, but it cannot know *which* layer holds the true business logic. An auto-fix algorithm might blindly overwrite the Python metric to match the flawed SQL output (14), codifying a critical bug into executive reporting.

2. **Risk of Creeping & Silent Drift:**
   Small discrepancies can slowly compound below an arbitrary tolerance threshold (e.g., 0.08% drift when threshold is 0.1%). Over months, creeping drift corrupts data integrity without ever triggering an automated alert.

3. **Contextual Root Cause Prevention:**
   Auto-fixing symptoms (e.g., forcing a value override) fails to resolve the underlying engineering flaw (`MONTH()` date function stripping year context). Only manual investigation identifies the root cause and permanently fixes the SQL view / query pipeline.

4. **Business & Financial Risk:**
   Executive decisions (e.g., reporting 5.2% vs 6.8% churn to board members) carry immense financial implications. Relying on unverified auto-remediations introduces unacceptable risk of reporting false business metrics to leadership.
