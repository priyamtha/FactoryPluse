-- Filter GROUPS after aggregation
SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(amount) as annual_revenue
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'
GROUP BY customer_id
HAVING SUM(amount) > 10000                      -- HAVING filters groups: threshold on aggregated annual revenue
  AND COUNT(*) >= 5                             -- HAVING filters groups: threshold on aggregated order frequency
ORDER BY annual_revenue DESC;
