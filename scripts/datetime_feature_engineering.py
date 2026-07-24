import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_sample_transaction_dataset():
    """
    Create a synthetic transaction dataset containing raw timestamp strings,
    customer IDs, transaction amounts, and category information.
    """
    np.random.seed(42)
    n_rows = 150
    
    # Generate random customer IDs
    customer_ids = [f"CUST_{i:03d}" for i in np.random.randint(1, 21, size=n_rows)]
    
    # Generate timestamp strings spanning multiple weeks in early 2025
    start_date = pd.Timestamp('2025-01-01 08:00:00')
    dates = []
    for _ in range(n_rows):
        random_days = np.random.randint(0, 45)
        random_hours = np.random.randint(0, 24)
        random_minutes = np.random.randint(0, 60)
        random_seconds = np.random.randint(0, 60)
        dt = start_date + pd.Timedelta(days=random_days, hours=random_hours, minutes=random_minutes, seconds=random_seconds)
        dates.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
        
    # Transaction amounts
    amounts = np.round(np.random.uniform(15.5, 350.0, size=n_rows), 2)
    
    data = {
        'transaction_id': [f"TXN_{i:04d}" for i in range(1, n_rows + 1)],
        'customer_id': customer_ids,
        'transaction_date': dates,
        'amount': amounts
    }
    
    return pd.DataFrame(data)


# ---------------------------------------------------------
# TASK 1: Parse Timestamp Strings with Explicit Format (1 mark)
# ---------------------------------------------------------
def task_1_parse_timestamps(df):
    """
    Convert string timestamp column to datetime64[ns] type using an explicit format.
    Explicit format specification avoids silent date parsing corruption.
    """
    print("=" * 60)
    print("TASK 1: PARSE TIMESTAMP STRINGS WITH EXPLICIT FORMAT")
    print("=" * 60)
    
    format_string = '%Y-%m-%d %H:%M:%S'
    print(f"Explicit Format String Used: '{format_string}'")
    print("Rationale: Specifying explicit format string ensures predictable, fast,")
    print("and reliable datetime conversion without ambiguous parsing or silent date corruption.\n")
    
    print(f"Before parsing - dtype: {df['transaction_date'].dtype}")
    print("Sample raw dates before conversion:")
    print(df['transaction_date'].head(3).tolist())
    
    # Parse with explicit format string
    df['transaction_date'] = pd.to_datetime(
        df['transaction_date'],
        format=format_string
    )
    
    print(f"\nAfter parsing - dtype: {df['transaction_date'].dtype}")
    print(f"Min date: {df['transaction_date'].min()}")
    print(f"Max date: {df['transaction_date'].max()}")
    print(f"Verification: Dtype is datetime64? {'datetime64' in str(df['transaction_date'].dtype)}")
    
    return df


