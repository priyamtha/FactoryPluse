import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, inspect

def create_cleaned_customer_dataset(n_rows=1000):
    """
    Generate a synthetic cleaned customer profile dataset:
    - customer_id: sequential integers starting at 1000
    - email: standard email address strings
    - signup_date: date objects in the past year
    - customer_type: segment classification (Enterprise, SMB, Startup)
    - lifetime_value: realistic segment-specific revenue distribution
    """
    np.random.seed(42)
    customer_ids = np.arange(1000, 1000 + n_rows)
    emails = [f"customer_{cid}@example.com" for cid in customer_ids]
    
    # Dates in the past year
    base_date = pd.Timestamp('2025-01-01')
    date_offsets = np.random.randint(0, 365, size=n_rows)
    signup_dates = [base_date + pd.Timedelta(days=int(offset)) for offset in date_offsets]
    
    # Convert signup dates to date format (yyyy-mm-dd) for SQLite validation matching
    signup_dates = [d.date() for d in signup_dates]
    
    customer_types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n_rows, p=[0.05, 0.40, 0.55])
    
    ltv_list = []
    for ct in customer_types:
        if ct == 'Enterprise':
            ltv = np.random.normal(150000, 10000)
        elif ct == 'SMB':
            ltv = np.random.normal(8000, 800)
        else: # Startup
            ltv = np.random.normal(2000, 200)
        ltv_list.append(round(max(ltv, 100.0), 2))
        
    df = pd.DataFrame({
        'customer_id': customer_ids.astype(int),
        'email': emails,
        'signup_date': signup_dates,
        'customer_type': customer_types,
        'lifetime_value': ltv_list
    })
    
    return df


# ---------------------------------------------------------
# TASK 1: Setup Database Connection (1 mark)
# ---------------------------------------------------------
def task_1_setup_connection(database_path='analytics.db'):
    """
    Setup SQLite database engine using SQLAlchemy.
    Verifies that database connection is successfully tested.
    """
    print("=" * 60)
    print("TASK 1: SETUP DATABASE CONNECTION")
    print("=" * 60)
    
    # SQLite file connection string - zero setup and local file persistence
    connection_str = f"sqlite:///{database_path}"
    print(f"Database connection string configured: '{connection_str}'")
    
    engine = create_engine(connection_str)
    
    # Test connection by acquiring connection context
    with engine.connect() as conn:
        print("[SUCCESS] Database connection tested successfully")
        
    return engine


# ---------------------------------------------------------
# TASK 2: Load Cleaned DataFrame as Table (1 mark)
# ---------------------------------------------------------
def task_2_load_dataframe(df_clean, engine):
    """
    Load cleaned customer DataFrame to database table.
    Inspects table presence and verifies row count.
    Supports SQLAlchemy 2.0+ by using standard inspector helper.
    """
    print("\n" + "=" * 60)
    print("TASK 2: LOAD CLEANED DATAFRAME AS TABLE")
    print("=" * 60)
    
    # Load DataFrame to table
    df_clean.to_sql('customers_cleaned', engine, if_exists='replace', index=False)
    
    # Verify table exists in the database
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Verified tables in database: {tables}")
    
    # Check row count
    count_df = pd.read_sql("SELECT COUNT(*) as row_count FROM customers_cleaned", engine)
    rows_loaded = count_df.iloc[0]['row_count']
    print(f"Rows loaded into table: {rows_loaded}")
    
    return rows_loaded


