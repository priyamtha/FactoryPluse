import os
import pandas as pd
import numpy as np
from scipy import stats

def create_sample_dataset():
    """
    Create synthetic customer dataset with realistic data and intentional extreme outliers.
    Includes revenue ($500k whale / data entry error) and age (150+ years impossible value).
    """
    np.random.seed(42)
    n = 100
    
    # Typical customer revenue ($20 to $500) with a couple of massive outliers
    normal_revenue = np.random.exponential(scale=100, size=n-3) + 20
    outlier_revenue = [15000.0, 50000.0, 500000.0]  # Extreme revenue outliers
    revenue = np.concatenate([normal_revenue, outlier_revenue])
    
    # Typical customer age (18 to 70) with impossible values
    normal_age = np.random.randint(18, 70, size=n-2)
    outlier_age = [150, 210]  # Impossible age outliers
    age = np.concatenate([normal_age, outlier_age])
    
    # Customer IDs
    customer_ids = [f"CUST_{i:04d}" for i in range(1, len(revenue) + 1)]
    
    df = pd.DataFrame({
        'customer_id': customer_ids,
        'revenue': np.round(revenue, 2),
        'age': age
    })
    
    return df


# ---------------------------------------------------------
# TASK 1: Z-Score Outlier Detection (1 mark)
# ---------------------------------------------------------
def task_1_zscore_detection(df, column='revenue'):
    """
    Detect outliers as values beyond ±3 standard deviations from the mean.
    Note: Z-score assumes a normal distribution.
    """
    print("=" * 60)
    print(f"TASK 1: Z-SCORE OUTLIER DETECTION FOR '{column.upper()}'")
    print("=" * 60)
    
    z_col = f"{column}_zscore"
    df[z_col] = np.abs(stats.zscore(df[column]))
    
    z_outliers = df[df[z_col] > 3]
    
    mean_val = df[column].mean()
    std_val = df[column].std()
    
    print(f"Column: {column}")
    print(f"Mean: {mean_val:.2f}, Std Dev: {std_val:.2f}")
    print(f"Threshold Bounds (Mean ± 3*Std): [{mean_val - 3*std_val:.2f}, {mean_val + 3*std_val:.2f}]")
    print(f"Z-score outliers found (Z > 3): {len(z_outliers)}")
    print("\nSample Z-Score Outliers:")
    print(z_outliers[['customer_id', column, z_col]])
    
    return df, z_outliers


# ---------------------------------------------------------
# TASK 2: IQR Outlier Detection (1 mark)
# ---------------------------------------------------------
def task_2_iqr_detection(df, column='revenue'):
    """
    Detect outliers beyond 1.5 × IQR from quartiles (Q1 and Q3).
    IQR method is robust against skewed distributions and non-normal data.
    """
    print("\n" + "=" * 60)
    print(f"TASK 2: IQR OUTLIER DETECTION FOR '{column.upper()}'")
    print("=" * 60)
    
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    iqr_col = f"is_outlier_iqr_{column}"
    df[iqr_col] = (df[column] < lower_bound) | (df[column] > upper_bound)
    iqr_outliers = df[df[iqr_col]]
    
    print(f"Column: {column}")
    print(f"Q1 (25th percentile): {Q1:.2f}")
    print(f"Q3 (75th percentile): {Q3:.2f}")
    print(f"IQR (Interquartile Range): {IQR:.2f}")
    print(f"Lower Bound (Q1 - 1.5*IQR): {lower_bound:.2f}")
    print(f"Upper Bound (Q3 + 1.5*IQR): {upper_bound:.2f}")
    print(f"IQR Outliers found: {len(iqr_outliers)}")
    print("\nSample IQR Outliers:")
    print(iqr_outliers[['customer_id', column, iqr_col]].head(5))
    
    return df, lower_bound, upper_bound, iqr_outliers


# ---------------------------------------------------------
# TASK 3: Cap Outliers at Boundaries (1 mark)
# ---------------------------------------------------------
def task_3_cap_outliers(df, column='revenue', lower=None, upper=None):
    """
    Apply Winsorization/capping strategy: replace extreme values beyond boundaries
    with the exact boundary threshold values (lower and upper).
    """
    print("\n" + "=" * 60)
    print(f"TASK 3: CAP OUTLIERS AT BOUNDARIES FOR '{column.upper()}'")
    print("=" * 60)
    
    capped_col = f"{column}_capped"
    df[capped_col] = df[column].clip(lower=lower, upper=upper)
    
    print(f"Capping '{column}' to range [{lower:.2f}, {upper:.2f}]")
    print(f"Before Capping: min = {df[column].min():.2f}, max = {df[column].max():.2f}")
    print(f"After Capping:  min = {df[capped_col].min():.2f}, max = {df[capped_col].max():.2f}")
    
    capped_rows = df[df[column] != df[capped_col]]
    print(f"Total rows modified by capping: {len(capped_rows)}")
    
    return df


