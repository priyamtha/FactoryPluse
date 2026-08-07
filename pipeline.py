import pandas as pd
import logging
import argparse
import os

# Configure logging with timestamps as required by Task 3
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def ingest(path):
    logger.info("Ingesting: " + path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found at: {path}")
    df = pd.read_csv(path)
    logger.info("Rows ingested: " + str(len(df)))
    return df

def clean(df):
    logger.info("Cleaning...")
    initial = len(df)
    # Ensure subset columns exist before dropna to prevent errors
    subset_cols = [c for c in ["customer_id", "amount"] if c in df.columns]
    df = df.dropna(subset=subset_cols)
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df = df[df["amount"] > 0]
    logger.info("Cleaned: " + str(initial) + " -> " + str(len(df)))
    return df

def aggregate(df):
    logger.info("Aggregating...")
    # Dynamically verify required columns for aggregation
    agg_cols = {}
    if "amount" in df.columns:
        agg_cols["revenue"] = ("amount", "sum")
    if "order_id" in df.columns:
        agg_cols["orders"] = ("order_id", "count")
        
    group_col = "segment" if "segment" in df.columns else df.columns[0]
    
    agg = df.groupby(group_col).agg(**agg_cols).reset_index()
    logger.info("Segments: " + str(len(agg)))
    return agg

def output(df, agg, out_dir):
    # Ensure output directory exists before writing
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "cleaned.csv"), index=False)
    agg.to_csv(os.path.join(out_dir, "aggregated.csv"), index=False)
    logger.info("Output written to: " + out_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Ingest-Clean-Aggregate-Output Pipeline")
    parser.add_argument("--input", required=True, help="Path to input raw CSV file")
    parser.add_argument("--output", default="output", help="Directory path to save output files")
    args = parser.parse_args()
    
    raw = ingest(args.input)
    cleaned = clean(raw)
    agg = aggregate(cleaned)
    output(cleaned, agg, args.output)
    
    # Task 5: Confirm pipeline completion in log entry
    logger.info("ETL Pipeline completed successfully.")
