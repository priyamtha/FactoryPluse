import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def create_sample_dataset():
    """
    Generate synthetic transactions dataset spanning 30 days.
    On day index 20 (Tuesday, 10 days ago), we inject a massive drop:
    - Daily revenue drops to $2,000 (normally ~$10,000)
    - Daily transactions drop to 40 (normally ~200)
    - Daily signups drop to 4 (normally ~30)
    This will serve as our primary business and statistical anomaly.
    """
    np.random.seed(42)
    end_date = pd.Timestamp.now().normalize()
    start_date = end_date - pd.Timedelta(days=29)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    records = []
    
    for i, date in enumerate(dates):
        # Inject anomaly on day index 20 (Tuesday, 10 days ago)
        is_anomaly_day = (i == 20)
        
        if is_anomaly_day:
            n_tx = 40
            # Generate amounts that sum exactly to $2,000
            amounts = np.random.normal(50, 5, size=n_tx)
            amounts = amounts * (2000 / sum(amounts))
            signups = 4
        else:
            n_tx = np.random.randint(180, 220)
            amounts = np.random.normal(50, 8, size=n_tx)
            # Normal revenue target centered at $10,000
            daily_target = np.random.normal(10000, 500)
            amounts = amounts * (daily_target / sum(amounts))
            signups = np.random.randint(22, 38)
            
        for tx_idx, amt in enumerate(amounts):
            records.append({
                'date': date,
                'amount': round(amt, 2),
                'signup': 1 if tx_idx < signups else 0
            })
            
    return pd.DataFrame(records)


# ---------------------------------------------------------
# TASK 1: Threshold-Based Anomaly Detection (1 mark)
# ---------------------------------------------------------
def check_thresholds(metrics, rules):
    """Alert if metrics outside business thresholds."""
    alerts = []
    for metric_name, rule in rules.items():
        value = metrics[metric_name]
        if value < rule['min']:
            alerts.append({
                'metric': metric_name,
                'value': value,
                'threshold': rule['min'],
                'direction': 'BELOW_MIN',
                'severity': 'HIGH'
            })
        elif value > rule['max']:
            alerts.append({
                'metric': metric_name,
                'value': value,
                'threshold': rule['max'],
                'direction': 'ABOVE_MAX',
                'severity': 'MEDIUM'
            })
    return alerts


def run_threshold_alerts(df):
    """Extract today's metrics (anomaly day) and check thresholds."""
    print("=" * 60)
    print("TASK 1: THRESHOLD-BASED ANOMALY DETECTION")
    print("=" * 60)
    
    # Calculate daily summaries
    daily_revenue = df.groupby('date')['amount'].sum()
    daily_tx_count = df.groupby('date')['amount'].count()
    daily_signup_rate = df.groupby('date')['signup'].sum()
    
    # Find anomaly date (day index 20)
    anomaly_date = daily_revenue.index[20]
    
    # Extract metrics for the anomaly day
    anomaly_metrics = {
        'daily_revenue': float(daily_revenue.loc[anomaly_date]),
        'transaction_count': int(daily_tx_count.loc[anomaly_date]),
        'signup_rate': int(daily_signup_rate.loc[anomaly_date])
    }
    
    alert_rules = {
        'daily_revenue': {'min': 5000, 'max': 50000},
        'transaction_count': {'min': 100, 'max': 10000},
        'signup_rate': {'min': 10, 'max': 500}
    }
    
    alerts = check_thresholds(anomaly_metrics, alert_rules)
    print(f"Metrics evaluated for date {anomaly_date.strftime('%Y-%m-%d')}:")
    print(f" - Revenue: ${anomaly_metrics['daily_revenue']:,.2f}")
    print(f" - Transactions: {anomaly_metrics['transaction_count']:,}")
    print(f" - Signups: {anomaly_metrics['signup_rate']:,}\n")
    
    print("Generated Alerts:")
    for alert in alerts:
        print(f" [ALERT] {alert['metric']} {alert['direction']}: {alert['value']} (threshold: {alert['threshold']})")
        
    return alerts


