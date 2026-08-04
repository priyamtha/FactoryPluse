-- Table: agg_daily_metrics
-- Purpose: Pre-aggregated daily summary table for fast dashboard reporting
-- Business metric: Aggregated daily revenue, transaction counts, and audit metadata
-- Refresh strategy: Populated periodically via scheduled ETL / background cron jobs
-- Used by: High-traffic Executive Dashboards, Fast Sales Overviews
--
-- Columns:
--   aggregation_date: Calendar date of the metric aggregation grain
--   metric_name: Identifier string for the metric (e.g., 'total_revenue', 'order_count')
--   metric_value: Computed numerical value of the metric
--   row_count: Number of raw transaction rows aggregated into this record
--   updated_at: Timestamp when this aggregation record was calculated

CREATE TABLE IF NOT EXISTS agg_daily_metrics (
    aggregation_date DATE,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    row_count INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (aggregation_date, metric_name)
);

-- Population Query Strategy:
-- INSERT OR REPLACE INTO agg_daily_metrics
-- SELECT 
--     DATE(o.order_date) as aggregation_date,
--     'total_revenue' as metric_name,
--     SUM(o.order_amount) as metric_value,
--     COUNT(*) as row_count,
--     CURRENT_TIMESTAMP as updated_at
-- FROM orders o
-- GROUP BY DATE(o.order_date);
