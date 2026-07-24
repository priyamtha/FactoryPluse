import time
import pandas as pd
import numpy as np

def create_sample_dataset(n_rows=100000):
    """
    Create synthetic customer revenue dataset with 100,000 rows
    to benchmark vectorization vs loop performance.
    """
    np.random.seed(42)
    revenue = np.round(np.random.exponential(scale=250, size=n_rows) + 10, 2)
    customer_ids = [f"CUST_{i:06d}" for i in range(1, n_rows + 1)]
    
    df = pd.DataFrame({
        'customer_id': customer_ids,
        'revenue': revenue
    })
    
    return df


# ---------------------------------------------------------
# TASK 1: Replace Loop with NumPy Vectorization (Min-Max) (1 mark)
# ---------------------------------------------------------
def task_1_min_max_vectorization(df):
    """
    Perform Min-Max normalization scaling values into range [0.0, 1.0]
    using vectorized NumPy array operations.
    """
    print("=" * 60)
    print("TASK 1: MIN-MAX NORMALIZATION WITH NUMPY VECTORIZATION")
    print("=" * 60)
    
    revenue_array = df['revenue'].values
    min_val = revenue_array.min()
    max_val = revenue_array.max()
    
    # Vectorized Min-Max formula: (x - min) / (max - min)
    normalized_np = (revenue_array - min_val) / (max_val - min_val)
    df['revenue_normalized'] = normalized_np
    
    print(f"Revenue Min: ${min_val:.2f}, Max: ${max_val:.2f}")
    print(f"Normalized Array Range: [{normalized_np.min():.4f}, {normalized_np.max():.4f}]")
    print("\nSample Min-Max Normalized Values:")
    print(df[['customer_id', 'revenue', 'revenue_normalized']].head(5))
    
    return df, normalized_np


# ---------------------------------------------------------
# TASK 2: Z-Score Normalization (1 mark)
# ---------------------------------------------------------
def task_2_zscore_vectorization(df):
    """
    Perform Z-Score standardization (mean = 0, std = 1)
    using vectorized NumPy array operations.
    """
    print("\n" + "=" * 60)
    print("TASK 2: Z-SCORE STANDARDIZATION WITH NUMPY VECTORIZATION")
    print("=" * 60)
    
    revenue_array = df['revenue'].values
    mean_val = revenue_array.mean()
    std_val = revenue_array.std()
    
    # Vectorized Z-score formula: (x - mean) / std
    z_scores = (revenue_array - mean_val) / std_val
    df['revenue_zscore'] = z_scores
    
    print(f"Revenue Mean: ${mean_val:.2f}, Std Dev: ${std_val:.2f}")
    print(f"Z-Score Output Mean: {z_scores.mean():.6f} (approx 0.0), Std Dev: {z_scores.std():.6f} (approx 1.0)")
    print("\nSample Z-Score Standardized Values:")
    print(df[['customer_id', 'revenue', 'revenue_zscore']].head(5))
    
    return df, z_scores


# ---------------------------------------------------------
# TASK 3: Bulk Ranking / Scoring (1 mark)
# ---------------------------------------------------------
def task_3_bulk_ranking(df):
    """
    Perform bulk customer ranking in descending order of revenue
    using np.argsort(). Assign 1-based customer ranks efficiently.
    """
    print("\n" + "=" * 60)
    print("TASK 3: BULK RANKING USING NUMPY ARGSORT")
    print("=" * 60)
    
    revenue_array = df['revenue'].values
    
    # Negative revenue array for descending sort indices
    sort_indices = np.argsort(-revenue_array)
    
    ranks = np.empty_like(sort_indices)
    ranks[sort_indices] = np.arange(1, len(sort_indices) + 1)
    
    df['revenue_rank'] = ranks
    
    print("Top 5 Highest Revenue Customers (Ranks 1 to 5):")
    top_5 = df.sort_values(by='revenue_rank').head(5)
    print(top_5[['customer_id', 'revenue', 'revenue_rank']])
    
    return df, ranks


# ---------------------------------------------------------
# TASK 4: Time Performance Comparison (1 mark)
# ---------------------------------------------------------
def task_4_time_performance_comparison(df):
    """
    Benchmark execution time: Python iterative loop vs NumPy SIMD vectorization.
    """
    print("\n" + "=" * 60)
    print("TASK 4: PERFORMANCE BENCHMARK (PYTHON LOOP VS NUMPY VECTORIZATION)")
    print("=" * 60)
    
    n_rows = len(df)
    print(f"Benchmarking operation (value * 1.1) over {n_rows:,} records...\n")
    
    # 1. Time Python Loop version
    start_loop = time.time()
    result_loop = []
    for val in df['revenue']:
        result_loop.append(val * 1.1)
    loop_time = time.time() - start_loop
    
    # 2. Time NumPy Vectorized version
    start_np = time.time()
    result_np = df['revenue'].values * 1.1
    np_time = time.time() - start_np
    
    speedup = loop_time / np_time if np_time > 0 else float('inf')
    
    print(f"Python Iterative Loop Time: {loop_time:.6f} seconds")
    print(f"NumPy Vectorized Time:     {np_time:.6f} seconds")
    print(f"Performance Speedup Factor:  {speedup:.1f}x faster!")
    
    return loop_time, np_time, speedup


# ---------------------------------------------------------
# TASK 5: Integrate Back to DataFrame & Verify (1 mark)
# ---------------------------------------------------------
def task_5_integrate_and_verify(df, normalized_np, z_scores, ranks):
    """
    Assign all computed NumPy array metrics back into Pandas DataFrame columns.
    Verify shape, memory alignment, and data types.
    """
    print("\n" + "=" * 60)
    print("TASK 5: INTEGRATE NUMPY RESULTS BACK TO DATAFRAME & VERIFY")
    print("=" * 60)
    
    df['revenue_normalized'] = normalized_np
    df['revenue_zscore'] = z_scores
    df['revenue_rank'] = ranks
    
    print(f"Final DataFrame Shape: {df.shape}")
    print("\nFinal Column Data Types (dtypes):")
    print(df.dtypes)
    
    print("\nFinal Clean DataFrame Head:")
    print(df.head(5))
    
    return df


def run_pipeline():
    """Execute complete NumPy Vectorization & Performance Optimization Pipeline."""
    print("Creating sample dataset with 100,000 rows...")
    df = create_sample_dataset(n_rows=100000)
    
    df, normalized_np = task_1_min_max_vectorization(df)
    df, z_scores = task_2_zscore_vectorization(df)
    df, ranks = task_3_bulk_ranking(df)
    loop_time, np_time, speedup = task_4_time_performance_comparison(df)
    task_5_integrate_and_verify(df, normalized_np, z_scores, ranks)
    
    print("\n" + "=" * 60)
    print("NUMPY VECTORIZATION PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
