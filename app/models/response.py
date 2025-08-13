"""Response models for Travel Buddy API."""

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



from datetime import date

class TravelItinerary(BaseModel):
    from_location: str
    to_location: str
    from_date: date
    to_date: date
    budget: float


class ItineraryResponse(BaseModel):
    travel_itinerary: TravelItinerary
    days: List[DayActivity]
    summary: TravelSummary
    tips: List[str]
    raw_text: Optional[str] = None  # For backward compatibility
