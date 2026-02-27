from __future__ import annotations

from math import log1p
from pathlib import Path
from typing import List

import pandas as pd

from phase_2.models import UserPreferences, Restaurant


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "zomato_raw.csv"


def _parse_rating(raw: str) -> float:
  """
  Convert Zomato-style rating strings like '3.9/5', '3.9 /5', or 'NEW'
  to a numeric value. Non-numeric or missing ratings return 0.0.
  """
  if not isinstance(raw, str):
    return 0.0

  text = raw.strip().upper()
  if text == "NEW" or text in {"-", ""}:
    return 0.0

  # Handle patterns like '3.9/5' or '3.9 /5'
  try:
    number_part = text.split("/")[0].strip()
    return float(number_part)
  except Exception:
    return 0.0


def _parse_price(raw) -> float:
  """
  Convert the 'approx_cost(for two people)' field to float.
  """
  try:
    # Some datasets use strings; remove commas if present.
    if isinstance(raw, str):
      raw = raw.replace(",", "").strip()
    return float(raw)
  except Exception:
    return 0.0


def _parse_votes(raw) -> int:
  try:
    if isinstance(raw, str):
      raw = raw.replace(",", "").strip()
    return int(raw)
  except Exception:
    return 0


def load_prepared_dataframe() -> pd.DataFrame:
  """
  Load the raw CSV generated in Phase 1 and add helper numeric columns.
  """
  df = pd.read_csv(RAW_DATA_PATH)

  # Normalize key fields we will filter/rank on.
  df["rating_numeric"] = df["rate"].apply(_parse_rating)
  df["price_for_two_numeric"] = df["approx_cost(for two people)"].apply(_parse_price)
  df["votes_numeric"] = df["votes"].apply(_parse_votes)
  df["location_normalized"] = df["location"].astype(str).str.lower()
  df["cuisines_normalized"] = df["cuisines"].astype(str).str.lower()

  return df


def filter_restaurants(df: pd.DataFrame, prefs: UserPreferences) -> pd.DataFrame:
  """
  Apply structured filters based on user preferences.
  """
  filtered = df.copy()

  # Price range
  if prefs.min_price is not None:
    filtered = filtered[filtered["price_for_two_numeric"] >= prefs.min_price]
  if prefs.max_price is not None:
    filtered = filtered[filtered["price_for_two_numeric"] <= prefs.max_price]

  # Locality (substring match, case-insensitive)
  if prefs.locality:
    loc = prefs.locality.strip().lower()
    filtered = filtered[filtered["location_normalized"].str.contains(loc, na=False)]

  # Minimum rating
  if prefs.min_rating is not None:
    filtered = filtered[filtered["rating_numeric"] >= prefs.min_rating]

  # Desired cuisines (at least one cuisine should match as substring)
  if prefs.desired_cuisines:
    cuisine_terms = [c.strip().lower() for c in prefs.desired_cuisines if c.strip()]
    if cuisine_terms:
      mask = False
      for term in cuisine_terms:
        mask = mask | filtered["cuisines_normalized"].str.contains(term, na=False)
      filtered = filtered[mask]

  return filtered


def rank_restaurants(df: pd.DataFrame, max_results: int = 20) -> List[Restaurant]:
  """
  Rank restaurants using a simple heuristic:
  - Higher rating is better.
  - Higher votes are better (log-scaled).
  - For tie-breaking, lower price_for_two is slightly favored.
  """
  if df.empty:
    return []

  df = df.copy()
  df["score"] = df["rating_numeric"] * 2.0 + df["votes_numeric"].apply(lambda v: log1p(max(v, 0)))

  df_sorted = df.sort_values(
    by=["score", "rating_numeric", "votes_numeric", "price_for_two_numeric"],
    ascending=[False, False, False, True],
  ).head(max_results)

  results: List[Restaurant] = []
  for _, row in df_sorted.iterrows():
    results.append(
      Restaurant(
        name=str(row.get("name", "")),
        location=str(row.get("location", "")),
        price_for_two=float(row.get("price_for_two_numeric", 0.0)),
        rating=float(row.get("rating_numeric", 0.0)),
        cuisines=str(row.get("cuisines", "")),
        votes=int(row.get("votes_numeric", 0)),
      )
    )

  return results


def get_recommendations(prefs: UserPreferences, max_results: int = 10) -> List[Restaurant]:
  """
  High-level deterministic recommendation function.
  """
  df = load_prepared_dataframe()
  filtered = filter_restaurants(df, prefs)
  return rank_restaurants(filtered, max_results=max_results)

