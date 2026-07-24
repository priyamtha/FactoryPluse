import os
import numpy as np
import pandas as pd

def generate_synthetic_data(output_path="data/raw_revenue.csv"):
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    # 6 months of daily data (from Jan 1, 2026 to Jun 30, 2026)
    dates = pd.date_range(start="2026-01-01", end="2026-06-30", freq="D")
    n_days = len(dates)
    
    # Underlying trend: slowly increasing over time from $10k to ~$12.7k
    # base(t) = 10000 + 15 * t
    t = np.arange(n_days)
    base_revenue = 10000 + 15 * t
    
    # Weekly seasonality: lower on weekends, higher mid-week
    # weekday: Mon=0, Tue=1, ..., Sun=6
    # Let's adjust based on day of week:
    # Wed/Thu +10%, Sat/Sun -20%
    day_adjustments = {
        0: 1.0,   # Monday
        1: 1.05,  # Tuesday
        2: 1.10,  # Wednesday
        3: 1.10,  # Thursday
        4: 1.05,  # Friday
        5: 0.80,  # Saturday
        6: 0.80   # Sunday
    }
    
    seasonality = np.array([day_adjustments[d.weekday()] for d in dates])
    
    # Daily random noise (std deviation of $1500)
    noise = np.random.normal(0, 1500, n_days)
    
    # Combine components
    revenue = base_revenue * seasonality + noise
    
    # Ensure revenue doesn't drop below $2k for realistic values
    revenue = np.maximum(revenue, 2000)
    
    # Round to 2 decimal places
    revenue = np.round(revenue, 2)
    
    # Orders count: proportional to revenue, approx $50 average order value, with some noise
    orders = np.round(revenue / 50.0 + np.random.normal(0, 8, n_days))
    orders = np.maximum(orders, 10).astype(int)  # At least 10 orders/day
    
    # Create DataFrame
    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "revenue": revenue,
        "orders": orders
    })
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Dataset generated and saved to {output_path}")
    print(f"Total days: {n_days}")
    print(f"Revenue sample: ${df['revenue'].iloc[0]:,.2f}, ${df['revenue'].iloc[1]:,.2f}, ${df['revenue'].iloc[2]:,.2f}")

if __name__ == "__main__":
    generate_synthetic_data()
