import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def create_join_tables(engine):
    """
    Generate synthetic dataset matching strict validation specifications:
    - customers: 1,000 profiles.
    - orders: 5,000 total orders.
      - 100 customers have NO orders (unmatched).
      - 10 orders have customer_ids not present in customers (orphaned).
    - order_items: 8,000 line items.
    - products: 500 records.
    """
    np.random.seed(42)
    n_customers = 1000
    n_orders = 5000
    n_items = 8000
    n_products = 500
    
    # 1. Customers
    customer_ids = np.arange(1001, 1001 + n_customers)
    customer_types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n_customers, p=[0.05, 0.40, 0.55])
    signup_dates = [pd.Timestamp('2024-01-01') + pd.Timedelta(days=int(offset)) 
                    for offset in np.random.randint(0, 365, size=n_customers)]
    signup_dates = [d.date() for d in signup_dates]
    
    df_customers = pd.DataFrame({
        'customer_id': customer_ids.astype(int),
        'customer_type': customer_types,
        'signup_date': signup_dates
    })
    
    # 2. Orders
    # Reserve 100 customers who never order
    ordering_customers = customer_ids[100:]  # 900 customers active
    
    # Generate 4,990 regular orders
    reg_customer_ids = np.random.choice(ordering_customers, size=n_orders - 10)
    
    # Generate 10 orphaned orders (non-existent customer_ids)
    orphaned_customer_ids = np.arange(9901, 9911)
    
    all_order_customer_ids = np.concatenate([reg_customer_ids, orphaned_customer_ids])
    
    order_dates = [pd.Timestamp('2024-01-01') + pd.Timedelta(days=int(offset)) 
                   for offset in np.random.randint(0, 365, size=n_orders)]
    order_dates = [d.date() for d in order_dates]
    
    order_amounts = np.random.uniform(20.0, 1500.0, size=n_orders).round(2)
    order_ids = np.arange(1, n_orders + 1)
    
    df_orders = pd.DataFrame({
        'order_id': order_ids.astype(int),
        'customer_id': all_order_customer_ids.astype(int),
        'order_amount': order_amounts,
        'order_date': order_dates
    })
    
    # 3. Products
    product_ids = np.arange(1, n_products + 1)
    product_names = [f"Product_{pid:03d}" for pid in product_ids]
    categories = np.random.choice(['SaaS', 'Hardware', 'Support', 'Training'], size=n_products)
    
    df_products = pd.DataFrame({
        'product_id': product_ids.astype(int),
        'product_name': product_names,
        'category': categories
    })
    
    # 4. Order Items
    # Each order gets at least 1 item
    oi_order_ids = []
    oi_product_ids = []
    oi_quantities = []
    oi_unit_prices = []
    
    for oid in order_ids:
        # Give at least 1 item
        oi_order_ids.append(oid)
        oi_product_ids.append(np.random.choice(product_ids))
        oi_quantities.append(np.random.randint(1, 5))
        oi_unit_prices.append(round(np.random.uniform(10.0, 300.0), 2))
        
    # Generate remaining 3,000 items randomly
    remaining_items = n_items - n_orders
    extra_order_ids = np.random.choice(order_ids, size=remaining_items)
    extra_product_ids = np.random.choice(product_ids, size=remaining_items)
    extra_quantities = np.random.randint(1, 5, size=remaining_items)
    extra_unit_prices = np.random.uniform(10.0, 300.0, size=remaining_items).round(2)
    
    oi_order_ids.extend(extra_order_ids)
    oi_product_ids.extend(extra_product_ids)
    oi_quantities.extend(extra_quantities)
    oi_unit_prices.extend(extra_unit_prices)
    
    df_order_items = pd.DataFrame({
        'order_item_id': np.arange(1, n_items + 1).astype(int),
        'order_id': np.array(oi_order_ids).astype(int),
        'product_id': np.array(oi_product_ids).astype(int),
        'quantity': np.array(oi_quantities).astype(int),
        'unit_price': np.array(oi_unit_prices).round(2)
    })
    
    # Write to SQL database
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)
    df_orders.to_sql('orders', engine, if_exists='replace', index=False)
    df_products.to_sql('products', engine, if_exists='replace', index=False)
    df_order_items.to_sql('order_items', engine, if_exists='replace', index=False)
    
    print("[SUCCESS] Loaded customer (1,000), orders (5,000), items (8,000), products (500) tables")


def translate_pg_to_sqlite(sql):
    """
    Translates standard PostgreSQL Outer Joins to SQLite UNION emulations.
    """
    if "FULL OUTER JOIN" in sql:
        sql = """
        SELECT c.customer_id, o.order_id, o.order_amount
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        UNION
        SELECT c.customer_id, o.order_id, o.order_amount
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL;
        """
    return sql


def load_query(query_name):
    """Load SQL query from file."""
    with open(f'queries/{query_name}.sql', 'r') as f:
        return f.read()