# ---------------------------------------------------------
# TASK 2: Statistical Anomaly Detection with Z-Score (1 mark)
# ---------------------------------------------------------
def detect_anomalies_zscore(series, threshold=2):
    """Flag values > N std dev from mean."""
    mean = series.mean()
    std = series.std()
    z_scores = np.abs((series - mean) / std)
    anomalies = series[z_scores > threshold]
    return anomalies, z_scores


def run_zscore_detection(df):
    """Perform z-score analysis on daily revenue."""
    print("\n" + "=" * 60)
    print("TASK 2: STATISTICAL ANOMALY DETECTION WITH Z-SCORE")
    print("=" * 60)
    
    # Compute daily revenue for last 30 days
    daily_revenue = df.groupby('date')['amount'].sum().tail(30)
    
    anomalies, z_scores = detect_anomalies_zscore(daily_revenue, threshold=2)
    
    print(f"Detected {len(anomalies)} anomalies out of {len(daily_revenue)} days")
    for date, value in anomalies.items():
        print(f"  {date.strftime('%Y-%m-%d')}: ${value:,.2f} (z-score: {z_scores[date]:.2f})")
        
    return daily_revenue, anomalies, z_scores


# ---------------------------------------------------------
# TASK 3: Severity Classification (1 mark)
# ---------------------------------------------------------
def classify_severity(value, mean, std):
    """Classify anomaly severity based on deviation."""
    z_score = abs((value - mean) / std)
    
    if z_score > 3:
        return 'CRITICAL'
    elif z_score > 2:
        return 'HIGH'
    elif z_score > 1.5:
        return 'MEDIUM'
    else:
        return 'LOW'


def run_severity_classification(daily_revenue, anomalies, z_scores):
    """Categorize and filter detected anomalies by severity."""
    print("\n" + "=" * 60)
    print("TASK 3: SEVERITY CLASSIFICATION")
    print("=" * 60)
    
    mean_val = daily_revenue.mean()
    std_val = daily_revenue.std()
    
    anomaly_severity = []
    for date, value in anomalies.items():
        severity = classify_severity(value, mean_val, std_val)
        anomaly_severity.append({
            'date': date.strftime('%Y-%m-%d'),
            'value': f"${value:,.2f}",
            'z_score': round(z_scores[date], 2),
            'severity': severity
        })
        
    severity_df = pd.DataFrame(anomaly_severity)
    print("Anomaly Severity Breakdown:")
    print(severity_df.to_string(index=False))
    
    # Alert only on HIGH+ severity anomalies
    critical = severity_df[severity_df['severity'].isin(['CRITICAL', 'HIGH'])]
    print(f"\n[ALERT] {len(critical)} critical anomalies require investigation")
    
    return severity_df, critical


# ---------------------------------------------------------
# TASK 4: Anomaly Logging and Audit Trail (1 mark)
# ---------------------------------------------------------
def run_anomaly_logging(daily_revenue, anomalies, z_scores, output_path='anomalies_log.csv'):
    """Create persistent audit log with status tracking."""
    print("\n" + "=" * 60)
    print("TASK 4: ANOMALY LOGGING AND AUDIT TRAIL")
    print("=" * 60)
    
    mean_val = daily_revenue.mean()
    std_val = daily_revenue.std()
    
    anomaly_log = []
    for date, value in anomalies.items():
        severity = classify_severity(value, mean_val, std_val)
        expected_min = max(0, mean_val - 2 * std_val)
        expected_max = mean_val + 2 * std_val
        
        anomaly_log.append({
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'anomaly_date': date.strftime('%Y-%m-%d'),
            'metric': 'daily_revenue',
            'value': round(value, 2),
            'expected_range': f"{expected_min:.0f}-{expected_max:.0f}",
            'z_score': round(z_scores[date], 2),
            'severity': severity,
            'status': 'OPEN'  # OPEN, INVESTIGATED, RESOLVED
        })
        
    anomalies_df = pd.DataFrame(anomaly_log)
    
    # Save log to root and output/
    anomalies_df.to_csv(output_path, index=False)
    os.makedirs('output', exist_ok=True)
    anomalies_df.to_csv(os.path.join('output', output_path), index=False)
    
    print(f"Logged {len(anomalies_df)} anomalies successfully to: '{output_path}' and 'output/{output_path}'")
    return anomalies_df


