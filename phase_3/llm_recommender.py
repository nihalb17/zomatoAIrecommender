import json
import re
from dataclasses import dataclass
from typing import List

from phase_2.models import UserPreferences, Restaurant
from phase_2.retrieval import get_recommendations as get_deterministic_recommendations
from phase_3.client import GroqClient, GroqClientError
from phase_3.prompt_templates import build_messages


@dataclass
class LLMRestaurantRecommendation:
  restaurant: Restaurant
  reason: str


def _extract_json_block(text: str) -> str:
  """
  Extract the first JSON object from the LLM response text.

  This is defensive in case the model accidentally adds extra commentary,
  despite our instruction to return JSON only.
  """
  # Simple heuristic: find first '{' and last '}' and slice.
  start = text.find("{")
  end = text.rfind("}")
  if start == -1 or end == -1 or end <= start:
    raise ValueError("No JSON object found in LLM response.")
  return text[start : end + 1]


def _parse_llm_response(
  raw_text: str, candidates: List[Restaurant]
) -> List[LLMRestaurantRecommendation]:
  """
  Parse the LLM's JSON response into structured recommendations.
  """
  json_block = _extract_json_block(raw_text)
  data = json.loads(json_block)

  recs = data.get("recommendations", [])
  results: List[LLMRestaurantRecommendation] = []

  for item in recs:
    try:
      idx = int(item.get("candidate_index"))
    except (TypeError, ValueError):
      continue

    if idx < 0 or idx >= len(candidates):
      # Ignore indexes that are out of range: this would violate the
      # "no external restaurants" rule.
      continue

    reason = str(item.get("reason", "")).strip()
    results.append(LLMRestaurantRecommendation(restaurant=candidates[idx], reason=reason))

  return results


def get_llm_recommendations(
  prefs: UserPreferences, max_candidates: int = 20, max_results: int = 5
) -> List[LLMRestaurantRecommendation]:
  """
  End-to-end recommendation pipeline for Phase 3:

  - Uses Phase 2 deterministic engine to get candidate restaurants
    (all from the Zomato dataset).
  - Sends candidates + user preferences to Groq with strict instructions
    to only choose from the provided list and not to add any external data.
  - Parses the JSON response into structured recommendations.
  """
  # Step 1: deterministic candidates from Phase 2 (dataset is the only source).
  candidates: List[Restaurant] = get_deterministic_recommendations(
    prefs, max_results=max_candidates
  )
  if not candidates:
    return []

  # Step 2: build Groq messages.
  messages = build_messages(prefs, candidates, max_results)

  # Step 3: call Groq.
  client = GroqClient()
  raw_text = client.chat(messages)

  # Step 4: parse JSON and map back to candidate restaurants.
  return _parse_llm_response(raw_text, candidates)

