-- =================================================================
-- Task 3: Refactor Query 3 - Use CTEs for Readability
-- =================================================================

-- -----------------------------------------------------------------
-- Inefficient Original Query (3-level deeply nested subqueries)
-- -----------------------------------------------------------------
SELECT customer_segment, AVG(revenue_per_transaction) as avg_transaction_value
FROM (
    SELECT 
        c.customer_segment,
        AVG(t.amount) as revenue_per_transaction,
        COUNT(DISTINCT t.transaction_id) as transaction_count
    FROM (
        SELECT t.transaction_id, t.amount, t.customer_id
        FROM transactions t
        WHERE t.transaction_date >= '2024-01-01'
    ) t
    JOIN customers c ON t.customer_id = c.id
    GROUP BY c.customer_segment
) grouped
ORDER BY avg_transaction_value DESC;


-- -----------------------------------------------------------------
-- Refactored Query (Modular, Testable Common Table Expressions - CTEs)
-- -----------------------------------------------------------------
WITH recent_transactions AS (
    -- Step 1: Filter to recent transaction data within target time window
    SELECT transaction_id, amount, customer_id
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
),
customer_with_segment AS (
    -- Step 2: Join filtered transactions to customer segment master
    SELECT 
        rt.transaction_id,
        rt.amount,
        c.customer_segment
    FROM recent_transactions rt
    JOIN customers c ON rt.customer_id = c.id
),
segment_metrics AS (
    -- Step 3: Compute segment-level aggregated KPIs
    SELECT 
        customer_segment,
        COUNT(DISTINCT transaction_id) as transaction_count,
        AVG(amount) as avg_transaction_value,
        SUM(amount) as total_revenue
    FROM customer_with_segment
    GROUP BY customer_segment
)
SELECT 
    customer_segment,
    ROUND(avg_transaction_value, 2) as avg_transaction_value,
    transaction_count,
    ROUND(total_revenue, 2) as total_revenue
FROM segment_metrics
ORDER BY avg_transaction_value DESC;
