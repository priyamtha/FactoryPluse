-- Group by multiple dimensions
SELECT 
    c.customer_type,
    DATE_TRUNC('month', t.transaction_date)::DATE as month,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    COUNT(*) as transaction_count,
    SUM(t.amount) as monthly_revenue,
    AVG(t.amount) as avg_transaction
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'  -- WHERE filters first: reduce dataset size before grouping
GROUP BY c.customer_type, DATE_TRUNC('month', t.transaction_date)
ORDER BY month DESC;
