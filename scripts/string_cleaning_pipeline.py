import pandas as pd
import numpy as np

def create_sample_dataset():
    """Create a synthetic dataset with messy text columns for cleaning."""
    data = {
        'customer_name': [
            '  JOHN  ', 'john', 'John', '  Alice Smith ', 'alice smith', 
            'ALICE SMITH ', '  Bob Jones', 'bob jones  ', 'São Paulo User', 'Café Manager!'
        ],
        'location': [
            '  São Paulo  ', 'são paulo', 'SAO PAULO', '  New York# ', 'new york', 
            'NEW YORK  ', ' London! ', 'london', '  Paris@', 'paris'
        ],
        'customer_segment': [
            '  b2b ', 'b 2 b', 'business-to-business', 'sme', 'Small Medium Enterprise', 
            'SMB', 'enterprise', '  ENT ', 'corporate enterprise', 'B2B'
        ],
        'product_category': [
            '  Electronics $ ', 'electronics', 'ELECTRONICS', '  Software & IT  ', 'software it', 
            'SOFTWARE', '  Hardware * ', 'hardware', 'HARDWARE', 'Software'
        ]
    }
    return pd.DataFrame(data)


# ---------------------------------------------------------
# TASK 1: Strip Whitespace Consistently
# ---------------------------------------------------------
def strip_all_strings(df):
    """Strip whitespace from all string columns."""
    print("=" * 60)
    print("TASK 1: STRIP WHITESPACE CONSISTENTLY")
    print("=" * 60)
    
    string_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    total_issues_fixed = 0
    
    # Store before value counts for 2 columns to show comparison
    cols_to_compare = list(string_cols[:2])
    before_counts = {col: df[col].copy().value_counts() for col in cols_to_compare}
    
    for col in string_cols:
        # Count values with leading or trailing whitespace
        has_whitespace = df[col].dropna().apply(lambda x: x != str(x).strip()).sum()
        total_issues_fixed += has_whitespace
        
        before = df[col].nunique()
        df[col] = df[col].str.strip()
        after = df[col].nunique()
        
        print(f"Column '{col}': {before} -> {after} unique values ({has_whitespace} values with whitespace cleaned)")
            
    print(f"\nSummary: Total whitespace issues fixed across dataset = {total_issues_fixed}\n")
    
    # Before/After value counts comparison for at least 2 columns
    for col in cols_to_compare:
        print(f"--- Before/After Value Counts for '{col}' ---")
        print("BEFORE STRIPPING:")
        print(before_counts[col])
        print("\nAFTER STRIPPING:")
        print(df[col].value_counts())
        print("-" * 40)
        
    return df


# ---------------------------------------------------------
# TASK 2: Normalize Casing to Consistent Standard
# ---------------------------------------------------------
def normalize_casing(df, columns_to_lower):
    """Normalize casing for specified columns."""
    print("\n" + "=" * 60)
    print("TASK 2: NORMALIZE CASING TO CONSISTENT STANDARD")
    print("=" * 60)
    
    print("\nBusiness Decision:")
    print("Standardizing all categorical text to lowercase to ensure database consistency,")
    print("case-insensitive searching, and merging without duplicate records caused by casing variations.\n")
    
    print("Demonstration of Casing Consolidation:")
    demo_series = pd.Series(["JOHN", "john", "John"])
    print("Before:", list(demo_series))
    print("After:", list(demo_series.str.lower()))
    print("Unique values mapped from 3 distinct casings to 1 single canonical casing: 'john'\n")
    
    print("Samples BEFORE casing normalization:")
    print(df[columns_to_lower].head(5))
    
    for col in columns_to_lower:
        df[col] = df[col].str.lower()
        print(f"Normalized '{col}' to lowercase")
        
    print("\nSamples AFTER casing normalization:")
    print(df[columns_to_lower].head(5))
    
    return df


# ---------------------------------------------------------
# TASK 3: Remove Special Characters Using Regex
# ---------------------------------------------------------
def remove_special_characters(df, columns):
    """Remove special characters from specified columns."""
    print("\n" + "=" * 60)
    print("TASK 3: REMOVE SPECIAL CHARACTERS USING REGEX")
    print("=" * 60)
    
    pattern = '[^a-zA-Z0-9 ]'
    print(f"Regex Pattern Used: '{pattern}'")
    print("Explanation: The pattern '[^a-zA-Z0-9 ]' uses a negated character set '[^...]'.")
    print("It matches any character that is NOT an ASCII letter (a-z, A-Z), a digit (0-9), or a space.")
    print("Non-ASCII international characters like 'ã' or 'é' are non-alphanumeric in ASCII standard,")
    print("so 'São Paulo' becomes 'So Paulo' and 'Café' becomes 'Caf'.\n")
    
    print("Samples BEFORE special character removal:")
    print(df[columns].head(5))
    
    for col in columns:
        df[col] = df[col].str.replace(pattern, '', regex=True)
        print(f"Removed special characters from '{col}'")
        
    print("\nSamples AFTER special character removal:")
    print(df[columns].head(5))
    
    print("\nInternational Character Verification:")
    print("Checking location entries originally containing accented characters:")
    loc_sample = df['location'][df['location'].str.contains('so paulo|caf', case=False, na=False)]
    print(loc_sample.to_string())
    
    return df


