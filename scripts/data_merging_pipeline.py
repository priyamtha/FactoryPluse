import os
import json
import pandas as pd
import numpy as np

def create_sample_dataset():
    """
    Create synthetic relational datasets:
    - Customer Table: 1,000 unique customers
    - Orders Table: 5,000 orders (1-to-many relationship, including zero-order customers & orphaned orders)
    """
    np.random.seed(42)
    
    # 1,000 customers (CUST_0001 to CUST_1000)
    customer_ids = [f"CUST_{i:04d}" for i in range(1, 1001)]
    df_customers = pd.DataFrame({
        'customer_id': customer_ids,
        'customer_name': [f"Customer_{i}" for i in range(1, 1001)],
        'segment': np.random.choice(['B2B', 'SMB', 'Enterprise'], size=1000, p=[0.4, 0.4, 0.2]),
        'signup_date': pd.date_range('2024-01-01', periods=1000, freq='4H').strftime('%Y-%m-%d')
    })
    
    # Active customers: 850 of the 1000 customers place 5,000 orders
    # 150 customers have 0 orders (unmatched left)
    active_customer_ids = customer_ids[:850]
    
    # 4,950 orders belonging to active customers
    order_customer_ids = list(np.random.choice(active_customer_ids, size=4950))
    
    # 50 orphaned orders with customer IDs outside customer table (CUST_9901 to CUST_9950)
    orphaned_customer_ids = [f"CUST_{i:04d}" for i in range(9901, 9951)]
    order_customer_ids.extend(orphaned_customer_ids)
    
    # Shuffle orders dataset
    np.random.shuffle(order_customer_ids)
    
    df_orders = pd.DataFrame({
        'order_id': [f"ORD_{i:06d}" for i in range(1, 5001)],
        'customer_id': order_customer_ids,
        'order_amount': np.round(np.random.exponential(scale=120, size=5000) + 15, 2),
        'order_date': pd.date_range('2025-01-01', periods=5000, freq='10T').strftime('%Y-%m-%d %H:%M:%S')
    })
    
    return df_customers, df_orders


# ---------------------------------------------------------
# TASK 1: Explicit Join with Row Count Validation (1 mark)
# ---------------------------------------------------------
def task_1_explicit_left_join(df_customers, df_orders):
    """
    Perform explicit LEFT JOIN on 'customer_id' and validate row count metrics.
    """
    print("=" * 60)
    print("TASK 1: EXPLICIT JOIN WITH ROW COUNT VALIDATION")
    print("=" * 60)
    
    print(f"Left Table (Customers) Row Count:  {len(df_customers)}")
    print(f"Right Table (Orders) Row Count:   {len(df_orders)}")
    
    # Explicit LEFT JOIN
    df_merged = pd.merge(df_customers, df_orders, on='customer_id', how='left')
    
    print(f"Merged Result Row Count:           {len(df_merged)}")
    print(f"Row Count Delta (Merged - Left):   {len(df_merged) - len(df_customers)}")
    print(f"Explanation: Since customers have multiple orders (1-to-many), merged rows > left rows.\n")
    
    print("Merged Sample Head:")
    print(df_merged.head(5))
    
    return df_merged


