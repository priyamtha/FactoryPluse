import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_sample_dataset():
    """
    Create synthetic customer churn dataset with multi-collinear features and 
    causal confounders to benchmark Pearson vs Spearman correlation analysis.
    """
    np.random.seed(42)
    n = 1000
    
    customer_pain = np.random.uniform(0, 10, size=n)
    
    # support_tickets strongly driven by customer_pain
    support_tickets = np.random.poisson(lam=customer_pain * 1.5)
    
    # churn binary target driven by customer_pain
    churn_prob = 1 / (1 + np.exp(-(customer_pain - 5)))
    churn = np.random.binomial(1, churn_prob)
    
    # transactions_per_month & engagement (highly collinear r > 0.9)
    transactions_per_month = np.random.normal(loc=15 - customer_pain * 0.8, scale=3, size=n).clip(min=0)
    engagement = transactions_per_month * 1.25 + np.random.normal(0, 0.5, size=n)
    
    tenure_months = np.random.randint(1, 48, size=n)
    total_spent = np.round(transactions_per_month * tenure_months * np.random.uniform(20, 50, size=n), 2)
    
    df = pd.DataFrame({
        'customer_id': [f"CUST_{i:04d}" for i in range(1, n + 1)],
        'support_tickets': support_tickets,
        'transactions_per_month': np.round(transactions_per_month, 2),
        'engagement': np.round(engagement, 2),
        'tenure_months': tenure_months,
        'total_spent': total_spent,
        'churn': churn
    })
    
    return df


# ---------------------------------------------------------
# TASK 1: Compute Pearson and Spearman Correlation (1 mark)
# ---------------------------------------------------------
def task_1_compute_correlations(df):
    """
    Compute linear (Pearson) and monotonic rank (Spearman) correlation matrices.
    Compare correlations against target variable 'churn'.
    """
    print("=" * 60)
    print("TASK 1: PEARSON VS SPEARMAN CORRELATION MATRIX")
    print("=" * 60)
    
    numeric_df = df.drop(columns=['customer_id'])
    
    pearson_corr = numeric_df.corr(method='pearson')
    spearman_corr = numeric_df.corr(method='spearman')
    
    comparison = pd.DataFrame({
        'pearson_churn': pearson_corr['churn'],
        'spearman_churn': spearman_corr['churn'],
        'abs_difference': (pearson_corr['churn'] - spearman_corr['churn']).abs()
    }).sort_values(by='abs_difference', ascending=False)
    
    print("--- Correlation Comparison with Target Variable ('churn') ---")
    print(comparison)
    
    return pearson_corr, spearman_corr, numeric_df


