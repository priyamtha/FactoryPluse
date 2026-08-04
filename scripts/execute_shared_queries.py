import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def create_synthetic_tables(engine):
    """
    Generate synthetic transactions, customers, and users tables:
    1. transactions: ~1,000 orders over the past 12 months.
    2. customers: ~500 customer profiles.
    3. users: ~1,000 signups over the last 90 days.
    Loads them into SQLite.
    """
    np.random.seed(42)
    n_customers = 500
    n_transactions = 1000
    n_users = 1000
    
    # 1. Create Customers DataFrame
    customer_ids = np.arange(1001, 1001 + n_customers)
    customer_types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n_customers, p=[0.05, 0.40, 0.55])
    df_customers = pd.DataFrame({
        'customer_id': customer_ids.astype(int),
        'customer_type': customer_types
    })
    
    # 2. Create Transactions DataFrame
    tx_customer_ids = np.random.choice(customer_ids, size=n_transactions)
    # Map customer types for transactions (needed for query 1 filter aggregate)
    cust_type_map = dict(zip(customer_ids, customer_types))
    tx_customer_types = [cust_type_map[cid] for cid in tx_customer_ids]
    
    # Dates spread over last 12 months (365 days)
    now = pd.Timestamp.now().normalize()
    tx_offsets = np.random.randint(0, 365, size=n_transactions)
    tx_dates = [now - pd.Timedelta(days=int(offset)) for offset in tx_offsets]
    
    # Amounts based on customer type
    amounts = []
    for ct in tx_customer_types:
        if ct == 'Enterprise':
            amt = np.random.normal(1000, 100)
        elif ct == 'SMB':
            amt = np.random.normal(90, 10)
        else:
            amt = np.random.normal(30, 5)
        amounts.append(round(max(amt, 5.0), 2))
        
    df_transactions = pd.DataFrame({
        'transaction_id': [f"TX_{i:05d}" for i in range(1, n_transactions + 1)],
        'order_id': [f"ORD_{i:05d}" for i in range(1, n_transactions + 1)],
        'customer_id': tx_customer_ids.astype(int),
        'transaction_date': tx_dates,
        'amount': amounts,
        'customer_type': tx_customer_types
    })
    
    # 3. Create Users DataFrame (daily funnels over last 90 days)
    user_offsets = np.random.randint(0, 90, size=n_users)
    created_dates = [now - pd.Timedelta(days=int(offset)) for offset in user_offsets]
    
    email_verified_dates = []
    first_purchase_dates = []
    
    for c_date in created_dates:
        # 80% verify email within 0 to 2 days
        verified = np.random.choice([True, False], p=[0.80, 0.20])
        if verified:
            v_offset = np.random.randint(0, 3)
            v_date = c_date + pd.Timedelta(days=v_offset)
            email_verified_dates.append(v_date)
            
            # 50% of verified users buy something within 0 to 5 days
            purchased = np.random.choice([True, False], p=[0.50, 0.50])
            if purchased:
                p_offset = np.random.randint(0, 6)
                p_date = v_date + pd.Timedelta(days=p_offset)
                first_purchase_dates.append(p_date)
            else:
                first_purchase_dates.append(None)
        else:
            email_verified_dates.append(None)
            first_purchase_dates.append(None)
            
    df_users = pd.DataFrame({
        'user_id': [f"USR_{i:05d}" for i in range(1, n_users + 1)],
        'created_at': created_dates,
        'email_verified_at': email_verified_dates,
        'first_purchase_at': first_purchase_dates
    })
    
    # Load to database
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)
    df_transactions.to_sql('transactions', engine, if_exists='replace', index=False)
    df_users.to_sql('users', engine, if_exists='replace', index=False)
    
    print("[SUCCESS] Synthetic database tables populated: 'customers', 'transactions', 'users'")


