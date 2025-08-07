"""Data models for Travel Buddy API."""

from .request import ItineraryRequest
from .response import (
    DayActivity,
    TravelSummary,
    TravelItinerary,
    ItineraryResponse
)
from .auth import (
    UserCreate,
    UserUpdate,
    User,
    Token,
    TokenData,
    LoginRequest
)

__all__ = [
    "ItineraryRequest",
    "DayActivity", 
    "TravelSummary",
    "TravelItinerary",
    "ItineraryResponse",
    "UserCreate",
    "UserUpdate", 
    "User",
    "Token",
    "TokenData",
    "LoginRequest"
]
