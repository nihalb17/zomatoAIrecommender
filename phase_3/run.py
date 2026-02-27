import os

from dotenv import load_dotenv

from phase_2.models import UserPreferences
from phase_3.client import GroqClientError
from phase_3.llm_recommender import get_llm_recommendations


def main() -> None:
  """
  Entry point for Phase 3.

  This will:
  - Use the Phase 2 deterministic engine to generate candidate restaurants.
  - Call Groq to select the best ones and generate explanations.
  - Print the final recommended restaurants with LLM reasons.

  NOTE:
  - You must set GROQ_API_KEY (and optionally GROQ_API_BASE, GROQ_MODEL)
    in your environment before running this phase.
  """
  # Load variables from .env (if present) into the environment.
  load_dotenv()

  if not os.getenv("GROQ_API_KEY"):
    print(
      "GROQ_API_KEY is not set. Please export GROQ_API_KEY in your environment "
      "before running Phase 3."
    )
    return

  prefs = UserPreferences(
    min_price=200,
    max_price=600,
    locality="BTM",
    min_rating=3.5,
    desired_cuisines=["North Indian"],
  )

  try:
    recommendations = get_llm_recommendations(prefs, max_candidates=20, max_results=5)
  except GroqClientError as exc:
    print(f"Groq client error: {exc}")
    return
  except Exception as exc:  # Defensive: unexpected parsing/network issues
    print(f"Unexpected error in Phase 3: {exc}")
    return

  if not recommendations:
    print("No LLM recommendations returned for the given preferences.")
    return

  print("=== Phase 3: Groq LLM Recommendations ===")
  print(
    f"Preferences: locality={prefs.locality}, price=[{prefs.min_price}, {prefs.max_price}], "
    f"min_rating={prefs.min_rating}, cuisines={prefs.desired_cuisines}"
  )
  print()

  for idx, rec in enumerate(recommendations, start=1):
    r = rec.restaurant
    print(
      f"{idx}. {r.name} | {r.location} | Rating: {r.rating:.1f} | "
      f"Price for two: {r.price_for_two:.0f} | Votes: {r.votes} | Cuisines: {r.cuisines}"
    )
    if rec.reason:
      print(f"   Reason: {rec.reason}")


if __name__ == "__main__":
  main()