# ---------------------------------------------------------
# TASK 4: Call Queries from Python (1 mark)
# ---------------------------------------------------------
def translate_pg_to_sqlite(sql):
    """
    Translates PostgreSQL specific SQL functions to SQLite dialect equivalents:
    - Removes casts (::DATE).
    - Replaces DATE_TRUNC with strftime formats.
    - Replaces NOW() and intervals with SQLite date modifiers.
    - Replaces FILTER (WHERE c) with CASE WHEN.
    """
    # Remove casts
    sql = sql.replace("::DATE", "")
    
    # Replaces DATE_TRUNC date formatting
    sql = sql.replace("DATE_TRUNC('month', transaction_date)", "strftime('%Y-%m-01', transaction_date)")
    sql = sql.replace("DATE_TRUNC('month', t.transaction_date)", "strftime('%Y-%m-01', t.transaction_date)")
    sql = sql.replace("DATE_TRUNC('day', u.created_at)", "strftime('%Y-%m-%d', u.created_at)")
    
    # Replaces NOW() offsets
    sql = sql.replace("DATE_TRUNC('month', NOW()) - INTERVAL '12 months'", "date('now', '-12 months', 'start of month')")
    sql = sql.replace("NOW() - INTERVAL '90 days'", "date('now', '-90 days')")
    
    # Replaces FILTER clauses with CASE WHEN aggregation
    sql = sql.replace(
        "COUNT(DISTINCT customer_id) FILTER (WHERE customer_type='Enterprise')",
        "COUNT(DISTINCT CASE WHEN customer_type='Enterprise' THEN customer_id END)"
    )
    sql = sql.replace(
        "COUNT(DISTINCT customer_id) FILTER (WHERE customer_type='SMB')",
        "COUNT(DISTINCT CASE WHEN customer_type='SMB' THEN customer_id END)"
    )
    sql = sql.replace(
        "COUNT(*) FILTER (WHERE u.email_verified_at IS NOT NULL)",
        "SUM(CASE WHEN u.email_verified_at IS NOT NULL THEN 1 ELSE 0 END)"
    )
    sql = sql.replace(
        "COUNT(*) FILTER (WHERE u.first_purchase_at IS NOT NULL)",
        "SUM(CASE WHEN u.first_purchase_at IS NOT NULL THEN 1 ELSE 0 END)"
    )
    
    return sql


def load_query(query_name):
    """Load SQL query from file."""
    with open(f'queries/{query_name}.sql', 'r') as f:
        return f.read()


def execute_queries(engine):
    """Loads, translates, and executes the shared query library."""
    print("\n" + "=" * 60)
    print("TASK 4: CALL QUERIES FROM PYTHON")
    print("=" * 60)
    
    # 1. Monthly Active Users Query
    mau_query_pg = load_query('monthly_active_users')
    mau_query_sqlite = translate_pg_to_sqlite(mau_query_pg)
    mau = pd.read_sql(mau_query_sqlite, engine)
    print("Monthly Active Users:")
    print(mau.head(10))
    
    # 2. Revenue by Segment Query
    revenue_query_pg = load_query('revenue_by_segment')
    revenue_query_sqlite = translate_pg_to_sqlite(revenue_query_pg)
    revenue = pd.read_sql(revenue_query_sqlite, engine)
    print("\nRevenue by Segment:")
    print(revenue.head(10))
    
    # 3. Conversion Funnel Query
    funnel_query_pg = load_query('conversion_funnel')
    funnel_query_sqlite = translate_pg_to_sqlite(funnel_query_pg)
    # Fill NaN conversion percentages with 0.0 in case of zero signups (should be populated)
    funnel = pd.read_sql(funnel_query_sqlite, engine)
    funnel['conversion_pct'] = funnel['conversion_pct'].fillna(0.0)
    print("\nConversion Funnel:")
    print(funnel.head(10))
    
    return mau, revenue, funnel


# ---------------------------------------------------------
# TASK 5: Validate Query Results (1 mark)
# ---------------------------------------------------------
def validate_metrics(mau_df, revenue_df, funnel_df):
    """Validate metric computations for consistency, ranges, and null counts."""
    print("\n" + "=" * 60)
    print("TASK 5: VALIDATE QUERY RESULTS")
    print("=" * 60)
    
    # Check for nulls
    assert mau_df.isnull().sum().sum() == 0, "MAU has nulls"
    assert revenue_df.isnull().sum().sum() == 0, "Revenue has nulls"
    
    # Check value ranges
    assert (revenue_df['monthly_revenue'] > 0).all(), "Revenue <= 0"
    assert (funnel_df['conversion_pct'] >= 0).all() and (funnel_df['conversion_pct'] <= 100).all(), "Conversion out of range"
    
    # Check consistency
    for idx, row in revenue_df.iterrows():
        assert row['order_count'] > 0, "Zero orders"
        assert row['monthly_revenue'] > 0, "Zero revenue"
        
    print("[SUCCESS] All metrics validated successfully")
    return True


def run_pipeline():
    """Execute complete shared SQL query execution and validation pipeline."""
    engine = create_engine('sqlite:///analytics.db')
    
    # Initialize tables
    create_synthetic_tables(engine)
    
    # Execute SQL queries
    mau, revenue, funnel = execute_queries(engine)
    
    # Validate metrics
    validate_metrics(mau, revenue, funnel)
    
    print("\n" + "=" * 60)
    print("KPI QUERY PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
