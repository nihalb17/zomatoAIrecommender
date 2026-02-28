import pandas as pd
import os
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent
RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "zomato_raw.csv"
FILTERED_DATA_PATH = ROOT_DIR / "data" / "zomato_filtered.csv"

def filter_dataset():
    print(f"Reading raw dataset from {RAW_DATA_PATH}...")
    if not RAW_DATA_PATH.exists():
        print(f"Error: Raw dataset not found at {RAW_DATA_PATH}")
        return

    # Define columns to keep
    columns_to_keep = [
        'name', 
        'rate', 
        'votes', 
        'location', 
        'cuisines', 
        'approx_cost(for two people)'
    ]

    try:
        # Load only necessary columns to save memory during processing
        df = pd.read_csv(RAW_DATA_PATH, usecols=columns_to_keep)
        
        print(f"Original row count: {len(df)}")
        
        # Ensure output directory exists
        FILTERED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Save filtered dataset
        print(f"Saving filtered dataset to {FILTERED_DATA_PATH}...")
        df.to_csv(FILTERED_DATA_PATH, index=False)
        
        size_mb = os.path.getsize(FILTERED_DATA_PATH) / (1024 * 1024)
        print(f"Success! Filtered dataset size: {size_mb:.2f} MB")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    filter_dataset()
