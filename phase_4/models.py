from typing import List, Optional
from pydantic import BaseModel, Field

class RecommendationRequest(BaseModel):
    """Input model for recommendation requests."""
    min_price: Optional[float] = Field(None, description="Minimum price for two")
    max_price: Optional[float] = Field(None, description="Maximum price for two")
    locality: Optional[str] = Field(None, description="Locality name (e.g., BTM, HSR)")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum restaurant rating")
    desired_cuisines: Optional[List[str]] = Field(None, description="List of preferred cuisines")

class RestaurantInfo(BaseModel):
    """Details of a recommended restaurant."""
    name: str
    location: str
    price_for_two: float
    rating: float
    cuisines: str
    votes: int

class RecommendationResponseItem(BaseModel):
    """A single recommendation with its explanation."""
    restaurant: RestaurantInfo
    reason: str

class RecommendationResponse(BaseModel):
    """Final wrapped response with multiple recommendations."""
    preferences: RecommendationRequest
    recommendations: List[RecommendationResponseItem]
