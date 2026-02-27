from pathlib import Path
from typing import Dict, Any

import pandas as pd
from datasets import load_dataset


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"


def load_zomato_dataset() -> pd.DataFrame:
  """
  Load the Zomato dataset from Hugging Face and return it as a pandas DataFrame.

  The function is robust to different split names by picking the first available split.
  """
  dataset_dict = load_dataset(DATASET_NAME)

  if hasattr(dataset_dict, "keys"):
    # Pick the first split (e.g., 'train') if multiple are present.
    first_split = next(iter(dataset_dict.keys()))
    ds = dataset_dict[first_split]
  else:
    # Fallback: assume a single dataset object.
    ds = dataset_dict

  df = ds.to_pandas()
  return df


def ensure_directories() -> None:
  """Create data directories if they do not exist."""
  RAW_DIR.mkdir(parents=True, exist_ok=True)


def save_raw_dataset(df: pd.DataFrame, filename: str = "zomato_raw.csv") -> Path:
  """Save the raw dataset to the raw data directory and return the path."""
  ensure_directories()
  output_path = RAW_DIR / filename
  df.to_csv(output_path, index=False)
  return output_path


def basic_eda(df: pd.DataFrame) -> Dict[str, Any]:
  """
  Compute lightweight, defensive EDA focused on:
  - overall size and columns
  - candidate columns for price, rating, locality, and cuisine.
  """
  summary: Dict[str, Any] = {
    "num_rows": int(df.shape[0]),
    "num_columns": int(df.shape[1]),
    "columns": list(df.columns),
  }

  def pick_columns(substring_options):
    lowered = {col.lower(): col for col in df.columns}
    for sub in substring_options:
      for key, original in lowered.items():
        if sub in key:
          return original
    return None

  price_col = pick_columns(["cost", "price"])
  rating_col = pick_columns(["rate", "rating"])
  locality_col = pick_columns(["locality", "location", "city"])
  cuisine_col = pick_columns(["cuisines", "cuisine"])

  if price_col:
    summary["price_column"] = price_col
    summary["price_sample_distribution"] = (
      df[price_col].value_counts(dropna=True).head(10).to_dict()
    )

  if rating_col:
    summary["rating_column"] = rating_col
    summary["rating_sample_distribution"] = (
      df[rating_col].value_counts(dropna=True).head(10).to_dict()
    )

  if locality_col:
    summary["locality_column"] = locality_col
    summary["top_localities"] = (
      df[locality_col].value_counts(dropna=True).head(10).to_dict()
    )

  if cuisine_col:
    summary["cuisine_column"] = cuisine_col
    summary["top_cuisines"] = (
      df[cuisine_col].value_counts(dropna=True).head(10).to_dict()
    )

  return summary


def print_summary(summary: Dict[str, Any]) -> None:
  """Pretty-print the basic EDA summary to stdout."""
  print("=== Zomato Dataset Summary (Phase 1) ===")
  print(f"Rows: {summary.get('num_rows')}")
  print(f"Columns: {summary.get('num_columns')}")
  print("Column names:")
  print(", ".join(summary.get("columns", [])))

  if "price_column" in summary:
    print(f"\nPrice column: {summary['price_column']}")
    print("Sample price distribution (top 10):")
    for val, count in summary["price_sample_distribution"].items():
      print(f"  {val}: {count}")

  if "rating_column" in summary:
    print(f"\nRating column: {summary['rating_column']}")
    print("Sample rating distribution (top 10):")
    for val, count in summary["rating_sample_distribution"].items():
      print(f"  {val}: {count}")

  if "locality_column" in summary:
    print(f"\nLocality column: {summary['locality_column']}")
    print("Top localities (top 10):")
    for val, count in summary["top_localities"].items():
      print(f"  {val}: {count}")

  if "cuisine_column" in summary:
    print(f"\nCuisine column: {summary['cuisine_column']}")
    print("Top cuisines (top 10):")
    for val, count in summary["top_cuisines"].items():
      print(f"  {val}: {count}")


