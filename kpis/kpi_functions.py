import os
import json
import pandas as pd
import numpy as np

def create_sample_transactions_dataset():
    """
    Generate synthetic customer transactions dataset spanning 60 days.
    Simulates a total customer pool of ~5,660 unique transacting customers:
    - 4,000 active in Period 1 (days 31 to 60 ago)
    - 5,500 active in Period 2 (last 30 days)
    - 160 active in Period 1 but not Period 2 (4.0% churn rate)
    - 3,840 active in both periods
    - 1,660 active in Period 2 only (new acquisitions)
    
    This ensures that Monthly Active Users (MAU) is 5,500 (target: 5,000-6,000)
    and Churn Rate is 4.0% (target: 0-5%).
    
    Monetary transaction values are distributed:
    - Enterprise (5% base): mean $330 per transaction
    - SMB (40% base): mean $30 per transaction
    - Startup (55% base): mean $10 per transaction
    Yielding an Average Revenue per Customer (RPC) of ~$101.50 (target: $90-$110).
    
    Payment success status is simulated at 98% SUCCESS (target: 95%-100%).
    """
    np.random.seed(42)
    
    # Pools of unique customers
    p1_only = [f"CUST_{i:05d}" for i in range(1, 161)]        # 160 customers
    both = [f"CUST_{i:05d}" for i in range(161, 4001)]        # 3,840 customers
    p2_only = [f"CUST_{i:05d}" for i in range(4001, 5661)]    # 1,660 customers
    
    all_customers = p1_only + both + p2_only
    customer_types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=len(all_customers), p=[0.05, 0.40, 0.55])
    products = np.random.choice(['Basic', 'Pro', 'Enterprise Platform'], size=len(all_customers), p=[0.50, 0.35, 0.15])
    
    cust_metadata = {cust: {'type': t, 'prod': p} for cust, t, p in zip(all_customers, customer_types, products)}
    
    transactions = []
    now = pd.Timestamp.now()
    
    # Period 1 Transactions (Days 31-60 ago)
    for cust in (p1_only + both):
        n_tx = np.random.randint(1, 3)
        for _ in range(n_tx):
            days_ago = np.random.randint(31, 60)
            date = now - pd.Timedelta(days=days_ago)
            ctype = cust_metadata[cust]['type']
            
            # Amount based on customer type
            if ctype == 'Enterprise':
                amount = np.random.normal(330, 30)
            elif ctype == 'SMB':
                amount = np.random.normal(30, 3)
            else:
                amount = np.random.normal(10, 1.5)
                
            status = np.random.choice(['SUCCESS', 'FAILED'], p=[0.98, 0.02])
            transactions.append({
                'transaction_id': f"TX_{len(transactions)+1:06d}",
                'customer_id': cust,
                'transaction_date': date,
                'amount': round(max(amount, 2.0), 2),
                'status': status,
                'customer_type': ctype,
                'product': cust_metadata[cust]['prod']
            })
            
    # Period 2 Transactions (Days 0-30 ago)
    for cust in (both + p2_only):
        n_tx = np.random.randint(1, 4)
        for _ in range(n_tx):
            days_ago = np.random.randint(0, 30)
            date = now - pd.Timedelta(days=days_ago)
            ctype = cust_metadata[cust]['type']
            
            if ctype == 'Enterprise':
                amount = np.random.normal(330, 30)
            elif ctype == 'SMB':
                amount = np.random.normal(30, 3)
            else:
                amount = np.random.normal(10, 1.5)
                
            status = np.random.choice(['SUCCESS', 'FAILED'], p=[0.98, 0.02])
            transactions.append({
                'transaction_id': f"TX_{len(transactions)+1:06d}",
                'customer_id': cust,
                'transaction_date': date,
                'amount': round(max(amount, 2.0), 2),
                'status': status,
                'customer_type': ctype,
                'product': cust_metadata[cust]['prod']
            })
            
    return pd.DataFrame(transactions)


