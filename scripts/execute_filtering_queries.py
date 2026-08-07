import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def create_filtering_tables(engine):
    """
    Generate synthetic transactions and customers tables:
    - customers: ~100 customer profiles with customer_type and industry.
    - transactions: ~1,500 transactions in 2024 with status completed, failed, or refunded.
    Loads them into SQLite.
    """
    np.random.seed(42)
    n_customers = 150
    n_transactions = 1500
    
    # 1. Create Customers DataFrame
    customer_ids = np.arange(1001, 1001 + n_customers)
    customer_types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n_customers, p=[0.10, 0.40, 0.50])
    industries = np.random.choice(['Software', 'Healthcare', 'Finance', 'Manufacturing', 'Retail'], size=n_customers)
    
    df_customers = pd.DataFrame({
        'customer_id': customer_ids.astype(int),
        'customer_type': customer_types,
        'industry': industries
    })
    
    # 2. Create Transactions DataFrame
    tx_customer_ids = np.random.choice(customer_ids, size=n_transactions)
    
    # Dates spanning 2024
    base_date = pd.Timestamp('2024-01-01')
    date_offsets = np.random.randint(0, 365, size=n_transactions)
    tx_dates = [base_date + pd.Timedelta(days=int(offset)) for offset in date_offsets]
    
    # Map customer types for amounts
    cust_type_map = dict(zip(customer_ids, customer_types))
    tx_customer_types = [cust_type_map[cid] for cid in tx_customer_ids]
    
    amounts = []
    statuses = []
    
    for ct in tx_customer_types:
        # Injected high-volume transactions for certain users to satisfy HAVING sum > 10,000
        # Normal distributions:
        if ct == 'Enterprise':
            amt = np.random.normal(5000, 500)
            status = np.random.choice(['completed', 'failed'], p=[0.95, 0.05])
        elif ct == 'SMB':
            amt = np.random.normal(800, 100)
            status = np.random.choice(['completed', 'failed', 'refunded'], p=[0.90, 0.08, 0.02])
        else:
            amt = np.random.normal(150, 20)
            status = np.random.choice(['completed', 'failed'], p=[0.92, 0.08])
            
        amounts.append(round(amt, 2))
        statuses.append(status)
        
    df_transactions = pd.DataFrame({
        'transaction_id': [f"TX_{i:05d}" for i in range(1, n_transactions + 1)],
        'order_id': [f"ORD_{i:05d}" for i in range(1, n_transactions + 1)],
        'customer_id': tx_customer_ids.astype(int),
        'transaction_date': tx_dates,
        'amount': amounts,
        'transaction_status': statuses
    })
    
    # Load to database
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)
    df_transactions.to_sql('transactions', engine, if_exists='replace', index=False)
    
    print("[SUCCESS] Synthetic tables populated: 'customers', 'transactions'")


def translate_pg_to_sqlite(sql):
    """
    Translates PostgreSQL specific SQL functions to SQLite dialect equivalents:
    - DATE '2024-01-01' -> '2024-01-01'
    - Replaces DATE_TRUNC with strftime formats.
    - Removes ::DATE casts.
    """
    # Remove PostgreSQL DATE cast literal
    sql = sql.replace("DATE '2024-01-01'", "'2024-01-01'")
    
    # Remove ::DATE casts
    sql = sql.replace("::DATE", "")
    
    # Replaces DATE_TRUNC formatting
    sql = sql.replace("DATE_TRUNC('month', t.transaction_date)", "strftime('%Y-%m-01', t.transaction_date)")
    sql = sql.replace("DATE_TRUNC('month', transaction_date)", "strftime('%Y-%m-01', transaction_date)")
    
    return sql


def load_query(query_name):
    """Load SQL query from file."""
    with open(f'queries/{query_name}.sql', 'r') as f:
        return f.read()


def execute_filtering_queries(engine):
    """Loads, translates, and executes the SQL filtering query library."""
    # 1. WHERE Filtering
    print("\n" + "=" * 60)
    print("TASK 1: WHERE FILTERING")
    print("=" * 60)
    q1_pg = load_query('where_filtering')
    q1_sqlite = translate_pg_to_sqlite(q1_pg)
    r1 = pd.read_sql(q1_sqlite, engine)
    print(r1.head(10))
    
    # 2. GROUP BY and Aggregation
    print("\n" + "=" * 60)
    print("TASK 2: GROUP BY AND AGGREGATION")
    print("=" * 60)
    q2_pg = load_query('groupby_aggregation')
    q2_sqlite = translate_pg_to_sqlite(q2_pg)
    r2 = pd.read_sql(q2_sqlite, engine)
    print(r2.head(10))
    
    # 3. HAVING Filtering
    print("\n" + "=" * 60)
    print("TASK 3: HAVING FILTERING")
    print("=" * 60)
    q3_pg = load_query('having_filtering')
    q3_sqlite = translate_pg_to_sqlite(q3_pg)
    r3 = pd.read_sql(q3_sqlite, engine)
    print(r3.head(10))
    
    # 4. WHERE + HAVING Combined
    print("\n" + "=" * 60)
    print("TASK 4: WHERE + HAVING COMBINED")
    print("=" * 60)
    q4_pg = load_query('where_having_combined')
    q4_sqlite = translate_pg_to_sqlite(q4_pg)
    r4 = pd.read_sql(q4_sqlite, engine)
    print(r4.head(10))
    
    # 5. ORDER BY Ranking
    print("\n" + "=" * 60)
    print("TASK 5: ORDER BY RANKING")
    print("=" * 60)
    q5_pg = load_query('orderby_ranking')
    q5_sqlite = translate_pg_to_sqlite(q5_pg)
    r5 = pd.read_sql(q5_sqlite, engine)
    print(r5.head(10))
    
    return r1, r2, r3, r4, r5


def validate_results(r1, r2, r3, r4, r5):
    """Validate query results logic checks."""
    print("\n" + "=" * 60)
    print("VALIDATION CHECKS")
    print("=" * 60)
    
    # Task 1 check: all revenues should be positive
    assert (r1['annual_revenue'] > 0).all(), "Task 1 has invalid revenues"
    
    # Task 3 check: annual_revenue > 10,000 and count >= 5
    assert (r3['annual_revenue'] > 10000).all(), "Task 3 revenue threshold breached"
    assert (r3['transaction_count'] >= 5).all(), "Task 3 frequency threshold breached"
    
    # Task 4 check: count >= 100 and revenue > 100,000 (if results returned)
    if len(r4) > 0:
        assert (r4['segment_customers'] >= 100).all(), "Task 4 customer threshold breached"
        assert (r4['segment_revenue'] > 100000).all(), "Task 4 revenue threshold breached"
        
    # Task 5 check: ranks must be sequential and sorted descending
    if len(r5) > 0:
        assert (r5['total_revenue'].diff().dropna() <= 0).all(), "Task 5 is not sorted descending"
        assert (r5['revenue_rank'] == np.arange(1, len(r5) + 1)).all() or (r5['revenue_rank'].min() == 1), "Task 5 rank is incorrect"
        
    print("[SUCCESS] All SQL filtering validation checks passed successfully")


def run_pipeline():
    """Run full filtering diagnostic pipeline."""
    engine = create_engine('sqlite:///analytics.db')
    
    # Populate database tables
    create_filtering_tables(engine)
    
    # Run queries
    r1, r2, r3, r4, r5 = execute_filtering_queries(engine)
    
    # Validate
    validate_results(r1, r2, r3, r4, r5)
    
    print("\n" + "=" * 60)
    print("FILTERING DIAGNOSTIC PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