# ---------------------------------------------------------
# TASK 2: Detect Unmatched Keys (1 mark)
# ---------------------------------------------------------
def task_2_detect_unmatched_keys(df_customers, df_orders, output_dir='output'):
    """
    Identify and extract unmatched keys from both left and right directions:
    - Customers with zero orders (unmatched left)
    - Orphaned orders without valid customer account (unmatched right)
    """
    print("\n" + "=" * 60)
    print("TASK 2: DETECT UNMATCHED KEYS")
    print("=" * 60)
    
    unmatched_customers = df_customers[~df_customers['customer_id'].isin(df_orders['customer_id'])]
    unmatched_orders = df_orders[~df_orders['customer_id'].isin(df_customers['customer_id'])]
    
    print(f"Customers without orders (Unmatched Left): {len(unmatched_customers)}")
    print(f"Orphaned orders (Unmatched Right):        {len(unmatched_orders)}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    cust_path = os.path.join(output_dir, 'unmatched_customers.csv')
    ord_path = os.path.join(output_dir, 'unmatched_orders.csv')
    
    unmatched_customers.to_csv(cust_path, index=False)
    unmatched_orders.to_csv(ord_path, index=False)
    
    print(f"\nUnmatched customers saved to: '{cust_path}'")
    print(f"Unmatched orders saved to:    '{ord_path}'")
    
    print("\nSample Unmatched Customers (No Purchases):")
    print(unmatched_customers.head(3))
    
    print("\nSample Orphaned Orders (No Customer Account Record):")
    print(unmatched_orders.head(3))
    
    return unmatched_customers, unmatched_orders


# ---------------------------------------------------------
# TASK 3: Compare Join Types (1 mark)
# ---------------------------------------------------------
def task_3_compare_join_types(df_customers, df_orders):
    """
    Perform and compare all 4 SQL join types (INNER, LEFT, RIGHT, OUTER).
    """
    print("\n" + "=" * 60)
    print("TASK 3: COMPARE JOIN TYPES")
    print("=" * 60)
    
    inner = pd.merge(df_customers, df_orders, on='customer_id', how='inner')
    left  = pd.merge(df_customers, df_orders, on='customer_id', how='left')
    right = pd.merge(df_customers, df_orders, on='customer_id', how='right')
    outer = pd.merge(df_customers, df_orders, on='customer_id', how='outer')
    
    print(f"INNER Join Row Count: {len(inner)} (Only matching customer & order pairs)")
    print(f"LEFT  Join Row Count: {len(left)}  (All customers + matching orders + null-padded non-buyers)")
    print(f"RIGHT Join Row Count: {len(right)} (All orders + matching customers + null-padded orphans)")
    print(f"OUTER Join Row Count: {len(outer)} (All customers and all orders preserved)")
    
    return inner, left, right, outer


# ---------------------------------------------------------
# TASK 4: Validate No Unexpected Duplication (1 mark)
# ---------------------------------------------------------
def task_4_validate_no_duplication(df_merged):
    """
    Check column integrity for unexpected suffix conflicts (_x, _y)
    and inspect order cardinality per customer key.
    """
    print("\n" + "=" * 60)
    print("TASK 4: VALIDATE NO UNEXPECTED DUPLICATION")
    print("=" * 60)
    
    print("Merged Table Columns:")
    print(list(df_merged.columns))
    
    suffix_cols = [c for c in df_merged.columns if c.endswith('_x') or c.endswith('_y')]
    if suffix_cols:
        print(f"WARNING: Unexpected column suffix conflicts found: {suffix_cols}")
    else:
        print("✓ Success: Clean column names with no suffix collisions (_x / _y).")
        
    key_counts = df_merged['customer_id'].value_counts()
    print(f"Max orders per single customer: {key_counts.max()}")
    print(f"Min orders per customer in left join: {key_counts.min()}")
    print(f"Average orders per active customer: {key_counts.mean():.2f}")
    
    print("\nTop 5 Customers by Order Frequency:")
    print(key_counts.head(5))


# ---------------------------------------------------------
# TASK 5: Document Join Decision (1 mark)
# ---------------------------------------------------------
def task_5_document_join_decision(df_customers, df_orders, df_merged, unmatched_cust, unmatched_ord):
    """
    Document join methodology, operational details, and business reasoning in JSON report format.
    """
    print("\n" + "=" * 60)
    print("TASK 5: DOCUMENT JOIN DECISION")
    print("=" * 60)
    
    join_report = {
        'join_type': 'left',
        'left_table': 'customers',
        'right_table': 'orders',
        'join_key': 'customer_id',
        'left_rows': len(df_customers),
        'right_rows': len(df_orders),
        'result_rows': len(df_merged),
        'unmatched_left': len(unmatched_cust),
        'unmatched_right': len(unmatched_ord),
        'reasoning': 'Left join preserves all customer master records, ensuring non-purchasing customers are retained for marketing churn analysis while expanding order histories for active buyers.'
    }
    
    json_report = json.dumps(join_report, indent=2)
    print("--- EXECUTIVE JOIN DECISION REPORT (JSON) ---")
    print(json_report)
    
    # Save report to output directory
    os.makedirs('output', exist_ok=True)
    with open('output/join_report.json', 'w') as f:
        f.write(json_report)
        
    print("\nJoin decision report written to 'output/join_report.json'")


def run_pipeline():
    """Execute complete Relational Data Merging & Join Validation Pipeline."""
    print("Creating sample customer (1,000 rows) and orders (5,000 rows) datasets...")
    df_customers, df_orders = create_sample_dataset()
    
    df_merged = task_1_explicit_left_join(df_customers, df_orders)
    unmatched_cust, unmatched_ord = task_2_detect_unmatched_keys(df_customers, df_orders, output_dir='output')
    inner, left, right, outer = task_3_compare_join_types(df_customers, df_orders)
    task_4_validate_no_duplication(df_merged)
    task_5_document_join_decision(df_customers, df_orders, df_merged, unmatched_cust, unmatched_ord)
    
    print("\n" + "=" * 60)
    print("RELATIONAL DATA MERGING PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
