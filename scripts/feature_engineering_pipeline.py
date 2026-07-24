import pandas as pd
import numpy as np

def create_sample_dataset():
    """
    Create synthetic customer transaction dataset for feature engineering.
    Contains raw columns: total_transactions, days_as_customer, total_spent,
    days_since_last_purchase, purchase_count.
    """
    np.random.seed(42)
    n = 500
    
    days_as_customer = np.random.randint(30, 1000, size=n)
    total_transactions = np.random.randint(1, 150, size=n)
    total_spent = np.round(total_transactions * np.random.uniform(15, 120, size=n) + np.random.uniform(50, 2000, size=n), 2)
    days_since_last_purchase = np.random.randint(1, 180, size=n)
    purchase_count = total_transactions  # Synonymous with total_transactions
    
    df = pd.DataFrame({
        'customer_id': [f"CUST_{i:04d}" for i in range(1, n + 1)],
        'days_as_customer': days_as_customer,
        'total_transactions': total_transactions,
        'purchase_count': purchase_count,
        'total_spent': total_spent,
        'days_since_last_purchase': days_since_last_purchase
    })
    
    return df


# ---------------------------------------------------------
# TASK 1: Compute Ratio Features (1 mark)
# ---------------------------------------------------------
def task_1_compute_ratio_features(df):
    """
    Compute normalized ratio features to measure velocity, unit economics, and monthly customer value:
    - transactions_per_month = total_transactions / (days_as_customer / 30)
    - avg_spend_per_transaction = total_spent / total_transactions
    - lifetime_value_per_month = total_spent / (days_as_customer / 30)
    """
    print("=" * 60)
    print("TASK 1: COMPUTE RATIO FEATURES")
    print("=" * 60)
    
    # Avoid division by zero
    days_in_months = np.maximum(df['days_as_customer'] / 30.0, 0.001)
    safe_transactions = np.maximum(df['total_transactions'], 1)
    
    df['transactions_per_month'] = np.round(df['total_transactions'] / days_in_months, 2)
    df['avg_spend_per_transaction'] = np.round(df['total_spent'] / safe_transactions, 2)
    df['lifetime_value_per_month'] = np.round(df['total_spent'] / days_in_months, 2)
    
    print("Ratio Features Summary Statistics:")
    print(df[['transactions_per_month', 'avg_spend_per_transaction', 'lifetime_value_per_month']].describe())
    
    print("\nSample Engineered Ratio Features:")
    print(df[['customer_id', 'days_as_customer', 'total_transactions', 'transactions_per_month', 'avg_spend_per_transaction']].head(5))
    
    return df


# ---------------------------------------------------------
# TASK 2: Binning with Equal-Width / Fixed Custom Bins (1 mark)
# ---------------------------------------------------------
def task_2_custom_binning(df):
    """
    Apply fixed interval binning using pd.cut() to classify engagement levels:
    - Bins: [0, 2, 10, infinity]
    - Labels: ['low', 'medium', 'high']
    """
    print("\n" + "=" * 60)
    print("TASK 2: BINNING WITH EQUAL-WIDTH / FIXED BINS (pd.cut)")
    print("=" * 60)
    
    df['engagement_tier'] = pd.cut(
        df['transactions_per_month'],
        bins=[0, 2, 10, float('inf')],
        labels=['low', 'medium', 'high'],
        include_lowest=True
    )
    
    print("Engagement Tier Value Counts:")
    print(df['engagement_tier'].value_counts())
    
    print("\nEngagement Tier Breakdown Sample:")
    print(df[['customer_id', 'transactions_per_month', 'engagement_tier']].head(5))
    
    return df


# ---------------------------------------------------------
# TASK 3: Binning with Quantiles (1 mark)
# ---------------------------------------------------------
def task_3_quantile_binning(df):
    """
    Apply equal-frequency quantile binning using pd.qcut() to divide total_spent into 4 quartiles:
    - Q1 (0-25%), Q2 (25-50%), Q3 (50-75%), Q4 (75-100%)
    """
    print("\n" + "=" * 60)
    print("TASK 3: BINNING WITH QUANTILES (pd.qcut)")
    print("=" * 60)
    
    df['spend_quartile'] = pd.qcut(
        df['total_spent'],
        q=4,
        labels=['Q1', 'Q2', 'Q3', 'Q4']
    )
    
    print("Spend Quartile Distribution:")
    print(df['spend_quartile'].value_counts())
    
    print("\nSpend Quartile Boundaries:")
    quantiles = df['total_spent'].quantile([0, 0.25, 0.50, 0.75, 1.0])
    print(quantiles)
    
    return df


