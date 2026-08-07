"""
Task 1, 2 & 3: Automated Metrics Validation Script (Python)
-----------------------------------------------------------
Cross-validates key business metrics between SQL and Python layers,
flags discrepancies based on tolerance thresholds, and outputs
a daily audit log to validation_report.csv.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

def get_db_connection():
    return sqlite3.connect('analytics.db')

def compute_python_churn(orders_df, current_date=None):
    """
    Computes monthly churn in Python:
    Customers who had spending > 0 in Month N-1, but placed 0 orders in Month N.
    """
    if current_date is None:
        current_date = date.today()
        
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    # Calculate Month N-1 and Month N bounds
    first_of_current_month = pd.Timestamp(current_date.year, current_date.month, 1)
    
    if current_date.month == 1:
        first_of_prev_month = pd.Timestamp(current_date.year - 1, 12, 1)
    else:
        first_of_prev_month = pd.Timestamp(current_date.year, current_date.month - 1, 1)
        
    # Month N-1 active spending customers
    prev_month_df = orders_df[
        (orders_df['order_date'] >= first_of_prev_month) & 
        (orders_df['order_date'] < first_of_current_month) & 
        (orders_df['order_amount'] > 0)
    ]
    prev_month_customers = set(prev_month_df['customer_id'].unique())
    
    # Month N active customers
    curr_month_df = orders_df[
        (orders_df['order_date'] >= first_of_current_month)
    ]
    curr_month_customers = set(curr_month_df['customer_id'].unique())
    
    # Set difference: Active in N-1 but NOT active in N
    churned_customers = prev_month_customers - curr_month_customers
    return len(churned_customers)

def validate_metrics(conn, tolerance_pct=0.1):
    """
    Validate that SQL and Python compute identical metrics.
    
    Args:
        conn: SQLite database connection
        tolerance_pct: Acceptable percentage difference (default 0.1%)
        
    Returns:
        validation_report: DataFrame with all metrics and match status
    """
    # Read source dataframes into pandas memory
    logins_df = pd.read_sql("SELECT * FROM logins", conn)
    orders_df = pd.read_sql("SELECT * FROM orders", conn)
    
    cutoff_30d = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Define metrics dictionary to validate
    metrics = {
        'active_users_30d': {
            'sql': "SELECT COUNT(DISTINCT user_id) FROM logins WHERE login_date >= date('now', '-30 days')",
            'python': lambda: logins_df[logins_df['login_date'] >= cutoff_30d]['user_id'].nunique(),
            'tolerance': 0
        },
        'aov': {
            'sql': "SELECT AVG(order_amount) FROM orders",
            'python': lambda: float(orders_df['order_amount'].mean()),
            'tolerance': 0.1
        },
        'churn_monthly_flawed': {
            'sql': """
                SELECT COUNT(DISTINCT c1.customer_id)
                FROM (
                    SELECT DISTINCT customer_id
                    FROM orders
                    WHERE strftime('%m', order_date) = strftime('%m', date('now', '-1 month'))
                      AND order_amount > 0
                ) c1
                LEFT JOIN (
                    SELECT DISTINCT customer_id
                    FROM orders
                    WHERE strftime('%m', order_date) = strftime('%m', 'now')
                ) c2 ON c1.customer_id = c2.customer_id
                WHERE c2.customer_id IS NULL;
            """,
            'python': lambda: compute_python_churn(orders_df),
            'tolerance': 0
        },
        'churn_monthly_fixed': {
            'sql': """
                WITH prev_month_custs AS (
                    SELECT DISTINCT customer_id
                    FROM orders
                    WHERE order_date >= date('now', 'start of month', '-1 month')
                      AND order_date < date('now', 'start of month')
                      AND order_amount > 0
                ),
                curr_month_custs AS (
                    SELECT DISTINCT customer_id
                    FROM orders
                    WHERE order_date >= date('now', 'start of month')
                )
                SELECT COUNT(DISTINCT p.customer_id)
                FROM prev_month_custs p
                LEFT JOIN curr_month_custs c ON p.customer_id = c.customer_id
                WHERE c.customer_id IS NULL;
            """,
            'python': lambda: compute_python_churn(orders_df),
            'tolerance': 0
        }
    }
    
    validation_report = []
    
    for metric_name, metric_def in metrics.items():
        sql_result = float(pd.read_sql(metric_def['sql'], conn).iloc[0, 0])
        py_result = float(metric_def['python']())
        
        difference = abs(sql_result - py_result)
        pct_diff = (difference / abs(sql_result)) * 100 if sql_result != 0 else 0.0
        
        match = pct_diff <= metric_def['tolerance']
        
        validation_report.append({
            'Metric': metric_name,
            'SQL': round(sql_result, 2),
            'Python': round(py_result, 2),
            'Difference': round(difference, 4),
            'Pct_Difference': round(pct_diff, 2),
            'Tolerance': metric_def['tolerance'],
            'Status': 'PASS' if match else 'FAIL',
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return pd.DataFrame(validation_report)

if __name__ == "__main__":
    conn = get_db_connection()
    report_df = validate_metrics(conn)
    
    print("\n=================================================================")
    print("Metrics Cross-Validation Report:")
    print("=================================================================")
    print(report_df.to_string(index=False))
    
    # Save validation report
    report_df.to_csv('validation_report.csv', index=False)
    print("\nReport saved to validation_report.csv")
