import os
import pandas as pd
import numpy as np

def create_sample_dataset():
    """
    Create synthetic customer revenue & churn dataset reflecting the real-world scenario:
    - Enterprise (5% of customer base): 1% churn rate, 70% of total revenue.
    - SMB (40% of customer base): 12% churn rate, 15% of total revenue.
    - Startup (55% of customer base): 8% churn rate, 15% of total revenue.
    """
    np.random.seed(42)
    n = 1000
    
    # Customer types distribution
    types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n, p=[0.05, 0.40, 0.55])
    products = np.random.choice(['Basic', 'Pro', 'Enterprise Platform'], size=n, p=[0.50, 0.35, 0.15])
    
    churn_list = []
    revenue_list = []
    support_tickets_list = []
    
    for t in types:
        if t == 'Enterprise':
            c = np.random.binomial(1, 0.01)
            r = np.random.normal(loc=14000, scale=2000)
            st = np.random.poisson(lam=1.2)
        elif t == 'SMB':
            c = np.random.binomial(1, 0.12)
            r = np.random.normal(loc=375, scale=50)
            st = np.random.poisson(lam=4.5)
        else:  # Startup
            c = np.random.binomial(1, 0.08)
            r = np.random.normal(loc=275, scale=40)
            st = np.random.poisson(lam=3.1)
            
        churn_list.append(c)
        revenue_list.append(max(r, 50.0))
        support_tickets_list.append(st)
        
    df = pd.DataFrame({
        'customer_id': [f"CUST_{i:04d}" for i in range(1, n + 1)],
        'customer_type': types,
        'product': products,
        'churn': churn_list,
        'revenue': np.round(revenue_list, 2),
        'support_tickets': support_tickets_list
    })
    
    return df


# ---------------------------------------------------------
# TASK 1: Single-Level GroupBy with Multiple Aggregations (1 mark)
# ---------------------------------------------------------
def task_1_single_level_groupby(df):
    """
    Group dataset by 'customer_type' and compute multiple metrics:
    churn rate, total revenue, customer count, and average support tickets.
    """
    print("=" * 60)
    print("TASK 1: SINGLE-LEVEL GROUPBY WITH MULTIPLE AGGREGATIONS")
    print("=" * 60)
    
    segment_metrics = df.groupby('customer_type').agg({
        'churn': 'mean',
        'revenue': 'sum',
        'customer_id': 'count',
        'support_tickets': 'mean'
    })
    
    segment_metrics.columns = ['churn_rate', 'total_revenue', 'customer_count', 'avg_support_tickets']
    
    print("--- Single-Level GroupBy Segment Metrics ---")
    print(segment_metrics)
    
    return segment_metrics


# ---------------------------------------------------------
# TASK 2: Multi-Level GroupBy & Unstack (1 mark)
# ---------------------------------------------------------
def task_2_multi_level_groupby(df):
    """
    Group dataset across two dimensions simultaneously ('customer_type' and 'product').
    Unstack the multi-index output for matrix inspection.
    """
    print("\n" + "=" * 60)
    print("TASK 2: MULTI-LEVEL GROUPBY AND UNSTACK")
    print("=" * 60)
    
    product_segment = df.groupby(['customer_type', 'product']).agg({
        'revenue': 'sum',
        'customer_id': 'count'
    })
    
    product_segment.columns = ['total_revenue', 'customer_count']
    
    print("--- Multi-Level GroupBy Result (Long Format) ---")
    print(product_segment)
    
    # Unstack multi-index for matrix view
    product_segment_pivot = product_segment.unstack()
    print("\n--- Unstacked Matrix View ---")
    print(product_segment_pivot)
    
    return product_segment, product_segment_pivot


# ---------------------------------------------------------
# TASK 3: Pivot Table (1 mark)
# ---------------------------------------------------------
def task_3_pivot_table(df):
    """
    Construct 2D Pivot Table: customer_type rows, product columns, summing revenue.
    """
    print("\n" + "=" * 60)
    print("TASK 3: PIVOT TABLE CREATION")
    print("=" * 60)
    
    pivot = pd.pivot_table(
        df,
        values='revenue',
        index='customer_type',
        columns='product',
        aggfunc='sum',
        fill_value=0
    )
    
    print("--- Revenue Pivot Table (customer_type x product) ---")
    print(pivot)
    
    return pivot


