import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_sample_dataset():
    """
    Create synthetic customer revenue & churn dataset reflecting the real-world scenario:
    - Enterprise (5% of customer base): 1% churn rate, $150k lifetime value, ~1200 retention days, ~1.2 support tickets.
    - SMB (40% of customer base): 12% churn rate, $8k lifetime value, ~240 retention days, ~4.5 support tickets.
    - Startup (55% of customer base): 8% churn rate, $2k lifetime value, ~480 retention days, ~3.1 support tickets.
    """
    np.random.seed(42)
    n = 1000
    
    # Customer types distribution
    types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n, p=[0.05, 0.40, 0.55])
    products = np.random.choice(['Basic', 'Pro', 'Enterprise Platform'], size=n, p=[0.50, 0.35, 0.15])
    
    churn_list = []
    ltv_list = []
    support_tickets_list = []
    retention_days_list = []
    
    for t in types:
        if t == 'Enterprise':
            c = np.random.binomial(1, 0.01)
            ltv = np.random.normal(loc=150000, scale=10000)
            st = np.random.poisson(lam=1.2)
            ret = np.random.normal(loc=1200, scale=100)
        elif t == 'SMB':
            c = np.random.binomial(1, 0.12)
            ltv = np.random.normal(loc=8000, scale=800)
            st = np.random.poisson(lam=4.5)
            ret = np.random.normal(loc=240, scale=30)
        else:  # Startup
            c = np.random.binomial(1, 0.08)
            ltv = np.random.normal(loc=2000, scale=200)
            st = np.random.poisson(lam=3.1)
            ret = np.random.normal(loc=480, scale=50)
            
        churn_list.append(c)
        ltv_list.append(max(ltv, 50.0))
        support_tickets_list.append(st)
        retention_days_list.append(max(int(ret), 1))
        
    df = pd.DataFrame({
        'customer_id': [f"CUST_{i:04d}" for i in range(1, n + 1)],
        'customer_type': types,
        'product': products,
        'churn': churn_list,
        'lifetime_value': np.round(ltv_list, 2),
        'support_tickets': support_tickets_list,
        'retention_days': retention_days_list
    })
    
    return df


# ---------------------------------------------------------
# TASK 1: Define Segments and Compute Metrics (1 mark)
# ---------------------------------------------------------
def task_1_define_segments(df):
    """
    Group dataset by 'customer_type' and compute 4+ metrics:
    - Lifetime Value (mean)
    - Churn (mean)
    - Support Tickets (mean)
    - Retention Days (mean)
    - Customer Count (count)
    """
    print("=" * 60)
    print("TASK 1: DEFINE SEGMENTS AND COMPUTE METRICS")
    print("=" * 60)
    
    segment_metrics = df.groupby('customer_type').agg({
        'lifetime_value': 'mean',
        'churn': 'mean',
        'support_tickets': 'mean',
        'retention_days': 'mean',
        'customer_id': 'count'
    })
    
    segment_metrics.columns = ['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention', 'count']
    
    print(segment_metrics)
    return segment_metrics


