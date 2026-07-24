import os
import pandas as pd
import numpy as np

def create_sample_dataset():
    """
    Create synthetic marketing campaign & customer dataset containing intentional validation failures:
    - Future birth dates (2050) & invalid age values
    - Negative prices (-$49.99)
    - Missing customer IDs & missing/malformed emails
    - Invalid phone number formats
    - Campaign end dates occurring before start dates
    """
    data = {
        'customer_id': ['CUST001', 'CUST002', None, 'CUST004', 'CUST005', 'CUST006', 'CUST007'],
        'age': [25, 42, -5, 185, 30, 29, 35],
        'price': [199.99, -49.99, 299.00, 0.00, 150.50, -10.00, 89.99],
        'birth_date': ['1998-05-12', '1981-11-03', '2050-01-01', '1910-04-20', '1993-08-15', '1994-12-01', '1988-03-22'],
        'email': ['alice@example.com', 'bob.domain.com', 'charlie@test.org', None, 'eve@company.com', 'frank@net.co', 'grace@web.org'],
        'phone': ['1234567890', '9876543210', '12345', '5556667777', '9998887777', 'invalid_phone', '1112223333'],
        'start_date': ['2025-01-01', '2025-01-10', '2025-02-01', '2025-01-15', '2025-03-01', '2025-01-20', '2025-02-10'],
        'end_date':   ['2025-01-15', '2025-01-05', '2025-02-28', '2025-01-10', '2025-03-15', '2025-01-25', '2025-02-20']
    }
    
    df = pd.DataFrame(data)
    # Convert date columns to datetime
    df['birth_date'] = pd.to_datetime(df['birth_date'])
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    
    return df


# ---------------------------------------------------------
# TASK 1: Range Checks (1 mark)
# ---------------------------------------------------------
def task_1_range_checks(df):
    """
    Validate numeric and temporal range constraints:
    - Age between 0 and 150
    - Price >= 0
    - Birth date between 1920-01-01 and current timestamp
    """
    print("=" * 60)
    print("TASK 1: RANGE CHECKS")
    print("=" * 60)
    
    current_time = pd.Timestamp.now()
    
    df['valid_age'] = (df['age'] >= 0) & (df['age'] <= 150)
    df['valid_price'] = df['price'] >= 0
    df['valid_birth_date'] = (df['birth_date'] >= '1920-01-01') & (df['birth_date'] <= current_time)
    
    print(f"Invalid age records: {(~df['valid_age']).sum()}")
    print(f"Invalid price records (negative price): {(~df['valid_price']).sum()}")
    print(f"Invalid birth_date records (future/pre-1920): {(~df['valid_birth_date']).sum()}")
    
    print("\nRange Check Violations Detail:")
    range_violations = df[~df['valid_age'] | ~df['valid_price'] | ~df['valid_birth_date']]
    print(range_violations[['customer_id', 'age', 'price', 'birth_date', 'valid_age', 'valid_price', 'valid_birth_date']])
    
    return df


# ---------------------------------------------------------
# TASK 2: Null Constraints (1 mark)
# ---------------------------------------------------------
def task_2_null_constraints(df):
    """
    Validate mandatory non-null requirements for primary key & critical contact fields:
    - customer_id must not be null
    - email must not be null
    """
    print("\n" + "=" * 60)
    print("TASK 2: NULL CONSTRAINTS")
    print("=" * 60)
    
    df['valid_customer_id'] = df['customer_id'].notna()
    df['valid_email_not_null'] = df['email'].notna()
    
    print(f"Missing customer_id count: {(~df['valid_customer_id']).sum()}")
    print(f"Missing email count: {(~df['valid_email_not_null']).sum()}")
    
    print("\nNull Constraint Violations Detail:")
    null_violations = df[~df['valid_customer_id'] | ~df['valid_email_not_null']]
    print(null_violations[['customer_id', 'email', 'valid_customer_id', 'valid_email_not_null']])
    
    return df