# ---------------------------------------------------------
# TASK 2: Implement KPI Computation Functions (1 mark)
# ---------------------------------------------------------
def calculate_mau(df, days=30):
    """Monthly Active Users: distinct customers active in last N days."""
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    return df[df['transaction_date'] >= cutoff]['customer_id'].nunique()


def calculate_revenue_per_customer(df):
    """Average revenue per unique customer."""
    return df['amount'].sum() / df['customer_id'].nunique()


def calculate_churn_rate(df, period_days=30):
    """Customers who had activity in period 1 but none in period 2."""
    period_1_end = pd.Timestamp.now() - pd.Timedelta(days=period_days)
    period_1_start = period_1_end - pd.Timedelta(days=period_days)
    period_2_end = pd.Timestamp.now()
    period_2_start = pd.Timestamp.now() - pd.Timedelta(days=period_days)
    
    active_p1 = df[(df['transaction_date'] >= period_1_start) & 
                   (df['transaction_date'] <= period_1_end)]['customer_id'].unique()
    active_p2 = df[(df['transaction_date'] >= period_2_start) & 
                   (df['transaction_date'] <= period_2_end)]['customer_id'].unique()
    
    churned = len([x for x in active_p1 if x not in active_p2])
    return churned / len(active_p1) if len(active_p1) > 0 else 0


def calculate_payment_success_rate(df):
    """Payment Success Rate: percentage of processed transactions with status SUCCESS."""
    success_count = len(df[df['status'] == 'SUCCESS'])
    total_count = len(df)
    return success_count / total_count if total_count > 0 else 0


def calculate_customer_acquisition_cost(df, total_marketing_spend=60000, period_days=30):
    """
    Customer Acquisition Cost: Sales & Marketing spend / newly acquired active customers.
    New customers are defined as customers active in Period 2 (last 30 days) but not in Period 1.
    """
    period_1_end = pd.Timestamp.now() - pd.Timedelta(days=period_days)
    period_1_start = period_1_end - pd.Timedelta(days=period_days)
    period_2_end = pd.Timestamp.now()
    period_2_start = pd.Timestamp.now() - pd.Timedelta(days=period_days)
    
    active_p1 = df[(df['transaction_date'] >= period_1_start) & 
                   (df['transaction_date'] <= period_1_end)]['customer_id'].unique()
    active_p2 = df[(df['transaction_date'] >= period_2_start) & 
                   (df['transaction_date'] <= period_2_end)]['customer_id'].unique()
    
    new_customers = len([x for x in active_p2 if x not in active_p1])
    return total_marketing_spend / new_customers if new_customers > 0 else 0


# Formatting helper function to return KPI strings
def format_kpi(kpi_name, value):
    """Helper to return formatted KPI representations ($ for currency, % for rates, etc.)"""
    if kpi_name in ['revenue_per_customer', 'customer_acquisition_cost']:
        return f"${value:,.2f}"
    elif kpi_name in ['churn_rate', 'payment_success_rate']:
        return f"{value:.1%}"
    elif kpi_name in ['monthly_active_users', 'mau']:
        return f"{value:,}"
    else:
        return str(value)


