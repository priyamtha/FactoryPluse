import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def create_sample_dataset():
    """
    Create synthetic customer revenue dataset with high right-skewness (skew > 2.0)
    and heavy tails (kurtosis > 3.0), incorporating bimodal behavior (Retail vs Enterprise).
    """
    np.random.seed(42)
    n = 1000
    
    # 85% small retail accounts (mean ~$100), 15% enterprise accounts (mean ~$2500 with extreme outliers)
    small_accounts = np.random.exponential(scale=100, size=int(n * 0.85)) + 15
    enterprise_accounts = np.random.exponential(scale=2500, size=int(n * 0.15)) + 1200
    
    revenue = np.concatenate([small_accounts, enterprise_accounts])
    np.random.shuffle(revenue)
    
    df = pd.DataFrame({
        'customer_id': [f"CUST_{i:04d}" for i in range(1, n + 1)],
        'revenue': np.round(revenue, 2)
    })
    
    return df


# ---------------------------------------------------------
# TASK 1: Distribution Plots (1 mark)
# ---------------------------------------------------------
def task_1_distribution_plots(df, output_path='output/revenue_distribution.png'):
    """
    Generate side-by-side Histogram and Kernel Density Estimation (KDE) plots.
    Save plot output to designated path.
    """
    print("=" * 60)
    print("TASK 1: DISTRIBUTION PLOTS (HISTOGRAM & KDE)")
    print("=" * 60)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram
    axes[0].hist(df['revenue'], bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    axes[0].set_title('Revenue Distribution (Histogram)', fontsize=13)
    axes[0].set_xlabel('Revenue ($)', fontsize=11)
    axes[0].set_ylabel('Customer Count', fontsize=11)
    axes[0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # KDE (Density) Plot
    df['revenue'].plot(kind='density', ax=axes[1], color='darkblue', linewidth=2)
    axes[1].set_title('Revenue Distribution (KDE)', fontsize=13)
    axes[1].set_xlabel('Revenue ($)', fontsize=11)
    axes[1].set_ylabel('Probability Density', fontsize=11)
    axes[1].grid(axis='both', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    print(f"✓ Distribution plots saved successfully to: '{output_path}'")


# ---------------------------------------------------------
# TASK 2: Compute Skewness and Kurtosis (1 mark)
# ---------------------------------------------------------
def task_2_skewness_and_kurtosis(df):
    """
    Compute statistical higher-order moments: Skewness (3rd moment) and Kurtosis (4th moment).
    Analyze central tendency breakdown (Mean vs Median gap).
    """
    print("\n" + "=" * 60)
    print("TASK 2: COMPUTE SKEWNESS AND KURTOSIS")
    print("=" * 60)
    
    revenue = df['revenue']
    mean_val = revenue.mean()
    median_val = revenue.median()
    skewness = stats.skew(revenue)
    kurtosis = stats.kurtosis(revenue)
    
    print(f"Mean Revenue:   ${mean_val:.2f}")
    print(f"Median Revenue: ${median_val:.2f}")
    print(f"Mean - Median Gap: ${mean_val - median_val:.2f}")
    print(f"Skewness: {skewness:.2f}")
    print(f"Kurtosis: {kurtosis:.2f}\n")
    
    if abs(skewness) > 1:
        print("--> Highly skewed distribution! The mean is distorted by extreme values. Use MEDIAN for central tendency.")
    else:
        print("--> Moderately symmetric distribution.")
        
    if kurtosis > 3:
        print("--> Heavy tails / Leptokurtic distribution! Expect high frequency of extreme outliers in the right tail.")
    else:
        print("--> Normal / Light tailed distribution.")
        
    return skewness, kurtosis


# ---------------------------------------------------------
# TASK 3: Identify Abnormal Patterns (1 mark)
# ---------------------------------------------------------
def task_3_abnormal_patterns(df):
    """
    Analyze percentiles to detect bimodal behavior, tail gaps, and hidden customer clusters.
    """
    print("\n" + "=" * 60)
    print("TASK 3: IDENTIFY ABNORMAL PATTERNS & PERCENTILES")
    print("=" * 60)
    
    print("--- Summary Statistics ---")
    print(df['revenue'].describe())
    
    quantiles = [0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    percentiles = df['revenue'].quantile(quantiles)
    
    print("\n--- Detailed Revenue Percentiles ---")
    for q, val in percentiles.items():
        print(f"  {int(q*100):2d}th Percentile: ${val:10.2f}")
        
    gap_75_90 = percentiles[0.90] - percentiles[0.75]
    print(f"\nGap between 75th and 90th percentiles: ${gap_75_90:.2f}")
    if gap_75_90 > 2 * (percentiles[0.75] - percentiles[0.50]):
        print("--> Pattern Detected: Massive percentile jump indicates a distinct high-spending Enterprise cluster (Bimodal distribution)!")
        
    return percentiles


# ---------------------------------------------------------
# TASK 4: Compare Segment Distributions (1 mark)
# ---------------------------------------------------------
def task_4_compare_segment_distributions(df, output_path='output/segment_comparison.png'):
    """
    Segment dataset into High-Value (top 25%) vs Low-Value (bottom 25%) cohorts.
    Plot comparative histograms and print metrics.
    """
    print("\n" + "=" * 60)
    print("TASK 4: COMPARE SEGMENT DISTRIBUTIONS")
    print("=" * 60)
    
    q75 = df['revenue'].quantile(0.75)
    q25 = df['revenue'].quantile(0.25)
    
    high_value = df[df['revenue'] >= q75]
    low_value  = df[df['revenue'] <= q25]
    
    print(f"High-Value Segment (>= 75th percentile ${q75:.2f}): {len(high_value)} customers")
    print(f"  • Mean: ${high_value['revenue'].mean():.2f}, Median: ${high_value['revenue'].median():.2f}")
    
    print(f"Low-Value Segment (<= 25th percentile ${q25:.2f}): {len(low_value)} customers")
    print(f"  • Mean: ${low_value['revenue'].mean():.2f}, Median: ${low_value['revenue'].median():.2f}")
    
    # Plot side-by-side segment histograms
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].hist(low_value['revenue'], bins=30, color='lightcoral', edgecolor='black', alpha=0.7)
    axes[0].set_title('Low-Value Customer Revenue Distribution', fontsize=12)
    axes[0].set_xlabel('Revenue ($)', fontsize=10)
    axes[0].set_ylabel('Customer Count', fontsize=10)
    axes[0].grid(axis='y', linestyle='--', alpha=0.7)
    
    axes[1].hist(high_value['revenue'], bins=30, color='mediumseagreen', edgecolor='black', alpha=0.7)
    axes[1].set_title('High-Value Enterprise Customer Revenue Distribution', fontsize=12)
    axes[1].set_xlabel('Revenue ($)', fontsize=10)
    axes[1].set_ylabel('Customer Count', fontsize=10)
    axes[1].grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    print(f"✓ Comparative segment plots saved to: '{output_path}'")
    
    return high_value, low_value


# ---------------------------------------------------------
# TASK 5: Business Interpretation (1 mark)
# ---------------------------------------------------------
def task_5_business_interpretation(df, skewness, kurtosis):
    """
    Synthesize statistical findings into an actionable executive business report.
    """
    print("\n" + "=" * 60)
    print("TASK 5: BUSINESS INTERPRETATION REPORT")
    print("=" * 60)
    
    mean_val = df['revenue'].mean()
    median_val = df['revenue'].median()
    p99 = df['revenue'].quantile(0.99)
    max_val = df['revenue'].max()
    
    interpretation = f"""
================================================================================
                    REVENUE DISTRIBUTION ANALYSIS & REPORT
================================================================================

1. CENTRAL TENDENCY METRICS:
   - Mean Revenue:   ${mean_val:.2f}
   - Median Revenue: ${median_val:.2f}
   - Discrepancy:    Mean is {((mean_val - median_val)/median_val)*100:.1f}% higher than Median.
   - Conclusion:     The average is misleading. Relying on mean revenue overestimates 
                     typical customer value.

2. SKEWNESS & TAIL BEHAVIOR:
   - Skewness: {skewness:.2f} -> {"Highly right-skewed (skew > 1.0)" if skewness > 1 else "Symmetric"}
   - Kurtosis: {kurtosis:.2f} -> {"Fat-tailed / Leptokurtic (kurtosis > 3.0)" if kurtosis > 3 else "Normal"}
   - Max Revenue: ${max_val:.2f}
   - Top 1% (99th Percentile): ${p99:.2f}

3. BUSINESS INSIGHT & STRATEGIC RECOMMENDATION:
   - Insight: The customer base exhibits a bimodal structure. The vast majority are 
     small self-service buyers ($15-$200), while a small minority (top 15%) represent 
     massive enterprise contracts ($1,200-$15,000+).
   - Strategic Action: Abandon a one-size-fits-all product/pricing strategy. 
     Segment accounts into separate 'Self-Serve Retail' vs 'Dedicated Enterprise' 
     tier operations to optimize marketing acquisition and account management.
================================================================================
"""
    print(interpretation)
    
    with open('output/business_interpretation.txt', 'w') as f:
        f.write(interpretation)
        
    print("Report written to 'output/business_interpretation.txt'")


def run_pipeline():
    """Execute complete Distribution Analysis & Statistical Profiling Pipeline."""
    print("Creating sample customer revenue dataset (1,000 rows)...")
    df = create_sample_dataset()
    
    task_1_distribution_plots(df, output_path='output/revenue_distribution.png')
    skewness, kurtosis = task_2_skewness_and_kurtosis(df)
    percentiles = task_3_abnormal_patterns(df)
    high_val, low_val = task_4_compare_segment_distributions(df, output_path='output/segment_comparison.png')
    task_5_business_interpretation(df, skewness, kurtosis)
    
    print("\n" + "=" * 60)
    print("DISTRIBUTION ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
