"""Data models for Travel Buddy API."""

from .request import ItineraryRequest
from .response import (
    DayActivity,
    TravelSummary,
    TravelItinerary,
    ItineraryResponse
)

__all__ = [
    "ItineraryRequest",
    "DayActivity", 
    "TravelSummary",
    "TravelItinerary",
    "ItineraryResponse"
]
