"""Itinerary service for MongoDB operations."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from app.models.database import Itinerary, User, ItineraryDay, ItinerarySummary, TravelItineraryInfo
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
            from_location=itinerary_response.travel_itinerary["from_location"],
            to_location=itinerary_response.travel_itinerary["to_location"],
            dates=itinerary_response.travel_itinerary["dates"],
            budget=itinerary_response.travel_itinerary["budget"]
        )
        
        days = [
            ItineraryDay(
                theme=day["theme"],
                morning=day["morning"],
                afternoon=day["afternoon"],
                evening=day["evening"],
                budget=day["budget"]
            )
            for day in itinerary_response.days
        ]
        
        summary = ItinerarySummary(
            total_estimated_cost=itinerary_response.summary["total_estimated_cost"],
            remaining_budget=itinerary_response.summary["remaining_budget"]
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
    async def get_all_itineraries(limit: int = 100) -> List[Itinerary]:
        """Get all itineraries."""
        return await Itinerary.find_all().sort(-Itinerary.created_at).limit(limit).to_list()
    
    @staticmethod
    async def get_itinerary_count() -> int:
        """Get total number of itineraries."""
        return await Itinerary.count()
    
    @staticmethod
    async def get_popular_destinations(limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular destinations with counts."""
        pipeline = [
            {
                "$group": {
                    "_id": "$to_location",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": limit
            },
            {
                "$project": {
                    "destination": "$_id",
                    "count": 1,
                    "_id": 0
                }
            }
        ]
        
        results = await Itinerary.aggregate(pipeline).to_list(length=limit)
        return results
    
    @staticmethod
    async def get_model_usage_stats() -> List[Dict[str, Any]]:
        """Get AI model usage statistics."""
        pipeline = [
            {
                "$group": {
                    "_id": "$model_used",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$project": {
                    "model": "$_id",
                    "count": 1,
                    "_id": 0
                }
            }
        ]
        
        results = await Itinerary.aggregate(pipeline).to_list()
        return results
    
    @staticmethod
    async def get_average_budget() -> Optional[float]:
        """Get average budget across all itineraries."""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_budget": {"$avg": "$budget"}
                }
            }
        ]
        
        result = await Itinerary.aggregate(pipeline).to_list(length=1)
        return result[0]["avg_budget"] if result else 0.0
    
    @staticmethod
    async def search_itineraries(
        destination: Optional[str] = None,
        origin: Optional[str] = None,
        min_budget: Optional[float] = None,
        max_budget: Optional[float] = None,
        model: Optional[str] = None,
        limit: int = 50
    ) -> List[Itinerary]:
        """Search itineraries with filters."""
        query = {}
        
        if destination:
            query["to_location"] = {"$regex": destination, "$options": "i"}
        
        if origin:
            query["from_location"] = {"$regex": origin, "$options": "i"}
        
        if min_budget is not None or max_budget is not None:
            budget_query = {}
            if min_budget is not None:
                budget_query["$gte"] = min_budget
            if max_budget is not None:
                budget_query["$lte"] = max_budget
            query["budget"] = budget_query
        
        if model:
            query["model_used"] = model
        
        return await Itinerary.find(query).sort(-Itinerary.created_at).limit(limit).to_list()
    
    @staticmethod
    async def delete_itinerary(itinerary_id: str, user_id: Optional[str] = None) -> bool:
        """Delete an itinerary."""
        try:
            query = {"_id": ObjectId(itinerary_id)}
            if user_id:
                query["user_id"] = user_id
            
            itinerary = await Itinerary.find_one(query)
            if itinerary:
                await itinerary.delete()
                return True
            return False
        except Exception:
            return False


itinerary_service = ItineraryService()