# ---------------------------------------------------------
# TASK 4: Composite Score (RFM Score) (1 mark)
# ---------------------------------------------------------
def task_4_composite_rfm_score(df):
    """
    Construct a composite RFM (Recency, Frequency, Monetary) Customer Health Score:
    - Recency Score (1-5): Lower recency days = Higher recency score (5)
    - Frequency Score (1-5): Higher purchase count = Higher frequency score (5)
    - Monetary Score (1-5): Higher total spend = Higher monetary score (5)
    - RFM Score = Recency + Frequency + Monetary (Range 3 to 15)
    """
    print("\n" + "=" * 60)
    print("TASK 4: COMPOSITE RFM HEALTH SCORE CONSTRUCTION")
    print("=" * 60)
    
    # Recency: 5 quintiles (smaller days_since_last_purchase -> higher score)
    df['recency_score'] = pd.qcut(df['days_since_last_purchase'], q=5, labels=[5, 4, 3, 2, 1])
    
    # Frequency: 5 quintiles (higher purchase_count -> higher score)
    df['frequency_score'] = pd.qcut(df['purchase_count'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Monetary: 5 quintiles (higher total_spent -> higher score)
    df['monetary_score'] = pd.qcut(df['total_spent'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Composite RFM Score calculation
    df['rfm_score'] = (
        df['recency_score'].astype(int) +
        df['frequency_score'].astype(int) +
        df['monetary_score'].astype(int)
    )
    
    print("Composite RFM Score Distribution Summary:")
    print(df['rfm_score'].describe())
    
    print("\nSample RFM Scoring Matrix:")
    print(df[['customer_id', 'days_since_last_purchase', 'recency_score', 
              'purchase_count', 'frequency_score', 
              'total_spent', 'monetary_score', 'rfm_score']].head(5))
    
    return df


# ---------------------------------------------------------
# TASK 5: Feature Validation (1 mark)
# ---------------------------------------------------------
def task_5_feature_validation(df):
    """
    Validate engineered features: ensure range integrity, correct binning distribution,
    and verify zero null/NaN values introduced during transformations.
    """
    print("\n" + "=" * 60)
    print("TASK 5: FEATURE VALIDATION & SANITY CHECKS")
    print("=" * 60)
    
    # Range checks
    print(f"Engagement Tier Distribution:\n{df['engagement_tier'].value_counts()}")
    print(f"\nSpend Quartile Distribution:\n{df['spend_quartile'].value_counts()}")
    print(f"\nRFM Score Range: Min = {df['rfm_score'].min()}, Max = {df['rfm_score'].max()}")
    
    # Verify no NaNs introduced
    target_feature_cols = [
        'transactions_per_month',
        'avg_spend_per_transaction',
        'lifetime_value_per_month',
        'engagement_tier',
        'spend_quartile',
        'rfm_score'
    ]
    
    null_counts = df[target_feature_cols].isna().sum()
    print("\nMissing Values Check across Engineered Features:")
    print(null_counts)
    
    if null_counts.sum() == 0:
        print("✓ Success: Zero missing/NaN values across all engineered features!")
    else:
        print("WARNING: Missing values detected in engineered features!")
        
    return df


def run_pipeline():
    """Execute complete Domain Feature Engineering Pipeline."""
    print("Creating sample customer dataset...")
    df = create_sample_dataset()
    
    df = task_1_compute_ratio_features(df)
    df = task_2_custom_binning(df)
    df = task_3_quantile_binning(df)
    df = task_4_composite_rfm_score(df)
    task_5_feature_validation(df)
    
    print("\n" + "=" * 60)
    print("DOMAIN FEATURE ENGINEERING PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