# ---------------------------------------------------------
# TASK 5: Visualization with Flagged Points (1 mark)
# ---------------------------------------------------------
def task_5_visualize_anomalies(daily_revenue, anomalies, z_scores, output_path='anomaly_detection.png'):
    """
    Plot raw values, 7-day moving average, expected ranges (mean ± 2σ), and flag anomalies.
    """
    print("\n" + "=" * 60)
    print("TASK 5: VISUALIZATION WITH FLAGGED POINTS")
    print("=" * 60)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Format the dates on x-axis nicely
    date_strs = [d.strftime('%Y-%m-%d') for d in daily_revenue.index]
    
    # Plot daily values
    ax.plot(date_strs, daily_revenue.values, marker='o', label='Daily Revenue', color='#2563eb', linewidth=2)
    
    # Plot rolling average (7-day MA)
    rolling_avg = daily_revenue.rolling(window=7).mean()
    ax.plot(date_strs, rolling_avg.values, label='7-day MA', color='#10b981', linewidth=2, linestyle='--')
    
    # Highlight anomalies with a red X
    for date, value in anomalies.items():
        date_str = date.strftime('%Y-%m-%d')
        ax.scatter(date_str, value, color='#ef4444', s=200, marker='X', zorder=5, label='Anomaly Flagged')
        ax.annotate('ANOMALY', (date_str, value), xytext=(0, 12), 
                    textcoords='offset points', ha='center', fontweight='bold', color='#ef4444')
                    
    # Shade expected range (mean ± 2σ)
    mean_val = daily_revenue.mean()
    std_val = daily_revenue.std()
    expected_min = mean_val - 2 * std_val
    expected_max = mean_val + 2 * std_val
    
    ax.axhline(mean_val, color='#94a3b8', linestyle=':', label='Historical Mean')
    ax.fill_between(date_strs, expected_min, expected_max, alpha=0.15, color='#3b82f6', label='Expected Range ±2σ')
    
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Revenue ($)', fontsize=11)
    ax.set_title('Daily Revenue with Anomalies Flagged', fontsize=13, fontweight='bold', pad=15)
    
    # Dedup legend labels
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right', frameon=True)
    
    ax.grid(True, linestyle=':', alpha=0.5)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the figure to both paths
    plt.savefig(output_path, dpi=150)
    plt.savefig(os.path.join('output', output_path), dpi=150)
    plt.close()
    
    print(f"Anomaly visualization saved to: '{output_path}' and 'output/{output_path}'")


def run_pipeline():
    """Execute complete anomaly detection and alerting workflow."""
    print("Generating transactional dataset...")
    df = create_sample_dataset()
    
    # Task 1
    run_threshold_alerts(df)
    
    # Task 2
    daily_revenue, anomalies, z_scores = run_zscore_detection(df)
    
    # Task 3
    run_severity_classification(daily_revenue, anomalies, z_scores)
    
    # Task 4
    run_anomaly_logging(daily_revenue, anomalies, z_scores, output_path='anomalies_log.csv')
    
    # Task 5
    task_5_visualize_anomalies(daily_revenue, anomalies, z_scores, output_path='anomaly_detection.png')
    
    print("\n" + "=" * 60)
    print("ANOMALY DETECTION PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
