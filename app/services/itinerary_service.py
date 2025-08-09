"""Itinerary service for MongoDB operations."""

from datetime import datetime
from typing import List, Optional

from app.models.database import Itinerary, ItineraryDay, ItinerarySummary, TravelItineraryInfo
from app.models.request import ItineraryRequest
from app.models.response import ItineraryResponse


class ItineraryService:
    """Service for itinerary-related database operations."""
    
    @staticmethod
    async def save_itinerary(
        itinerary_request: ItineraryRequest,
        itinerary_response: ItineraryResponse,
        user_id: Optional[str] = None,
        generation_time_ms: Optional[float] = None
    ) -> Itinerary:
        """Save an itinerary to MongoDB."""
        
        # Convert response to MongoDB document format
        travel_itinerary = TravelItineraryInfo(
            from_location=itinerary_response.travel_itinerary.from_location,
            to_location=itinerary_response.travel_itinerary.to_location,
            dates=itinerary_response.travel_itinerary.dates,
            budget=itinerary_response.travel_itinerary.budget
        )
        
        days = [
            ItineraryDay(
                theme=day.theme,
                morning=day.morning,
                afternoon=day.afternoon,
                evening=day.evening,
                budget=day.budget
            )
            for day in itinerary_response.days
        ]
        
        summary = ItinerarySummary(
            total_estimated_cost=itinerary_response.summary.total_estimated_cost,
            remaining_budget=itinerary_response.summary.remaining_budget
        )
        
        # Create itinerary document
        itinerary = Itinerary(
            user_id=user_id,
            from_location=itinerary_request.from_location,
            to_location=itinerary_request.to_location,
            dates=itinerary_request.dates,
            budget=itinerary_request.budget,
            model_used=itinerary_request.model,
            travel_itinerary=travel_itinerary,
            days=days,
            summary=summary,
            tips=itinerary_response.tips,
            generation_time_ms=generation_time_ms,
            created_at=datetime.utcnow()
        )
        
        await itinerary.create()
        return itinerary
    
    @staticmethod
    async def get_user_itineraries(user_id: str, limit: int = 10) -> List[Itinerary]:
        """Get itineraries for a specific user."""
        return await Itinerary.find(
            Itinerary.user_id == user_id
        ).sort(-Itinerary.created_at).limit(limit).to_list()
    
    @staticmethod
    async def get_itinerary_by_id(itinerary_id: str) -> Optional[Itinerary]:
        """Get itinerary by ID."""
        try:
            return await Itinerary.get(itinerary_id)
        except Exception:
            return None
    
    @staticmethod
    async def get_cached_itinerary(from_location: str, to_location: str) -> Optional[Itinerary]:
        """Get an existing itinerary for the same route (for caching)."""
        return await Itinerary.find(
            Itinerary.from_location == from_location,
            Itinerary.to_location == to_location
        ).first_or_none()
    
    @staticmethod
    async def delete_itinerary(itinerary_id: str, user_id: Optional[str] = None) -> bool:
        """Delete an itinerary."""
        try:
            # Get the itinerary by ID
            itinerary = await Itinerary.get(itinerary_id)
            
            if not itinerary:
                return False
            
            # Access control: users can delete their own itineraries OR anonymous itineraries
            if user_id and itinerary.user_id and itinerary.user_id != user_id:
                return False  # Different user's itinerary - access denied
            
            # Delete the itinerary
            await itinerary.delete()
            return True
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error deleting itinerary {itinerary_id}: {e}")
            return False


itinerary_service = ItineraryService()