# ---------------------------------------------------------
# TASK 3: Validate Schema (1 mark)
# ---------------------------------------------------------
def task_3_validate_schema(engine):
    """
    Inspect the schema of the loaded table and check column datatypes.
    Ensures primary columns match target validation constraints.
    """
    print("\n" + "=" * 60)
    print("TASK 3: VALIDATE SCHEMA")
    print("=" * 60)
    
    inspector = inspect(engine)
    columns = inspector.get_columns('customers_cleaned')
    
    print("TABLE SCHEMA INSPECTION:")
    for col in columns:
        null_constraint = "NOT NULL" if col['nullable'] == False else "NULL"
        print(f"  {col['name']:20} {str(col['type']):15} {null_constraint}")
        
    # Verify column datatypes
    print("\nDATATYPE VALIDATION STATUS:")
    expected_types = {
        'customer_id': 'INTEGER',
        'email': 'VARCHAR',
        'signup_date': 'DATE'
    }
    
    for col_name, expected_type in expected_types.items():
        # Match columns in inspector output
        match_cols = [c for c in columns if c['name'] == col_name]
        
        if len(match_cols) > 0:
            actual_type = match_cols[0]['type']
            actual_type_str = str(actual_type).upper()
            
            # Accommodate SQLite types:
            # - customer_id matches INTEGER
            # - email VARCHAR can map to TEXT or VARCHAR in SQLite
            # - signup_date DATE can map to DATE or DATETIME/TIMESTAMP depending on pandas storage
            is_valid = False
            if expected_type == 'INTEGER' and 'INT' in actual_type_str:
                is_valid = True
            elif expected_type == 'VARCHAR' and ('TEXT' in actual_type_str or 'CHAR' in actual_type_str):
                is_valid = True
            elif expected_type == 'DATE' and ('DATE' in actual_type_str or 'TIME' in actual_type_str or 'TIMESTAMP' in actual_type_str):
                is_valid = True
                
            status = '[PASS]' if is_valid else '[FAIL]'
            print(f" {status} {col_name}: expected {expected_type}, actual database type is {actual_type}")
        else:
            print(f" [FAIL] Expected column '{col_name}' was not found in the database table schema")


# ---------------------------------------------------------
# TASK 4: Query and Return Results (1 mark)
# ---------------------------------------------------------
def task_4_query_database(engine):
    """
    Execute SELECT queries from Python to retrieve data into Pandas DataFrames.
    Runs a simple filter query and an analytical aggregation query.
    """
    print("\n" + "=" * 60)
    print("TASK 4: QUERY AND RETURN RESULTS")
    print("=" * 60)
    
    # 1. Simple query: Filter by customer type
    query = "SELECT * FROM customers_cleaned WHERE customer_type = 'Enterprise'"
    results_df = pd.read_sql(query, engine)
    
    print(f"Simple query returned {len(results_df)} rows for segment 'Enterprise'")
    print("Preview of simple query:")
    print(results_df.head())
    
    # 2. Aggregation query: Group by segment and compute counts + average LTVs
    query_agg = """
    SELECT 
        customer_type,
        COUNT(*) as count,
        AVG(lifetime_value) as avg_ltv
    FROM customers_cleaned
    GROUP BY customer_type
    ORDER BY avg_ltv DESC
    """
    summary_df = pd.read_sql(query_agg, engine)
    
    print("\nSummary statistics by segment (agg query):")
    print(summary_df)
    
    return results_df, summary_df


# ---------------------------------------------------------
# TASK 5: Make Loading Repeatable (1 mark)
# ---------------------------------------------------------
def load_cleaned_data_to_database(df, table_name, database_path='analytics.db'):
    """Load cleaned DataFrame to database - repeatable function."""
    engine = create_engine(f'sqlite:///{database_path}')
    
    # Load with replace to handle overwrite scenarios
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    
    # Validate count
    count_df = pd.read_sql(f"SELECT COUNT(*) as ct FROM {table_name}", engine)
    rows_loaded = count_df.iloc[0]['ct']
    
    print(f"[SUCCESS] Loaded {rows_loaded} rows to {table_name}")
    return engine


def run_pipeline():
    """Execute complete Database Storage & Integration Pipeline."""
    print("Generating synthetic cleaned customer profiles (1,000 rows)...")
    df_clean = create_cleaned_customer_dataset(n_rows=1000)
    
    # Execute Tasks
    engine = task_1_setup_connection(database_path='analytics.db')
    task_2_load_dataframe(df_clean, engine)
    task_3_validate_schema(engine)
    task_4_query_database(engine)
    
    print("\n" + "=" * 60)
    print("TASK 5: MAKE LOADING REPEATABLE (REPEAT TEST)")
    print("=" * 60)
    # Test task 5 repeatable function
    repeatable_engine = load_cleaned_data_to_database(df_clean, 'customers_cleaned')
    
    # Query limit 10 using returned engine
    test_results = pd.read_sql("SELECT * FROM customers_cleaned LIMIT 10", repeatable_engine)
    print("Repeatable load output validation successful. Preview of 10 rows:")
    print(test_results[['customer_id', 'email', 'signup_date', 'customer_type', 'lifetime_value']].to_string())
    
    print("\n" + "=" * 60)
    print("DATABASE INTEGRATION PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
