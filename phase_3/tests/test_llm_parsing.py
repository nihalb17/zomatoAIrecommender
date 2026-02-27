import json

from phase_2.models import Restaurant
from phase_3.llm_recommender import _parse_llm_response


def test_parse_llm_response_basic():
  candidates = [
    Restaurant(
      name="A",
      location="BTM",
      price_for_two=300,
      rating=4.0,
      cuisines="North Indian",
      votes=100,
    ),
    Restaurant(
      name="B",
      location="HSR",
      price_for_two=400,
      rating=3.8,
      cuisines="Chinese",
      votes=50,
    ),
  ]

  payload = {
    "recommendations": [
      {"candidate_index": 0, "reason": "Matches locality and budget."},
      {"candidate_index": 1, "reason": "Backup option."},
    ]
  }
  text = json.dumps(payload)

  recs = _parse_llm_response(text, candidates)
  assert len(recs) == 2
  assert recs[0].restaurant.name == "A"
  assert "Matches locality" in recs[0].reason