# ---------------------------------------------------------
# TASK 2: Summary Statistics Table (1 mark)
# ---------------------------------------------------------
def task_2_summary_table(segment_metrics):
    """
    Format metrics with readable labels and comparisons.
    Rank segments by at least 2 metrics (LTV descending and Churn ascending).
    Show both absolute values and rankings.
    """
    print("\n" + "=" * 60)
    print("TASK 2: SUMMARY STATISTICS TABLE")
    print("=" * 60)
    
    segment_summary = segment_metrics.copy()
    segment_summary['ltv_rank'] = segment_summary['avg_ltv'].rank(ascending=False)
    segment_summary['churn_rank'] = segment_summary['churn_rate'].rank(ascending=True)
    
    print("--- Absolute Values and Rankings ---")
    print(segment_summary[['avg_ltv', 'ltv_rank', 'churn_rate', 'churn_rank']])
    
    # Generate human-readable formatted representation
    formatted_summary = pd.DataFrame(index=segment_summary.index)
    formatted_summary['Avg LTV'] = segment_summary['avg_ltv'].apply(lambda x: f"${x:,.2f}")
    formatted_summary['LTV Rank'] = segment_summary['ltv_rank'].astype(int)
    formatted_summary['Churn Rate'] = segment_summary['churn_rate'].apply(lambda x: f"{x:.1%}")
    formatted_summary['Churn Rank'] = segment_summary['churn_rank'].astype(int)
    formatted_summary['Avg Support Tickets'] = segment_summary['avg_tickets'].apply(lambda x: f"{x:.2f}")
    formatted_summary['Avg Retention (Days)'] = segment_summary['avg_retention'].apply(lambda x: f"{x:.1f}")
    formatted_summary['Customer Count'] = segment_summary['count'].astype(int)
    
    print("\n--- Formatted for Readability ---")
    print(formatted_summary)
    
    return segment_summary, formatted_summary


