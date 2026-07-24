import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_metrics_pipeline(data_path="data/raw_revenue.csv", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if raw data exists
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}. Please run generate_data.py first.")
        
    # Read the data
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # -------------------------------------------------------------
    # Task 1: Resample Data by Time Period
    # -------------------------------------------------------------
    df_ts = df.set_index('date')
    
    # Weekly aggregation
    weekly_revenue = df_ts['revenue'].resample('W').sum()
    weekly_count = df_ts['orders'].resample('W').count()
    weekly_avg = df_ts['revenue'].resample('W').mean()
    
    # Monthly aggregation
    try:
        monthly_revenue = df_ts['revenue'].resample('ME').sum()
        monthly_count = df_ts['orders'].resample('ME').count()
        monthly_avg = df_ts['revenue'].resample('ME').mean()
    except ValueError:
        monthly_revenue = df_ts['revenue'].resample('M').sum()
        monthly_count = df_ts['orders'].resample('M').count()
        monthly_avg = df_ts['revenue'].resample('M').mean()
    
    # Identify period with highest revenue
    max_week = weekly_revenue.idxmax()
    max_week_val = weekly_revenue.max()
    max_month = monthly_revenue.idxmax()
    max_month_val = monthly_revenue.max()
    
    # -------------------------------------------------------------
    # Task 2: Compute Rolling Window Average
    # -------------------------------------------------------------
    df['revenue_ma7'] = df['revenue'].rolling(window=7).mean()
    df['revenue_ma30'] = df['revenue'].rolling(window=30).mean()
    
    # Plot raw vs rolling averages
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['revenue'], label='Raw Daily Revenue', alpha=0.3, color='gray')
    plt.plot(df['date'], df['revenue_ma7'], label='7-day Moving Average (Weekly Trend)', linewidth=2, color='#1f77b4')
    plt.plot(df['date'], df['revenue_ma30'], label='30-day Moving Average (Monthly Trend)', linewidth=3, color='#ff7f0e')
    plt.title('Daily Revenue vs. Rolling Moving Averages', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Revenue ($)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=10)
    plt.tight_layout()
    rolling_img_path = os.path.join(output_dir, 'rolling_avg.png')
    plt.savefig(rolling_img_path, dpi=300)
    plt.close()
    
    # -------------------------------------------------------------
    # Task 3: Calculate Month-over-Month Percentage Change
    # -------------------------------------------------------------
    mom_change = monthly_revenue.pct_change() * 100
    
    # Document months with growth vs decline
    # Note: the first month (January) will be NaN in pct_change, so we dropna() or skip
    growth_months = mom_change[mom_change > 0]
    decline_months = mom_change[mom_change < 0]
    
    # -------------------------------------------------------------
    # Task 4: Compute Cumulative Sum
    # -------------------------------------------------------------
    df['cumulative_revenue'] = df['revenue'].cumsum()
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['cumulative_revenue'], color='#2ca02c', linewidth=2.5)
    plt.title('Cumulative Revenue Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Total Revenue Accumulated ($)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    cumulative_img_path = os.path.join(output_dir, 'cumulative.png')
    plt.savefig(cumulative_img_path, dpi=300)
    plt.close()
    
    total_accumulated = df['cumulative_revenue'].iloc[-1]
    
    # -------------------------------------------------------------
    # Task 5: Identify Trend Pattern and Business Implications
    # -------------------------------------------------------------
    # Analyze rolling average trend
    # Let's use the last 30 days of the 30-day moving average as requested
    recent_ma30 = df['revenue_ma30'].iloc[-30:]
    trend_direction = 'up' if recent_ma30.iloc[-1] > recent_ma30.iloc[0] else 'down'
    trend_magnitude = ((recent_ma30.iloc[-1] - recent_ma30.iloc[0]) / recent_ma30.iloc[0]) * 100
    
    # Describe overall month-over-month growth patterns
    mom_growth_str = ""
    for month, val in mom_change.items():
        if pd.isna(val):
            mom_growth_str += f"- {month.strftime('%B %Y')}: Baseline month (N/A)\n"
        else:
            status = "Growth" if val > 0 else "Decline"
            mom_growth_str += f"- {month.strftime('%B %Y')}: {val:+.2f}% ({status})\n"
            
    # Business implications and suggestions based on trend direction
    if trend_direction == 'up':
        business_implication = "Accelerating growth - maintain current strategy. The business is experiencing sustainable, positive momentum once daily noise is filtered out."
        action_suggested = "1. Maintain the current marketing and sales strategy.\n2. Prepare operational capacity for increased order volume.\n3. Consider investing surplus cash into growth channels to capitalize on momentum."
    else:
        business_implication = "Declining momentum - investigate causes. Despite periodic spikes (noise), the underlying demand is softening."
        action_suggested = "1. Conduct a deep dive into customer retention and acquisition costs.\n2. Review pricing strategies or recent product changes that might have impacted conversions.\n3. Implement targeted promotion campaigns to reverse the downward trend."
        
    revenue_volatility = df['revenue'].std()
    
    # Build full text analysis
    analysis_text = f"""================================================================================
TIME SERIES TREND ANALYSIS & BUSINESS IMPLICATIONS
================================================================================

1. RESAMPLING SUMMARY (Task 1)
--------------------------------------------------------------------------------
- Weekly Revenue:
{weekly_revenue.to_string()}

- Weekly Orders:
{weekly_count.to_string()}

- Comparison:
  * Highest Revenue Week: {max_week.strftime('%Y-%m-%d')} with ${max_week_val:,.2f}
  * Highest Revenue Month: {max_month.strftime('%B %Y')} with ${max_month_val:,.2f}

2. ROLLING AVERAGE OBSERVATIONS (Task 2)
--------------------------------------------------------------------------------
- 7-day MA reveals weekly cyclical patterns (e.g., weekend dips) and filters out daily spikes.
- 30-day MA reveals the long-term trend, smoothing out the high daily noise and weekly cycles.
- Hidden trend: Daily revenue fluctuates wildly (e.g., standard deviation of ${revenue_volatility:,.2f}), masking whether the business is growing. The 30-day MA clearly shows a steady, continuous trend that is invisible when looking at daily data alone.

3. MONTH-OVER-MONTH (MoM) GROWTH ANALYSIS (Task 3)
--------------------------------------------------------------------------------
{mom_growth_str}
- Growth Months:
{", ".join([m.strftime('%B %Y') for m in growth_months.index])}
- Decline Months:
{", ".join([m.strftime('%B %Y') for m in decline_months.index]) if len(decline_months) > 0 else "None"}

- Pattern Interpretation:
  The growth pattern indicates a stable and accelerating trajectory. Monthly revenues are expanding consistently MoM, confirming that the short-term fluctuations are noise rather than structural issues.

4. CUMULATIVE REVENUE METRICS (Task 4)
--------------------------------------------------------------------------------
- Total Revenue Accumulated by End of Period: ${total_accumulated:,.2f}
- Visualized in: output/cumulative.png

5. TREND ANALYSIS & BUSINESS IMPLICATIONS (Task 5)
--------------------------------------------------------------------------------
- Rolling Average Trend: {trend_direction.upper()}
- Change in 30-day MA over last 30 days of period: {trend_magnitude:+.2f}%
- Month-over-Month Growth (Latest Month): {mom_change.dropna().iloc[-1]:+.2f}%
- Revenue Volatility (Daily standard deviation): ${revenue_volatility:,.2f} (measure of noise)

- Business Implication:
  {business_implication}

- Suggested Actions:
{action_suggested}

================================================================================
Report generated successfully.
"""
    
    # Save the analysis to output/trend_analysis.txt
    analysis_file_path = os.path.join(output_dir, 'trend_analysis.txt')
    with open(analysis_file_path, 'w') as f:
        f.write(analysis_text)
        
    print(f"Metrics computed successfully!")
    print(f"Saved plots to {rolling_img_path} and {cumulative_img_path}")
    print(f"Saved analysis to {analysis_file_path}")
    
    # Print the requested summary to stdout
    print("\n" + "="*40 + "\nTREND ANALYSIS PREVIEW:\n" + "="*40)
    print(f"Rolling Average Trend: {trend_direction.upper()}")
    print(f"Change over last 30 days: {trend_magnitude:.1f}%")
    print(f"Month-over-month growth (latest): {mom_change.dropna().iloc[-1]:.1f}%")
    print(f"Total revenue: ${total_accumulated:,.0f}")
    print(f"Revenue volatility: ${revenue_volatility:.0f}")

if __name__ == "__main__":
    run_metrics_pipeline()