# ---------------------------------------------------------
# TASK 4: Standardize Categorical Labels Using Mapping Dictionary
# ---------------------------------------------------------
def standardize_categorical_labels(df):
    """Standardize categorical labels using mapping dictionary."""
    print("\n" + "=" * 60)
    print("TASK 4: STANDARDIZE CATEGORICAL LABELS USING MAPPING DICTIONARY")
    print("=" * 60)
    
    segment_map = {
        # B2B Category variations (3 variations)
        'b2b': 'B2B',
        'b 2 b': 'B2B',
        'business-to-business': 'B2B',
        'businesstobusiness': 'B2B',
        
        # SMB Category variations (3 variations)
        'sme': 'SMB',
        'small medium enterprise': 'SMB',
        'smb': 'SMB',
        
        # Enterprise Category variations (3 variations)
        'enterprise': 'Enterprise',
        'ent': 'Enterprise',
        'corporate enterprise': 'Enterprise'
    }
    
    print("Mapping Dictionary Introduced:")
    for k, v in segment_map.items():
        print(f"  '{k}' -> '{v}'")
        
    print("\nBusiness Decision Justifications:")
    print("1. 'B2B': Standard CRM code used across sales & revenue operations instead of spelling out 'business-to-business'.")
    print("2. 'SMB': Unified abbreviation for Small & Medium Businesses for aligned financial reporting.")
    print("3. 'Enterprise': Formal title used for accounts requiring dedicated key account managers.")
    
    print("\n'customer_segment' Value Counts BEFORE Mapping:")
    print(df['customer_segment'].value_counts())
    
    df['customer_segment'] = df['customer_segment'].replace(segment_map)
    
    print("\n'customer_segment' Value Counts AFTER Mapping:")
    print(df['customer_segment'].value_counts())
    
    return df


# ---------------------------------------------------------
# TASK 5: Build Reusable String Cleaning Function
# ---------------------------------------------------------
def clean_text_column(series, lowercase=True, strip=True, 
                     remove_special=False, mapping=None):
    """Reusable text cleaning function for any string column."""
    result = series.copy()
    
    if result.isna().any():
        print(f"Warning: {result.isna().sum()} null values in column")
        
    if strip:
        result = result.str.strip()
        
    if lowercase:
        result = result.str.lower()
        
    if remove_special:
        result = result.str.replace('[^a-zA-Z0-9 ]', '', regex=True)
        
    if mapping:
        result = result.map(mapping).fillna(result)
        
    return result


def run_pipeline_and_tests():
    """Main function executing the pipeline tasks and testing edge cases."""
    print("Initializing Raw Messy Dataset...")
    df_raw = create_sample_dataset()
    print("Raw Dataset Head:")
    print(df_raw.head())
    print("\n")
    
    # Run Tasks 1 to 4 on dataset copy
    df = df_raw.copy()
    df = strip_all_strings(df)
    df = normalize_casing(df, columns_to_lower=['customer_name', 'location', 'customer_segment', 'product_category'])
    df = remove_special_characters(df, columns=['customer_name', 'location', 'product_category'])
    df = standardize_categorical_labels(df)
    
    print("\n" + "=" * 60)
    print("FINAL CLEANED DATASET AFTER TASKS 1-4:")
    print("=" * 60)
    print(df)
    
    # Task 5 Application on Fresh Dataset
    print("\n" + "=" * 60)
    print("TASK 5: REUSABLE STRING CLEANING FUNCTION DEMONSTRATION")
    print("=" * 60)
    df_task5 = create_sample_dataset()
    
    print("\nParameter Choices & Application for 3 Columns:")
    print("1. 'customer_name': lowercase=True, strip=True, remove_special=True")
    print("   Reason: Clean name strings, remove accidental spaces and special symbols.")
    df_task5['customer_name'] = clean_text_column(df_task5['customer_name'], lowercase=True, strip=True, remove_special=True)
    
    print("2. 'location': lowercase=False, strip=True, remove_special=False")
    print("   Reason: Keep location casing intact while trimming whitespace, retaining accent marks prior to mapping.")
    df_task5['location'] = clean_text_column(df_task5['location'], lowercase=False, strip=True, remove_special=False)
    
    segment_map_clean = {
        'b2b': 'B2B', 'b 2 b': 'B2B', 'business-to-business': 'B2B',
        'sme': 'SMB', 'small medium enterprise': 'SMB', 'smb': 'SMB',
        'enterprise': 'Enterprise', 'ent': 'Enterprise', 'corporate enterprise': 'Enterprise'
    }
    print("3. 'customer_segment': lowercase=True, strip=True, mapping=segment_map_clean")
    print("   Reason: Strip, lowercase, and immediately map to canonical labels.")
    df_task5['customer_segment'] = clean_text_column(df_task5['customer_segment'], lowercase=True, strip=True, mapping=segment_map_clean)
    
    print("\nCleaned DataFrame using clean_text_column():")
    print(df_task5)
    
    # Edge Cases Testing
    print("\n" + "-" * 40)
    print("EDGE CASES TESTING (AS SPECIFIED IN INSTRUCTIONS)")
    print("-" * 40)
    test_cases = [
        '  Product A  ',      # Leading/trailing spaces
        'PRODUCT B',         # All caps
        'Product_C',         # Special char
        None,                # Null value
        ''                   # Empty string
    ]
    
    test_series = pd.Series(test_cases)
    print("Raw Edge Cases Input Series:")
    print(test_series)
    print("\nApplying clean_text_column(test_series, lowercase=True, strip=True, remove_special=True):")
    result = clean_text_column(test_series, lowercase=True, strip=True, remove_special=True)
    print("\nCleaned Edge Cases Result Series:")
    print(result)


if __name__ == '__main__':
    run_pipeline_and_tests()
