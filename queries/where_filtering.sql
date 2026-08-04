-- Filter data quality issues BEFORE grouping
SELECT 
    customer_id,
    SUM(amount) as annual_revenue,
    COUNT(*) as transaction_count
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'  -- Date range filter: focus on 2024 onwards
  AND amount > 0                              -- Remove refunds: only positive sales volume
  AND transaction_status = 'completed'        -- Valid transactions only: filter out errors/failures
GROUP BY customer_id
ORDER BY annual_revenue DESC;
