from pydantic import BaseModel
from typing import Optional, List

class DayActivity(BaseModel):
    theme: str
    morning: str
    afternoon: str
    evening: str
    budget: float

class TravelSummary(BaseModel):
    total_estimated_cost: float
    remaining_budget: float

class TravelItinerary(BaseModel):
    from_location: str
    to_location: str
    dates: str
    budget: float

class ItineraryRequest(BaseModel):
    from_location: str  # Origin city (e.g., "Hubli", "Mumbai", "NYC")
    to_location: str    # Destination city (e.g., "Belagavi", "Paris", "Tokyo")
    budget: float
    dates: str
    model: Optional[str] = "local"  # "openai", "groq", or "local"
    include_real_data: Optional[bool] = False  # Whether to fetch real flight/hotel/weather data
    response_format: Optional[str] = "json"  # "json" or "text"

class ItineraryResponse(BaseModel):
    travel_itinerary: TravelItinerary
    days: List[DayActivity]
    summary: TravelSummary
    tips: List[str]
    raw_text: Optional[str] = None  # For backward compatibility