# ---------------------------------------------------------
# TASK 3: Visual Comparison (1 mark)
# ---------------------------------------------------------
def task_3_visual_comparison(segment_metrics, output_path='segment_heatmap.png'):
    """
    Create a Seaborn heatmap showing 3+ metrics across segments (avg_ltv, churn_rate, avg_tickets).
    Use column-wise scaling/normalization to preserve readability across different magnitudes
    (e.g., LTV in thousands vs Churn in decimals) while keeping actual values annotated.
    Ensure green represents best performance (high LTV, low churn, low tickets) and red represents worst.
    """
    print("\n" + "=" * 60)
    print("TASK 3: VISUAL COMPARISON")
    print("=" * 60)
    
    # Select columns for the heatmap
    metrics_to_plot = segment_metrics[['avg_ltv', 'churn_rate', 'avg_tickets']].copy()
    
    # Scale columns between 0 and 1 so that colors represent relative performance
    scaled_data = (metrics_to_plot - metrics_to_plot.min()) / (metrics_to_plot.max() - metrics_to_plot.min())
    
    # Invert Churn Rate and Support Tickets so that lower values are green (1) and higher are red (0)
    scaled_data['churn_rate'] = 1.0 - scaled_data['churn_rate']
    scaled_data['avg_tickets'] = 1.0 - scaled_data['avg_tickets']
    
    # Format annotations to show actual raw values beautifully
    annot_data = metrics_to_plot.copy()
    annot_labels = np.array([
        [f"${annot_data.loc[idx, 'avg_ltv']:,.0f}", 
         f"{annot_data.loc[idx, 'churn_rate']:.1%}", 
         f"{annot_data.loc[idx, 'avg_tickets']:.2f}"]
        for idx in metrics_to_plot.index
    ])
    
    plt.figure(figsize=(9, 6.5))
    
    # Draw heatmap
    sns.heatmap(
        scaled_data,
        annot=annot_labels,
        fmt='',
        cmap='RdYlGn',
        cbar_kws={'label': 'Relative Performance Score (Green = Best, Red = Worst)'},
        linewidths=1,
        linecolor='#f0f0f0'
    )
    
    plt.title('Segment Comparison Heatmap (Relative Performance)', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Customer Type', fontsize=12)
    plt.xlabel('Metrics', fontsize=12)
    plt.xticks(ticks=[0.5, 1.5, 2.5], labels=['Average LTV', 'Churn Rate', 'Average Tickets'])
    plt.tight_layout()
    
    # Save the figure to both paths
    plt.savefig(output_path, dpi=300)
    os.makedirs('output', exist_ok=True)
    plt.savefig(os.path.join('output', output_path), dpi=300)
    plt.close()
    
    print(f"Heatmap saved successfully to: '{output_path}' and 'output/{output_path}'")


# ---------------------------------------------------------
# TASK 4: Top and Bottom Performer Analysis (1 mark)
# ---------------------------------------------------------
def task_4_performer_analysis(segment_metrics):
    """
    Identify top performer by value, bottom performer by churn, and best retention.
    Print and return formatted insights.
    """
    print("\n" + "=" * 60)
    print("TASK 4: TOP AND BOTTOM PERFORMER ANALYSIS")
    print("=" * 60)
    
    # Highest value segment
    top_segment = segment_metrics['avg_ltv'].idxmax()
    top_value = segment_metrics.loc[top_segment, 'avg_ltv']

    # Highest churn segment
    high_churn = segment_metrics['churn_rate'].idxmax()

    insights = f"""
HIGHEST VALUE: {top_segment} = ${top_value:,.0f}
HIGHEST CHURN: {high_churn} = {segment_metrics.loc[high_churn, 'churn_rate']:.1%}
BEST RETENTION: {segment_metrics['avg_retention'].idxmax()}
"""
    print(insights)
    return insights


# ---------------------------------------------------------
# TASK 5: Business-Facing Insights (1 mark)
# ---------------------------------------------------------
def task_5_business_insights(segment_metrics, output_path='output/segment_insights.csv'):
    """
    Present segment strategy summary with 2-3 sentence insights per segment.
    Include specific, metrics-connected action recommendations.
    Export insights and summary to CSV.
    """
    print("=" * 60)
    print("TASK 5: BUSINESS-FACING INSIGHTS")
    print("=" * 60)
    
    business_summary = """
SEGMENT STRATEGY SUMMARY:

Enterprise (5% of base, $150k LTV, 1% churn):
- Highest value, lowest churn
- Action: Maintain premium support, retention focus

SMB (40% of base, $8k LTV, 12% churn):
- Middle value, high churn risk
- Action: Improve onboarding, cheaper support tier

Startup (55% of base, $2k LTV, 8% churn):
- Lowest value, moderate churn
- Action: Self-service, education-focused
"""
    print(business_summary)
    
    # Exporting metrics to CSV with action strategies
    insights_records = []
    for segment in segment_metrics.index:
        row = segment_metrics.loc[segment]
        action = ""
        if segment == 'Enterprise':
            action = "Maintain high-touch premium support and executive alignment to retain these high-value accounts."
        elif segment == 'SMB':
            action = "Address onboarding friction and introduce lower-cost self-serve tiers to combat the elevated 12% churn."
        elif segment == 'Startup':
            action = "Provide scaleable self-service documentation and education paths to optimize low LTV accounts."
            
        insights_records.append({
            'customer_type': segment,
            'avg_ltv': float(row['avg_ltv']),
            'churn_rate': float(row['churn_rate']),
            'avg_tickets': float(row['avg_tickets']),
            'avg_retention': float(row['avg_retention']),
            'count': int(row['count']),
            'recommended_action': action
        })
        
    insights_df = pd.DataFrame(insights_records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    insights_df.to_csv(output_path, index=False)
    print(f"Segment insights exported successfully to: '{output_path}'")
    
    return insights_df


def run_pipeline():
    """Execute complete customer churn segmentation analysis pipeline."""
    print("Creating synthetic customer dataset (1,000 rows)...")
    df = create_sample_dataset()
    
    # Calculate and show overall aggregate statistics to contrast with segmented results
    avg_churn = df['churn'].mean()
    print(f"Overall average churn rate (aggregate): {avg_churn:.1%}")
    print("Notice how this hides the critical story of the individual segments!\n")
    
    # Execute tasks
    segment_metrics = task_1_define_segments(df)
    segment_summary, formatted_summary = task_2_summary_table(segment_metrics)
    task_3_visual_comparison(segment_metrics, output_path='segment_heatmap.png')
    task_4_performer_analysis(segment_metrics)
    insights_df = task_5_business_insights(segment_metrics, output_path='output/segment_insights.csv')
    
    print("\n" + "=" * 60)
    print("SEGMENT ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