# ---------------------------------------------------------
# TASK 3: Format Pattern Validation (1 mark)
# ---------------------------------------------------------
def task_3_format_validation(df):
    """
    Validate text formatting using regular expression matching:
    - Email format contains '@'
    - Phone number matches exactly 10 digits (r'^\d{10}$')
    """
    print("\n" + "=" * 60)
    print("TASK 3: FORMAT PATTERN VALIDATION")
    print("=" * 60)
    
    df['valid_email_format'] = df['email'].str.contains('@', na=False)
    df['valid_phone'] = df['phone'].str.match(r'^\d{10}$', na=False)
    
    print(f"Invalid email format count: {(~df['valid_email_format']).sum()}")
    print(f"Invalid phone number format count: {(~df['valid_phone']).sum()}")
    
    print("\nFormat Pattern Violations Detail:")
    format_violations = df[~df['valid_email_format'] | ~df['valid_phone']]
    print(format_violations[['customer_id', 'email', 'phone', 'valid_email_format', 'valid_phone']])
    
    return df


# ---------------------------------------------------------
# TASK 4: Business Rule Validation (1 mark)
# ---------------------------------------------------------
def task_4_business_rule_validation(df):
    """
    Validate relational multi-column business logic rules:
    - Campaign end_date must be greater than or equal to start_date
    """
    print("\n" + "=" * 60)
    print("TASK 4: BUSINESS RULE VALIDATION (RELATIONAL DATE ORDERING)")
    print("=" * 60)
    
    df['valid_date_order'] = df['end_date'] >= df['start_date']
    
    print(f"Invalid campaign date range ordering count: {(~df['valid_date_order']).sum()}")
    
    print("\nBusiness Rule Violations Detail:")
    date_order_violations = df[~df['valid_date_order']]
    print(date_order_violations[['customer_id', 'start_date', 'end_date', 'valid_date_order']])
    
    return df


# ---------------------------------------------------------
# TASK 5: Validation Report & Failure Isolation (1 mark)
# ---------------------------------------------------------
def task_5_validation_report(df, output_path='output/validation_failures.csv'):
    """
    Combine all validation checks, isolate failing records,
    export failure report, and produce clean subset for downstream analysis.
    """
    print("\n" + "=" * 60)
    print("TASK 5: VALIDATION REPORT & FAILURE ISOLATION")
    print("=" * 60)
    
    validation_cols = [
        'valid_age',
        'valid_price',
        'valid_birth_date',
        'valid_customer_id',
        'valid_email_not_null',
        'valid_email_format',
        'valid_phone',
        'valid_date_order'
    ]
    
    df['passes_all_checks'] = df[validation_cols].all(axis=1)
    
    failures = df[~df['passes_all_checks']]
    df_clean = df[df['passes_all_checks']]
    
    # Save failures report
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    failures.to_csv(output_path, index=False)
    
    total_records = len(df)
    passed_count = df['passes_all_checks'].sum()
    failed_count = total_records - passed_count
    pass_rate = (passed_count / total_records) * 100
    
    print("--- EXECUTIVE VALIDATION REPORT SUMMARY ---")
    print(f"Total Dataset Records Processed: {total_records}")
    print(f"Records Passing All Checks:     {passed_count} ({pass_rate:.1f}%)")
    print(f"Records Failing Validation:     {failed_count} ({100 - pass_rate:.1f}%)")
    print(f"Validation Failures exported to: '{output_path}'")
    
    print("\n--- Failure Breakdown by Rule ---")
    for col in validation_cols:
        fail_cnt = (~df[col]).sum()
        print(f"  • {col:<22}: {fail_cnt} violations")
        
    print("\n--- Isolated Validation Failures Sample ---")
    print(failures[['customer_id', 'age', 'price', 'email', 'phone', 'start_date', 'end_date', 'passes_all_checks']])
    
    print("\n--- Clean Validated Dataset Ready for Downstream Analysis ---")
    print(df_clean[['customer_id', 'age', 'price', 'email', 'phone', 'start_date', 'end_date']])
    
    return df, df_clean, failures


def run_pipeline():
    """Execute complete Data Validation Framework."""
    print("Initializing Raw Customer Campaign Dataset...")
    df = create_sample_dataset()
    
    df = task_1_range_checks(df)
    df = task_2_null_constraints(df)
    df = task_3_format_validation(df)
    df = task_4_business_rule_validation(df)
    df, df_clean, failures = task_5_validation_report(df, output_path='output/validation_failures.csv')
    
    print("\n" + "=" * 60)
    print("DATA VALIDATION PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