# ---------------------------------------------------------
# TASK 2: Visualize Correlation Heatmap (1 mark)
# ---------------------------------------------------------
def task_2_visualize_heatmap(pearson_corr, output_path='output/correlation_heatmap.png'):
    """
    Generate annotated Seaborn heatmap visualization of feature correlations.
    Save plot output to designated path.
    """
    print("\n" + "=" * 60)
    print("TASK 2: VISUALIZE CORRELATION HEATMAP")
    print("=" * 60)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        pearson_corr,
        annot=True,
        fmt=".2f",
        cmap='coolwarm',
        vmin=-1.0,
        vmax=1.0,
        center=0,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )
    ax.set_title('Feature Correlation Matrix (Pearson r)', fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    print(f"✓ Heatmap visualization saved successfully to: '{output_path}'")


# ---------------------------------------------------------
# TASK 3: Identify Strongly Correlated Pairs (1 mark)
# ---------------------------------------------------------
def task_3_identify_strong_correlations(pearson_corr):
    """
    Flatten correlation matrix and isolate feature pairs with strong correlation (|r| > 0.7).
    Exclude self-correlations (r = 1.0).
    """
    print("\n" + "=" * 60)
    print("TASK 3: IDENTIFY STRONGLY CORRELATED PAIRS (|r| > 0.7)")
    print("=" * 60)
    
    corr_flat = pearson_corr.unstack()
    strong = corr_flat[corr_flat.abs() > 0.7].sort_values(ascending=False)
    
    # Exclude diagonal self-correlations (r == 1.0)
    strong_pairs = strong[strong != 1.0]
    
    # Remove duplicate symmetric pairs
    unique_pairs = {}
    for (f1, f2), val in strong_pairs.items():
        pair_key = tuple(sorted([f1, f2]))
        if pair_key not in unique_pairs:
            unique_pairs[pair_key] = val
            
    unique_pairs_series = pd.Series(unique_pairs).sort_values(ascending=False)
    print("--- Top Strongly Correlated Feature Pairs ---")
    for (f1, f2), val in unique_pairs_series.items():
        print(f"  • {f1:<24} <-> {f2:<24}: r = {val:+.4f}")
        
    return unique_pairs_series


# ---------------------------------------------------------
# TASK 4: Business Interpretation & Causation Analysis (1 mark)
# ---------------------------------------------------------
def task_4_business_interpretation(pearson_corr):
    """
    Evaluate correlation vs causation. Deconstruct spurious correlations,
    confounding variables, and business directionality.
    """
    print("\n" + "=" * 60)
    print("TASK 4: BUSINESS INTERPRETATION & CAUSATION ANALYSIS")
    print("=" * 60)
    
    r_tickets_churn = round(float(pearson_corr.loc['support_tickets', 'churn']), 2)
    
    analysis = {
        'support_tickets <-> churn': {
            'correlation_r': r_tickets_churn,
            'possible_directions': [
                'support_tickets -> churn (customer gives up after contacting support)',
                'churn -> support_tickets (unhappy customers contact support before leaving)',
                'customer_pain -> both (underlying product bugs cause both tickets and churn)'
            ],
            'data_indicates': 'Likely customer_pain is the unobserved confounder; support tickets are a symptom, not the root cause.',
            'actionable_business_strategy': 'Do NOT reduce support access. Focus on fixing core product defects that generate customer friction.'
        },
        'transactions_per_month <-> engagement': {
            'correlation_r': round(float(pearson_corr.loc['transactions_per_month', 'engagement']), 2),
            'finding': 'Multi-collinear feature redundancy (r > 0.90).',
            'actionable_business_strategy': 'Drop one redundant feature during model development to prevent inflated standard errors.'
        }
    }
    
    json_analysis = json.dumps(analysis, indent=2)
    print("--- Executive Causation Analysis Report (JSON) ---")
    print(json_analysis)
    
    with open('output/correlation_causation_report.json', 'w') as f:
        f.write(json_analysis)
        
    return analysis


# ---------------------------------------------------------
# TASK 5: Feature Selection Based on Correlation (1 mark)
# ---------------------------------------------------------
def task_5_feature_selection(numeric_df, pearson_corr):
    """
    Eliminate redundant collinear features (r > 0.90) to ensure feature parsimony
    and prevent multicollinearity issues in downstream machine learning models.
    """
    print("\n" + "=" * 60)
    print("TASK 5: FEATURE SELECTION BASED ON CORRELATION")
    print("=" * 60)
    
    r_eng_tx = pearson_corr.loc['transactions_per_month', 'engagement']
    print(f"Collinearity Check: 'transactions_per_month' vs 'engagement' r = {r_eng_tx:.4f}")
    print("Decision: 'engagement' is redundant with 'transactions_per_month'. Dropping 'engagement'.\n")
    
    df_features = numeric_df.drop(columns=['engagement'])
    clean_corr = df_features.corr(method='pearson')
    
    print("--- Clean Reduced Feature Correlation Matrix ---")
    print(clean_corr)
    
    return df_features, clean_corr


def run_pipeline():
    """Execute complete Correlation Analysis & Causation Evaluation Pipeline."""
    print("Creating synthetic customer churn dataset (1,000 rows)...")
    df = create_sample_dataset()
    
    pearson_corr, spearman_corr, numeric_df = task_1_compute_correlations(df)
    task_2_visualize_heatmap(pearson_corr, output_path='output/correlation_heatmap.png')
    unique_pairs = task_3_identify_strong_correlations(pearson_corr)
    analysis = task_4_business_interpretation(pearson_corr)
    df_features, clean_corr = task_5_feature_selection(numeric_df, pearson_corr)
    
    print("\n" + "=" * 60)
    print("CORRELATION ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
