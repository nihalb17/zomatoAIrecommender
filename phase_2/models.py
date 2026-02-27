from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UserPreferences:
  """Structured representation of user constraints for retrieval."""

  min_price: Optional[float] = None
  max_price: Optional[float] = None
  locality: Optional[str] = None
  min_rating: Optional[float] = None
  desired_cuisines: Optional[List[str]] = None


@dataclass
class Restaurant:
  """Lightweight restaurant representation used by the retrieval engine."""

  name: str
  location: str
  price_for_two: float
  rating: float
  cuisines: str
  votes: int