# ---------------------------------------------------------
# TASK 2: Extract Day-of-Week and Hour-of-Day (1 mark)
# ---------------------------------------------------------
def task_2_extract_day_and_hour(df):
    """
    Extract readable Day-of-Week and numeric Hour-of-Day features from parsed datetime.
    Display traffic distributions and save an hourly volume histogram plot.
    """
    print("\n" + "=" * 60)
    print("TASK 2: EXTRACT DAY-OF-WEEK AND HOUR-OF-DAY")
    print("=" * 60)
    
    # Extract temporal features
    df['day_of_week'] = df['transaction_date'].dt.day_name()
    df['dow_numeric'] = df['transaction_date'].dt.dayofweek
    df['hour'] = df['transaction_date'].dt.hour
    
    print("Extracted Features Sample:")
    print(df[['transaction_date', 'day_of_week', 'dow_numeric', 'hour']].head(5))
    
    print("\n--- Day of Week Transaction Distribution ---")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_volume = df['day_of_week'].value_counts().reindex(day_order).fillna(0).astype(int)
    print(daily_volume)
    
    print("\n--- Hourly Transaction Distribution (0-23) ---")
    hourly_volume = df.groupby('hour').size()
    print(hourly_volume)
    
    # Plot histogram / bar plot for hourly distribution
    try:
        plt.figure(figsize=(10, 5))
        hourly_volume.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Hourly Transaction Distribution (Peak Hours Analysis)', fontsize=14)
        plt.xlabel('Hour of Day (0-23)', fontsize=12)
        plt.ylabel('Transaction Count', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('hourly_distribution.png')
        plt.close()
        print("\nPlot saved: 'hourly_distribution.png'")
    except Exception as e:
        print(f"\nPlotting skipped or handled: {e}")
        
    return df


# ---------------------------------------------------------
# TASK 3: Compute Week Number and Resample Data (1 mark)
# ---------------------------------------------------------
def task_3_week_number_and_resample(df):
    """
    Extract ISO week number and perform resampling operations on datetime index.
    Compute weekly total revenue, transaction count, and mean transaction amount.
    """
    print("\n" + "=" * 60)
    print("TASK 3: COMPUTE WEEK NUMBER AND RESAMPLE DATA")
    print("=" * 60)
    
    # Extract week number
    df['week_num'] = df['transaction_date'].dt.isocalendar().week
    print(f"Unique weeks present in dataset: {sorted(df['week_num'].unique())}\n")
    
    # Set datetime as index for resampling operations
    df_ts = df.set_index('transaction_date')
    
    # Resample to weekly buckets ('W')
    weekly_metrics = df_ts['amount'].resample('W').agg(['sum', 'count', 'mean']).rename(
        columns={'sum': 'total_revenue', 'count': 'transaction_count', 'mean': 'avg_transaction_value'}
    )
    
    print("--- Weekly Resampled Trend Metrics ---")
    print(weekly_metrics)
    
    return df, weekly_metrics


# ---------------------------------------------------------
# TASK 4: Compute Days-Since-Event Metric (1 mark)
# ---------------------------------------------------------
def task_4_days_since_event(df):
    """
    Compute customer recency (days since last purchase) using datetime arithmetic.
    Identify customers with no recent activity for churn risk analysis.
    """
    print("\n" + "=" * 60)
    print("TASK 4: COMPUTE DAYS-SINCE-EVENT METRIC (RECENCY)")
    print("=" * 60)
    
    # Use fixed anchor date after dataset max date or current timestamp
    reference_today = pd.Timestamp('2025-02-16 00:00:00')
    print(f"Reference Date for Recency Calculation: {reference_today}\n")
    
    # Customer level last purchase
    customer_last_purchase = df.groupby('customer_id')['transaction_date'].max()
    
    # Datetime arithmetic to calculate days since last purchase
    recency_df = pd.DataFrame({
        'last_purchase_date': customer_last_purchase,
        'days_since_last_purchase': (reference_today - customer_last_purchase).dt.days
    }).reset_index()
    
    # Merge back to main DataFrame
    df = df.merge(recency_df[['customer_id', 'days_since_last_purchase']], on='customer_id', how='left')
    
    print("--- Recency Metric Summary Statistics ---")
    print(recency_df['days_since_last_purchase'].describe())
    
    # Churn risk threshold: > 20 days since last purchase
    churn_threshold = 20
    inactive_customers = recency_df[recency_df['days_since_last_purchase'] > churn_threshold]
    print(f"\nInactive / Churn Risk Customers (> {churn_threshold} days since purchase):")
    print(inactive_customers[['customer_id', 'last_purchase_date', 'days_since_last_purchase']])
    
    return df, recency_df


# ---------------------------------------------------------
# TASK 5: Build Time-Indexed Aggregation (1 mark)
# ---------------------------------------------------------
def task_5_time_indexed_aggregation(df):
    """
    Multi-dimensional aggregation by day_of_week and hour.
    Build pivot table for hour x day_of_week heatmap/matrix and identify peak activity windows.
    """
    print("\n" + "=" * 60)
    print("TASK 5: BUILD TIME-INDEXED AGGREGATION & PIVOT TABLE")
    print("=" * 60)
    
    # Multi-level groupby across temporal dimensions
    hourly_daily = df.groupby(['day_of_week', 'hour']).agg(
        total_amount=('amount', 'sum'),
        transaction_count=('amount', 'count'),
        avg_amount=('amount', 'mean')
    )
    
    print("--- Sample Multi-Level Temporal GroupBy (Day x Hour) ---")
    print(hourly_daily.head(10))
    
    # Pivot table for hour x day_of_week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_table = pd.pivot_table(
        df,
        values='amount',
        index='hour',
        columns='day_of_week',
        aggfunc='sum',
        fill_value=0
    )
    # Reindex columns to standard week order
    existing_days = [d for d in day_order if d in pivot_table.columns]
    pivot_table = pivot_table[existing_days]
    
    print("\n--- Pivot Table: Hourly Revenue by Day of Week ---")
    print(pivot_table)
    
    # Identify Peak Activity Windows
    top_slots = hourly_daily.sort_values(by='total_amount', ascending=False).head(3)
    print("\n--- Peak Activity Windows (Top 3 Day & Hour Combos by Revenue) ---")
    print(top_slots)
    
    return hourly_daily, pivot_table


