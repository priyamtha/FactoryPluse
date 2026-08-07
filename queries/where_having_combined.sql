-- Real-world: filter data quality AND aggregate thresholds
SELECT 
    c.customer_type,
    COUNT(DISTINCT t.customer_id) as segment_customers,
    SUM(t.amount) as segment_revenue,
    ROUND(AVG(t.amount), 2) as avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'      -- WHERE: date range filter (row-level)
  AND t.transaction_status = 'completed'           -- WHERE: payment status check (row-level)
  AND t.amount > 0                                 -- WHERE: positive amount check (row-level)
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 100       -- HAVING: cohort sample size constraint (group-level)
  AND SUM(t.amount) > 100000                       -- HAVING: total business volume threshold (group-level)
ORDER BY segment_revenue DESC;
