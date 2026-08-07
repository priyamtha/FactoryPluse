"""
SQL Query Optimization Benchmark & Refactoring Suite
---------------------------------------------------
Demonstrates side-by-side performance comparison of analytical SQL queries:
1. Task 1: Removing SELECT * in favor of explicit columns.
2. Task 2: Applying early filtering before JOIN execution.
3. Task 3: Restructuring nested subqueries into modular Common Table Expressions (CTEs).
"""

import sqlite3
import pandas as pd
import time

def run_benchmarks():
    conn = sqlite3.connect('analytics.db')

    print("=================================================================")
    print("Task 1: Refactor Query 1 - SELECT * to Explicit Columns")
    print("=================================================================")
    
    original_query_1 = """
    SELECT *
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    WHERE strftime('%Y', t.transaction_date) = '2024'
    LIMIT 1000;
    """

    optimized_query_1 = """
    SELECT 
        t.transaction_id,     -- Unique ID for transaction tracking
        t.transaction_date,   -- Timestamp for time-series trend analysis
        t.amount,             -- Monetary transaction amount for revenue calculations
        t.customer_id,        -- Foreign key mapping to customer master
        c.customer_name,      -- Customer display identity
        c.country,            -- Regional segmentation analysis
        c.account_type        -- Account tier for revenue grouping
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    WHERE t.transaction_date >= '2024-01-01' AND t.transaction_date <= '2024-12-31'
    LIMIT 1000;
    """

    # Measure Original Query 1
    t0 = time.perf_counter()
    orig_df1 = pd.read_sql(original_query_1, conn)
    t1 = time.perf_counter()
    orig_time1 = (t1 - t0) * 1000

    # Measure Optimized Query 1
    t0 = time.perf_counter()
    opt_df1 = pd.read_sql(optimized_query_1, conn)
    t1 = time.perf_counter()
    opt_time1 = (t1 - t0) * 1000

    orig_cols = orig_df1.shape[1]
    opt_cols = opt_df1.shape[1]
    col_improvement = ((orig_cols - opt_cols) / orig_cols) * 100

    print(f"Original columns returned: {orig_cols} ({orig_time1:.2f} ms)")
    print(f"Optimized columns returned: {opt_cols} ({opt_time1:.2f} ms)")
    print(f"Improvement: {col_improvement:.1f}% fewer columns fetched\n")


    print("=================================================================")
    print("Task 2: Refactor Query 2 - Apply Filters Before JOINs")
    print("=================================================================")

    transactions_count = pd.read_sql("SELECT COUNT(*) as cnt FROM transactions", conn).iloc[0, 0]

    filtered_transactions = pd.read_sql("""
        SELECT COUNT(*) as cnt FROM transactions
        WHERE transaction_date >= '2024-01-01'
          AND amount > 100
    """, conn).iloc[0, 0]

    original_query_2 = """
    SELECT t.transaction_id, t.amount, c.customer_name, p.product_name
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    JOIN products p ON t.product_id = p.id
    WHERE t.transaction_date >= '2024-01-01'
      AND t.amount > 100
      AND c.country = 'USA'
    LIMIT 5000;
    """

    optimized_query_2 = """
    WITH filtered_trans AS (
        SELECT transaction_id, amount, customer_id, product_id
        FROM transactions
        WHERE transaction_date >= '2024-01-01'
          AND amount > 100
    )
    SELECT ft.transaction_id, ft.amount, c.customer_name, p.product_name
    FROM filtered_trans ft
    JOIN customers c ON ft.customer_id = c.id
    JOIN products p ON ft.product_id = p.id
    WHERE c.country = 'USA'
    LIMIT 5000;
    """

    orig_df2 = pd.read_sql(original_query_2, conn)
    opt_df2 = pd.read_sql(optimized_query_2, conn)

    reduction_factor = transactions_count / filtered_transactions

    print(f"Original table: {transactions_count:,} rows")
    print(f"After filter (before join): {filtered_transactions:,} rows ({(filtered_transactions/transactions_count)*100:.1f}%)")
    print(f"Reduction factor: {reduction_factor:.1f}x smaller dataset before joining")
    print(f"Verified row count parity: {len(orig_df2) == len(opt_df2)} ({len(opt_df2)} rows returned)\n")


    print("=================================================================")
    print("Task 3: Refactor Query 3 - Use CTEs for Readability")
    print("=================================================================")

    refactored_query_3 = """
    WITH recent_transactions AS (
        -- Step 1: Filter to recent data within date window
        SELECT transaction_id, amount, customer_id
        FROM transactions
        WHERE transaction_date >= '2024-01-01'
    ),
    customer_with_segment AS (
        -- Step 2: Join filtered transactions to customer segment details
        SELECT 
            rt.transaction_id,
            rt.amount,
            c.customer_segment
        FROM recent_transactions rt
        JOIN customers c ON rt.customer_id = c.id
    ),
    segment_metrics AS (
        -- Step 3: Calculate segment-level aggregation metrics
        SELECT 
            customer_segment,
            COUNT(DISTINCT transaction_id) as transaction_count,
            ROUND(AVG(amount), 2) as avg_transaction_value,
            ROUND(SUM(amount), 2) as total_revenue
        FROM customer_with_segment
        GROUP BY customer_segment
    )
    SELECT 
        customer_segment,
        avg_transaction_value,
        transaction_count,
        total_revenue
    FROM segment_metrics
    ORDER BY avg_transaction_value DESC;
    """

    res3 = pd.read_sql(refactored_query_3, conn)
    print(res3)
    print("\n=== Benchmark Complete ===")

if __name__ == "__main__":
    run_benchmarks()