# ---------------------------------------------------------
# TASK 4: Rank and Identify Top/Bottom Performers (1 mark)
# ---------------------------------------------------------
def task_4_rank_segments(segment_metrics):
    """
    Rank segments by churn rate and compute percentage revenue contribution.
    """
    print("\n" + "=" * 60)
    print("TASK 4: RANK AND IDENTIFY TOP/BOTTOM PERFORMERS")
    print("=" * 60)
    
    # Rank segments by churn rate (1 = lowest churn / best)
    segment_metrics['churn_rank'] = segment_metrics['churn_rate'].rank()
    
    # Sort to display highest churn segment first
    worst_first = segment_metrics.sort_values('churn_rate', ascending=False)
    print("--- Segments Ranked by Churn Rate (Worst/Highest Churn First) ---")
    print(worst_first[['churn_rate', 'churn_rank', 'customer_count', 'total_revenue']])
    
    # Calculate percentage share of total revenue
    segment_metrics['revenue_contribution'] = (
        segment_metrics['total_revenue'] / segment_metrics['total_revenue'].sum() * 100
    )
    
    print("\n--- Segment Revenue Contribution & Churn Rate Matrix ---")
    print(segment_metrics[['revenue_contribution', 'churn_rate', 'total_revenue']])
    
    return segment_metrics


# ---------------------------------------------------------
# TASK 5: Surface Actionable Segment Insights (1 mark)
# ---------------------------------------------------------
def task_5_surface_insights(segment_metrics, output_path='output/segment_insights.csv'):
    """
    Iterate over aggregated segment metrics to construct business insight records
    and generate actionable recommendations based on churn thresholds.
    """
    print("\n" + "=" * 60)
    print("TASK 5: SURFACE ACTIONABLE SEGMENT INSIGHTS")
    print("=" * 60)
    
    insights = []
    
    for segment in segment_metrics.index:
        row = segment_metrics.loc[segment]
        
        insight = {
            'segment': segment,
            'customer_count': int(row['customer_count']),
            'churn_rate': f"{row['churn_rate']:.1%}",
            'total_revenue': f"${row['total_revenue']:,.0f}",
            'revenue_contribution': f"{row['revenue_contribution']:.1f}%",
            'action': ''
        }
        
        # Rule-based business action assignment
        if row['churn_rate'] > 0.10:
            insight['action'] = 'HIGH PRIORITY: Churn above 10%. Investigate pain points and offer success support.'
        elif row['churn_rate'] < 0.02:
            insight['action'] = 'HEALTHY: Churn below 2%. Maintain high-touch executive service level.'
        else:
            insight['action'] = 'MONITOR: Moderate churn. Optimize onboarding flow.'
            
        insights.append(insight)
        
    insights_df = pd.DataFrame(insights)
    
    print("--- ACTIONABLE SEGMENT INSIGHTS SUMMARY TABLE ---")
    print(insights_df.to_string(index=False))
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    insights_df.to_csv(output_path, index=False)
    print(f"\n✓ Segment insights exported successfully to: '{output_path}'")
    
    return insights_df


def run_pipeline():
    """Execute complete Grouping, Aggregation & Segment Analysis Pipeline."""
    print("Creating synthetic customer dataset (1,000 rows)...")
    df = create_sample_dataset()
    
    segment_metrics = task_1_single_level_groupby(df)
    product_segment, product_segment_pivot = task_2_multi_level_groupby(df)
    pivot = task_3_pivot_table(df)
    segment_metrics = task_4_rank_segments(segment_metrics)
    insights_df = task_5_surface_insights(segment_metrics, output_path='output/segment_insights.csv')
    
    print("\n" + "=" * 60)
    print("SEGMENT ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
