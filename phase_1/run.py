from phase_1.data_ingestion import (
  load_zomato_dataset,
  save_raw_dataset,
  basic_eda,
  print_summary,
)


def main() -> None:
  """
  Entry point for Phase 1.

  - Loads the Zomato dataset from Hugging Face.
  - Saves a raw CSV copy under data/raw.
  - Prints basic EDA summaries to the console.
  """
  df = load_zomato_dataset()
  output_path = save_raw_dataset(df)
  print(f"Raw dataset saved to: {output_path}")

  summary = basic_eda(df)
  print_summary(summary)


if __name__ == "__main__":
  main()

