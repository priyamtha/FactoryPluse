"""
Task 1, 2 & 3: Clean Data Layer Python Query Script
Simulates how Streamlit or executive dashboards query the unified clean data layer.
"""

import sqlite3
import pandas as pd
import time

def execute_sql(sql_statement, conn):
    """Utility helper to execute DDL / DML statements."""
    cursor = conn.cursor()
    cursor.executescript(sql_statement)
    conn.commit()

def run_data_layer():
    conn = sqlite3.connect('analytics.db')

    # Task 1: Create SQL Views
    print("--- Task 1: Creating SQL Views ---")
    
    view1_sql = """
    CREATE VIEW IF NOT EXISTS vw_active_customers AS
    SELECT 
        c.customer_id,
        c.customer_name,
        c.segment,
        COUNT(DISTINCT o.order_id) as order_count_30d,
        COALESCE(SUM(o.order_amount), 0.0) as revenue_30d,
        MAX(o.order_date) as last_order_date,
        CAST(ROUND(julianday('now') - julianday(MAX(o.order_date))) AS INTEGER) as days_since_order
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
        AND o.order_date >= date('now', '-30 days')
    WHERE c.deleted_at IS NULL
    GROUP BY c.customer_id, c.customer_name, c.segment;
    """

    view2_sql = """
    CREATE VIEW IF NOT EXISTS vw_product_performance AS
    SELECT 
        p.id as product_id,
        p.product_name,
        p.category,
        p.price as unit_price,
        COALESCE(SUM(o.quantity), 0) as total_units_sold,
        COALESCE(SUM(o.order_amount), 0.0) as total_product_revenue,
        COUNT(DISTINCT o.customer_id) as unique_purchasers,
        COALESCE(ROUND(AVG(o.order_amount), 2), 0.0) as avg_order_value_per_prod
    FROM products p
    LEFT JOIN orders o ON p.id = o.product_id
    GROUP BY p.id, p.product_name, p.category, p.price;
    """

    execute_sql(view1_sql, conn)
    execute_sql(view2_sql, conn)

    # Confirm view creation
    active_customers = pd.read_sql("SELECT * FROM vw_active_customers LIMIT 10", conn)
    custom_metric = pd.read_sql("SELECT * FROM vw_product_performance LIMIT 10", conn)

    print("View 1 (vw_active_customers) columns:", active_customers.columns.tolist())
    print("View 2 (vw_product_performance) columns:", custom_metric.columns.tolist())


    # Task 2: Pre-Aggregated Summary Table
    print("\n--- Task 2: Creating & Populating Pre-Aggregated Table ---")

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS agg_daily_metrics (
        aggregation_date DATE,
        metric_name VARCHAR(100),
        metric_value NUMERIC,
        row_count INTEGER,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (aggregation_date, metric_name)
    );
    """
    execute_sql(create_table_sql, conn)

    populate_sql = """
    INSERT OR REPLACE INTO agg_daily_metrics (aggregation_date, metric_name, metric_value, row_count, updated_at)
    SELECT 
        DATE(o.order_date) as aggregation_date,
        'total_revenue' as metric_name,
        SUM(o.order_amount) as metric_value,
        COUNT(*) as row_count,
        CURRENT_TIMESTAMP as updated_at
    FROM orders o
    GROUP BY DATE(o.order_date);
    """
    execute_sql(populate_sql, conn)

    agg_data = pd.read_sql("SELECT * FROM agg_daily_metrics ORDER BY aggregation_date DESC LIMIT 10", conn)
    print(f"Aggregated {len(agg_data)} daily metric rows")
    print(agg_data[['aggregation_date', 'metric_name', 'metric_value', 'row_count', 'updated_at']].head())

    # Demonstrate instant query speed against pre-aggregated table
    start = time.time()
    result = pd.read_sql("SELECT metric_name, SUM(metric_value) as total_val FROM agg_daily_metrics GROUP BY metric_name", conn)
    elapsed = time.time() - start
    print(f"Pre-aggregated query time: {elapsed*1000:.2f} ms")


    # Task 3: Querying Views & Pre-Aggregated Tables from Python
    print("\n--- Task 3: Simulating Dashboard Queries ---")

    # Query View 1: Active Customers
    active_cust_df = pd.read_sql("""
        SELECT 
            customer_id, 
            customer_name, 
            revenue_30d,
            days_since_order
        FROM vw_active_customers
        WHERE days_since_order <= 30
        ORDER BY revenue_30d DESC
        LIMIT 10
    """, conn)

    print("\nTop 10 Active Customers (last 30 days):")
    print(active_cust_df)

    # Query View 2: Product Performance Custom Metric
    custom_result = pd.read_sql("""
        SELECT 
            product_id,
            product_name,
            category,
            total_product_revenue,
            total_units_sold
        FROM vw_product_performance
        ORDER BY total_product_revenue DESC
        LIMIT 10
    """, conn)

    print("\nTop 10 Product Performance Results:")
    print(custom_result)

    # Query Pre-Aggregated Table
    agg_result = pd.read_sql("""
        SELECT 
            aggregation_date,
            metric_name,
            metric_value,
            row_count
        FROM agg_daily_metrics
        ORDER BY aggregation_date DESC
        LIMIT 10
    """, conn)

    print("\nDaily Aggregated Metrics (last 10 days):")
    print(agg_result)

    # Demonstrate segment filtering capability
    active_by_segment = pd.read_sql("""
        SELECT 
            segment,
            COUNT(*) as customer_count,
            SUM(revenue_30d) as total_segment_revenue,
            AVG(revenue_30d) as avg_customer_revenue
        FROM vw_active_customers
        GROUP BY segment
        ORDER BY total_segment_revenue DESC
    """, conn)

    print("\nRevenue by Segment Breakdown:")
    print(active_by_segment)

if __name__ == "__main__":
    run_data_layer()
