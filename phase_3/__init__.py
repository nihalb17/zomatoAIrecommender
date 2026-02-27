"""
Phase 3: Groq LLM integration and reasoning layer.

This phase takes deterministic candidate restaurants from Phase 2 and uses
the Groq LLM to:
- Choose the best subset based on user preferences.
- Generate natural language explanations for why each restaurant is recommended.

IMPORTANT CONSTRAINT:
- The LLM is strictly instructed to only recommend restaurants from the
  provided candidate list (derived from the Zomato dataset) and must not
  invent or add any external restaurants or data.
"""