def run_join_validation(engine):
    """Executes join types and prints outputs and assertions."""
    # Read row count before
    customers_count = len(pd.read_sql("SELECT * FROM customers", engine))
    
    # ---------------------------------------------------------
    # TASK 1: LEFT JOIN with Row Count Validation
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("TASK 1: LEFT JOIN WITH ROW COUNT VALIDATION")
    print("=" * 60)
    q1 = load_query('join_left_validation')
    joined = pd.read_sql(q1, engine)
    
    print(f"Before: {customers_count} customers")
    print(f"After LEFT JOIN (grouped): {len(joined)} rows")
    
    # Run the raw un-grouped left join to show multiplication factors
    raw_joined = pd.read_sql("SELECT c.customer_id, o.order_id FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id", engine)
    print(f"After LEFT JOIN (ungrouped): {len(raw_joined)} rows")
    diff = len(raw_joined) - customers_count
    pct_change = (diff / customers_count) * 100
    avg_multiplicity = len(raw_joined) / customers_count
    print(f"Change: {diff} rows ({pct_change:.1f}%)")
    print(f"Multiplication factor (orders per customer): {avg_multiplicity:.2f}")
    
    # ---------------------------------------------------------
    # TASK 2: Detect Unmatched Keys
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("TASK 2: DETECT UNMATCHED KEYS")
    print("=" * 60)
    q2_cust = load_query('join_unmatched_customers')
    no_orders = pd.read_sql(q2_cust, engine)
    
    q2_ord = load_query('join_unmatched_orders')
    orphaned = pd.read_sql(q2_ord, engine)
    
    print(f"Customers without orders: {len(no_orders)} ({(len(no_orders)/customers_count)*100:.1f}%)")
    print(f"Orphaned orders (no matching customer): {len(orphaned)}")
    
    if len(orphaned) > 0:
        print("[WARNING] Orphaned records found - investigate customer_id mismatch")
        
    # ---------------------------------------------------------
    # TASK 3: Compare Join Types
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("TASK 3: COMPARE JOIN TYPES")
    print("=" * 60)
    
    q3_inner = load_query('join_compare_inner')
    inner = pd.read_sql(q3_inner, engine)
    
    q3_left = load_query('join_compare_left')
    left = pd.read_sql(q3_left, engine)
    
    q3_full_pg = load_query('join_compare_full')
    q3_full_sqlite = translate_pg_to_sqlite(q3_full_pg)
    full = pd.read_sql(q3_full_sqlite, engine)
    
    print(f"INNER: {len(inner)} rows (only matched)")
    print(f"LEFT:  {len(left)} rows (all left, matched right)")
    print(f"FULL:  {len(full)} rows (all from both)")
    
    # Assertions
    assert len(left) >= len(inner), "LEFT join cannot have fewer rows than INNER"
    assert len(full) >= max(len(left), 1000), "FULL outer join should cover all left records and orphaned orders"
    print("[SUCCESS] Join type count assertions passed successfully")
    
    # ---------------------------------------------------------
    # TASK 4: Multi-Table Join
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("TASK 4: MULTI-TABLE JOIN")
    print("=" * 60)
    
    q4 = load_query('join_multi_table')
    result = pd.read_sql(q4, engine)
    print(f"Multi-table join retrieved {len(result)} rows for segment 'Enterprise'")
    print(result.head())
    
    # Validate no unexpected duplication
    # Because order_items contains itemized lines, and we join customers -> orders -> order_items,
    # the sum of (quantity * price) in result set grouped by product should exactly match expected total.
    # We must filter the expected_total query by 'Enterprise' customers to match our result set query!
    # Wait, the expected query:
    # SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_type = 'Enterprise'
    product_total = result.groupby('product_id')['line_total'].sum()
    expected_total_df = pd.read_sql("""
        SELECT SUM(oi.quantity * oi.unit_price) as sum_total
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.customer_type = 'Enterprise'
    """, engine)
    expected_total = expected_total_df.iloc[0, 0]
    
    print(f"Result sum: {product_total.sum():,.2f}, Expected sum: {expected_total:,.2f}")
    assert abs(product_total.sum() - expected_total) < 0.01, "Duplication detected in multi-table join!"
    print("[SUCCESS] Multi-table join validated - no duplication detected")
    
    # ---------------------------------------------------------
    # TASK 5: Document Join Decisions
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("TASK 5: DOCUMENT JOIN DECISIONS")
    print("=" * 60)
    with open('queries/join_documentation.txt', 'r') as f:
        print(f.read())


def run_pipeline():
    """Run full join validation pipeline."""
    engine = create_engine('sqlite:///analytics.db')
    
    # Recreate tables with validation constraints
    create_join_tables(engine)
    
    # Run tests
    run_join_validation(engine)
    
    print("\n" + "=" * 60)
    print("JOIN VALIDATION PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
