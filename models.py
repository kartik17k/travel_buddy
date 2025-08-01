from pydantic import BaseModel
from typing import Optional

class ItineraryRequest(BaseModel):
    destination: str
    budget: float
    dates: str
    model: Optional[str] = "local"  # "openai" or "local"

class ItineraryResponse(BaseModel):
    itinerary: str