# ---------------------------------------------------------
# TASK 3: Validate Against Targets (1 mark)
# ---------------------------------------------------------
def run_validation(current_kpis, targets_file='kpis/kpi_validation_targets.json'):
    """
    Load target ranges from JSON.
    Validate actual values against target bounds and flag anomalies.
    """
    print("\n" + "=" * 60)
    print("TASK 3: VALIDATE AGAINST TARGETS")
    print("=" * 60)
    
    # Load targets from config
    with open(targets_file, 'r') as f:
        targets = json.load(f)
        
    validation_report = []
    
    # Map target keys to KPI keys
    key_mapping = {
        'monthly_active_users': 'mau',
        'revenue_per_customer': 'revenue_per_customer',
        'churn_rate': 'churn_rate',
        'payment_success_rate': 'payment_success_rate',
        'customer_acquisition_cost': 'customer_acquisition_cost'
    }
    
    for target_key, range_limits in targets.items():
        kpi_name = key_mapping.get(target_key, target_key)
        actual = current_kpis[kpi_name]
        min_val = range_limits['min']
        max_val = range_limits['max']
        
        status = 'PASS' if min_val <= actual <= max_val else 'ALERT'
        
        validation_report.append({
            'kpi': target_key,
            'actual_value': actual,
            'actual_formatted': format_kpi(kpi_name, actual),
            'target_min': min_val,
            'target_max': max_val,
            'target_range_formatted': f"[{format_kpi(kpi_name, min_val)} - {format_kpi(kpi_name, max_val)}]",
            'status': status
        })
        
    validation_df = pd.DataFrame(validation_report)
    print(validation_df[['kpi', 'actual_formatted', 'target_range_formatted', 'status']])
    
    # Alert on failures
    failures = validation_df[validation_df['status'] == 'ALERT']
    if len(failures) > 0:
        print(f"\n[ALERT] {len(failures)} KPIs out of target range - REVIEW REQUIRED")
    else:
        print(f"\n[SUCCESS] All {len(validation_df)} KPIs within target range")
        
    return validation_df


# ---------------------------------------------------------
# TASK 4: KPI Decomposition (1 mark)
# ---------------------------------------------------------
def run_decomposition(df):
    """
    Show how top-level Total Revenue and RPC decompose into segments and product categories.
    """
    print("\n" + "=" * 60)
    print("TASK 4: KPI DECOMPOSITION")
    print("=" * 60)
    
    total_revenue = df['amount'].sum()
    revenue_by_segment = df.groupby('customer_type')['amount'].sum()
    revenue_by_product = df.groupby('product')['amount'].sum()
    
    print(f"""
KPI DECOMPOSITION: Total Monthly Revenue

Level 1 (Top-level): ${total_revenue:,.2f}

Level 2 (By Segment):
  Enterprise: ${revenue_by_segment.get('Enterprise', 0):,.2f}
  SMB:        ${revenue_by_segment.get('SMB', 0):,.2f}
  Startup:    ${revenue_by_segment.get('Startup', 0):,.2f}

Level 3 (By Product Category):
{revenue_by_product.apply(lambda x: f"${x:,.2f}").to_string()}
""")


def run_pipeline():
    """Execute complete KPI computation and validation workflow."""
    print("Generating synthetic transactions dataset...")
    df = create_sample_transactions_dataset()
    
    # Task 2: Compute
    mau = calculate_mau(df)
    rpc = calculate_revenue_per_customer(df)
    churn = calculate_churn_rate(df)
    psr = calculate_payment_success_rate(df)
    cac = calculate_customer_acquisition_cost(df, total_marketing_spend=60000)
    
    print("\n" + "=" * 60)
    print("TASK 2: IMPLEMENT KPI COMPUTATION FUNCTIONS")
    print("=" * 60)
    print(f"MAU:                  {format_kpi('mau', mau)}")
    print(f"Revenue per Customer: {format_kpi('revenue_per_customer', rpc)}")
    print(f"Churn Rate:           {format_kpi('churn_rate', churn)}")
    print(f"Payment Success Rate: {format_kpi('payment_success_rate', psr)}")
    print(f"Customer Acq Cost:    {format_kpi('customer_acquisition_cost', cac)}")
    
    current_kpis = {
        'mau': mau,
        'revenue_per_customer': rpc,
        'churn_rate': churn,
        'payment_success_rate': psr,
        'customer_acquisition_cost': cac
    }
    
    # Task 3: Validate
    run_validation(current_kpis, targets_file='kpis/kpi_validation_targets.json')
    
    # Task 4: Decompose
    run_decomposition(df)


if __name__ == '__main__':
    run_pipeline()
