import pandas as pd


def ingest_data(filepath):
    """
    Load data from a CSV file.

    Input:
        filepath - path to CSV file

    Output:
        Pandas DataFrame
    """

    # Read CSV file
    df = pd.read_csv(filepath)

    return df


def process_data(df):
    """
    Clean the dataset.

    Input:
        DataFrame

    Output:
        Cleaned DataFrame
    """

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Fill missing numeric values
    for col in df.select_dtypes(include=["number"]).columns:
        df[col] = df[col].fillna(df[col].median())

    return df


def output_results(df, output_path):
    """
    Save processed data.

    Input:
        DataFrame

    Output:
        CSV file
    """

    df.to_csv(output_path, index=False)

    print("✓ Data successfully processed")
    print(f"✓ Rows processed: {len(df)}")
    print(f"✓ Output saved to {output_path}")


if __name__ == "__main__":

    data = ingest_data("data/raw/sample.csv")

    processed = process_data(data)

    output_results(processed, "output/processed.csv")
