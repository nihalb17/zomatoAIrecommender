from phase_2.models import UserPreferences
from phase_2.retrieval import get_recommendations


def main() -> None:
  """
  Entry point for Phase 2.

  Uses a sample set of user preferences to:
  - Load the Phase 1 data artifact.
  - Filter and rank restaurants deterministically.
  - Print the top-N recommendations to the console.
  """
  # Example preferences – you can change these and re-run the module.
  prefs = UserPreferences(
    min_price=200,
    max_price=600,
    locality="BTM",
    min_rating=3.5,
    desired_cuisines=["North Indian"],
  )

  recommendations = get_recommendations(prefs, max_results=10)

  if not recommendations:
    print("No restaurants found for the given preferences.")
    return

  print("=== Phase 2: Deterministic Recommendations ===")
  print(
    f"Preferences: locality={prefs.locality}, price=[{prefs.min_price}, {prefs.max_price}], "
    f"min_rating={prefs.min_rating}, cuisines={prefs.desired_cuisines}"
  )
  print()

  for idx, r in enumerate(recommendations, start=1):
    print(
      f"{idx}. {r.name} | {r.location} | Rating: {r.rating:.1f} | "
      f"Price for two: {r.price_for_two:.0f} | Votes: {r.votes} | Cuisines: {r.cuisines}"
    )


if __name__ == "__main__":
  main()