# ---------------------------------------------------------
# TASK 4: Flag Outliers with Binary Column (1 mark)
# ---------------------------------------------------------
def task_4_flag_outliers(df, column='revenue'):
    """
    Mark anomalies with a binary indicator column without dropping records.
    Combines IQR and Z-score detection methods for robust downstream analysis.
    """
    print("\n" + "=" * 60)
    print(f"TASK 4: FLAG OUTLIERS WITH COMBINED BINARY COLUMN FOR '{column.upper()}'")
    print("=" * 60)
    
    z_col = f"{column}_zscore"
    iqr_col = f"is_outlier_iqr_{column}"
    flag_col = f"is_outlier_{column}"
    
    # Combined flag (either IQR or Z-score > 3)
    df[flag_col] = (df[iqr_col]) | (df[z_col] > 3)
    
    normal = df[~df[flag_col]]
    anomalies = df[df[flag_col]]
    
    print(f"Normal records: {len(normal)}")
    print(f"Anomalies flagged: {len(anomalies)}")
    print(f"Percentage of anomalies: {len(anomalies) / len(df) * 100:.2f}%")
    
    print("\nSample Flagged Anomalies:")
    print(anomalies[['customer_id', column, z_col, iqr_col, flag_col]].head(5))
    
    return df, normal, anomalies


# ---------------------------------------------------------
# TASK 5: Create Cleaning Log (1 mark)
# ---------------------------------------------------------
def task_5_create_cleaning_log(log_entries, output_path='output/cleaning_log.csv'):
    """
    Document all outlier-related transformations in a structured log DataFrame
    and save to CSV format.
    """
    print("\n" + "=" * 60)
    print("TASK 5: CREATE CLEANING LOG")
    print("=" * 60)
    
    log_df = pd.DataFrame(log_entries)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    log_df.to_csv(output_path, index=False)
    
    print(f"Cleaning Log successfully written to '{output_path}':")
    print(log_df.to_string())
    
    return log_df


def run_pipeline():
    """Execute complete Outlier Detection & Handling Pipeline."""
    print("Initializing Raw Customer Revenue & Age Dataset...")
    df = create_sample_dataset()
    print("Raw Dataset Summary:")
    print(df.describe())
    print("\n")
    
    cleaning_log = []
    
    # ------------------------------------
    # Process 'revenue' column
    # ------------------------------------
    df, z_out_rev = task_1_zscore_detection(df, column='revenue')
    df, lower_rev, upper_rev, iqr_out_rev = task_2_iqr_detection(df, column='revenue')
    df = task_3_cap_outliers(df, column='revenue', lower=lower_rev, upper=upper_rev)
    df, norm_rev, anom_rev = task_4_flag_outliers(df, column='revenue')
    
    cleaning_log.append({
        'column': 'revenue',
        'method': 'IQR + Z-Score',
        'action': 'cap & flag',
        'threshold_lower': round(lower_rev, 2),
        'threshold_upper': round(upper_rev, 2),
        'affected_rows': len(anom_rev),
        'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    # ------------------------------------
    # Process 'age' column (Domain specific capping: 18 to 100)
    # ------------------------------------
    print("\n" + "-" * 60)
    print("PROCESSING 'AGE' COLUMN (DOMAIN SPECIFIC IMPOSSIBLE VALUES)")
    print("-" * 60)
    
    df, z_out_age = task_1_zscore_detection(df, column='age')
    df, lower_age, upper_age, iqr_out_age = task_2_iqr_detection(df, column='age')
    
    # Domain capping for age: min 18, max 100
    df['age_capped'] = df['age'].clip(lower=18, upper=100)
    df['is_outlier_age'] = (df['age'] < 18) | (df['age'] > 100)
    
    cleaning_log.append({
        'column': 'age',
        'method': 'Domain Bounds (18-100)',
        'action': 'cap & flag',
        'threshold_lower': 18,
        'threshold_upper': 100,
        'affected_rows': int(df['is_outlier_age'].sum()),
        'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    # Save cleaning log
    task_5_create_cleaning_log(cleaning_log, output_path='output/cleaning_log.csv')
    
    print("\n" + "=" * 60)
    print("OUTLIER DETECTION PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
