"""MongoDB document models using Beanie ODM."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr
from pymongo import IndexModel


class User(Document):
    """User document model for MongoDB."""
    
    email: Indexed(EmailStr, unique=True)  # type: ignore # Unique email index
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Settings:
        name = "users"  # Collection name
        indexes = [
            IndexModel([("email", 1)], unique=True),
            IndexModel([("created_at", -1)]),
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True
            }
        }


class ItineraryDay(BaseModel):
    """Single day in an itinerary."""
    
    theme: str
    morning: str
    afternoon: str
    evening: str
    budget: float


class ItinerarySummary(BaseModel):
    """Itinerary summary with costs."""
    
    total_estimated_cost: float
    remaining_budget: float


class TravelItineraryInfo(BaseModel):
    """Basic travel information."""
    
    from_location: str
    to_location: str
    dates: str
    budget: float


class Itinerary(Document):
    """Itinerary document model for MongoDB."""
    
    user_id: Optional[str] = None  # Reference to User document
    from_location: str
    to_location: str
    dates: str
    budget: float
    model_used: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Itinerary content (stored as embedded documents)
    travel_itinerary: TravelItineraryInfo
    days: List[ItineraryDay]
    summary: ItinerarySummary
    tips: List[str] = []
    
    # Additional metadata
    generation_time_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    
    class Settings:
        name = "itineraries"  # Collection name
        indexes = [
            IndexModel([("user_id", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("to_location", 1)]),
            IndexModel([("from_location", 1)]),
            IndexModel([("model_used", 1)]),
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_location": "Mumbai",
                "to_location": "Paris",
                "dates": "2025-08-15 to 2025-08-20",
                "budget": 2000,
                "model_used": "groq",
                "travel_itinerary": {
                    "from_location": "Mumbai",
                    "to_location": "Paris",
                    "dates": "2025-08-15 to 2025-08-20",
                    "budget": 2000
                },
                "days": [
                    {
                        "theme": "Arrival & Exploration",
                        "morning": "Flight from Mumbai to Paris",
                        "afternoon": "Hotel check-in and rest",
                        "evening": "Evening stroll along Seine River",
                        "budget": 300
                    }
                ],
                "summary": {
                    "total_estimated_cost": 1800,
                    "remaining_budget": 200
                },
                "tips": [
                    "Book hotels in advance",
                    "Try local cuisine"
                ]
            }
        }
