"""Request models for Travel Buddy API."""

from pydantic import BaseModel
from typing import Optional


class ItineraryRequest(BaseModel):
    from_location: str  # Origin city (e.g., "Hubli", "Mumbai", "NYC")
    to_location: str    # Destination city (e.g., "Belagavi", "Paris", "Tokyo")
    budget: float
    dates: str
    model: Optional[str] = "local"  # "openai", "groq", or "local"
    include_real_data: Optional[bool] = False  # Whether to fetch real flight/hotel/weather data
    response_format: Optional[str] = "json"  # "json" or "text"
