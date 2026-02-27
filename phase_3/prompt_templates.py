from typing import List, Dict, Any

from phase_2.models import UserPreferences, Restaurant


def build_candidate_summary(candidates: List[Restaurant]) -> str:
  """
  Build a compact, human-readable summary of candidate restaurants
  for inclusion in the LLM prompt.
  """
  lines = []
  for idx, r in enumerate(candidates):
    line = (
      f"{idx}: name={r.name} | locality={r.location} | "
      f"rating={r.rating:.1f} | price_for_two={r.price_for_two:.0f} | "
      f"votes={r.votes} | cuisines={r.cuisines}"
    )
    lines.append(line)
  return "\n".join(lines)


def build_system_prompt() -> str:
  """
  System prompt strictly enforcing:
  - Use ONLY the provided candidate restaurants (from the Zomato dataset).
  - Do NOT invent or add any external restaurants or data.
  - Output a well-structured JSON object.
  """
  return (
    "You are an AI restaurant recommender assistant.\n"
    "You are given a list of candidate restaurants that all come from a single "
    "Zomato dataset. This dataset is the ONLY allowed source of restaurant data.\n\n"
    "RULES:\n"
    "- You must ONLY recommend restaurants from the provided candidate list.\n"
    "- You must NOT invent or add any new restaurant names, locations, cuisines, "
    "  or facts that are not present in the candidate list.\n"
    "- If no candidates are suitable, you must return an empty list.\n"
    "- You must respond with a valid JSON object only, with no extra commentary.\n"
    "- Do not add any external knowledge (such as reviews, addresses, or details) "
    "  beyond what is present in the candidate list fields.\n"
  )


def build_user_message(
  prefs: UserPreferences, candidates: List[Restaurant], max_results: int
) -> str:
  """
  Build the user message that describes preferences and asks the LLM
  to select and explain recommendations.
  """
  candidate_block = build_candidate_summary(candidates)

  prefs_desc = (
    f"User preferences:\n"
    f"- Locality: {prefs.locality or 'any'}\n"
    f"- Price for two range: "
    f"{prefs.min_price if prefs.min_price is not None else 'any'} to "
    f"{prefs.max_price if prefs.max_price is not None else 'any'}\n"
    f"- Minimum rating: {prefs.min_rating if prefs.min_rating is not None else 'any'}\n"
    f"- Desired cuisines: {', '.join(prefs.desired_cuisines) if prefs.desired_cuisines else 'any'}\n"
  )

  instructions = (
    "From the candidate list below, choose up to "
    f"{max_results} restaurants that best match the user's preferences.\n"
    "For each recommended restaurant, provide a short explanation that ONLY uses "
    "the fields available in the candidate list (name, locality, rating, price, "
    "votes, cuisines).\n\n"
    "Respond with a JSON object of the form:\n\n"
    "{\n"
    '  "recommendations": [\n'
    "    {\n"
    '      "candidate_index": <integer index from the candidate list>,\n'
    '      "reason": "<short explanation using only candidate fields>"\n'
    "    },\n"
    "    ...\n"
    "  ]\n"
    "}\n\n"
    "Remember: do NOT add any restaurants that are not in the candidate list."
  )

  return prefs_desc + "\nCandidate restaurants:\n" + candidate_block + "\n\n" + instructions


def build_messages(
  prefs: UserPreferences, candidates: List[Restaurant], max_results: int
) -> List[Dict[str, str]]:
  """
  Build the messages payload for Groq chat completions.
  """
  system_prompt = build_system_prompt()
  user_message = build_user_message(prefs, candidates, max_results)
  return [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message},
  ]