# ---------------------------------------------------------
# TESTING & EDGE CASES HANDLING
# ---------------------------------------------------------
def test_edge_cases_and_timezones():
    """
    Test datetime parsing against non-standard format variations and multi-timezone timestamps.
    """
    print("\n" + "=" * 60)
    print("TESTING & EDGE CASES: FORMAT MISMATCHES AND TIMEZONES")
    print("=" * 60)
    
    test_dates = [
        '2025-01-15 14:30:45',        # Standard YYYY-MM-DD HH:MM:SS
        '2025-1-15 14:30:45',         # Single-digit month
        '15/01/2025 14:30:45',        # European format DD/MM/YYYY
        '2025-01-15T14:30:45Z',       # ISO format with UTC Z designation
    ]
    
    print("--- Format Matching Verification ---")
    for date_str in test_dates:
        try:
            parsed = pd.to_datetime(date_str, format='%Y-%m-%d %H:%M:%S')
            print(f"✓ '{date_str}' matched format '%Y-%m-%d %H:%M:%S' -> {parsed}")
        except Exception as e:
            # Fallback to flexible parsing or ISO conversion
            flexible_parsed = pd.to_datetime(date_str)
            print(f"✗ '{date_str}' mismatched format '%Y-%m-%d %H:%M:%S'. Flexible fallback -> {flexible_parsed}")
            
    print("\n--- Multi-Timezone Handling Demonstration ---")
    print("Best Practice: Store/Convert timestamps to UTC, then localize/convert to local target timezone prior to feature extraction.")
    tz_sample = pd.Series(['2025-01-15 14:30:45', '2025-01-15 09:30:45'])
    utc_dates = pd.to_datetime(tz_sample).dt.tz_localize('UTC')
    est_dates = utc_dates.dt.tz_convert('America/New_York')
    print("UTC Timestamps:")
    print(utc_dates)
    print("Converted to US/Eastern (America/New_York):")
    print(est_dates)


def run_pipeline():
    """Execute complete datetime feature engineering pipeline."""
    print("Creating sample transaction dataset...")
    df = create_sample_transaction_dataset()
    
    df = task_1_parse_timestamps(df)
    df = task_2_extract_day_and_hour(df)
    df, weekly_metrics = task_3_week_number_and_resample(df)
    df, recency_df = task_4_days_since_event(df)
    hourly_daily, pivot_table = task_5_time_indexed_aggregation(df)
    
    test_edge_cases_and_timezones()
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
