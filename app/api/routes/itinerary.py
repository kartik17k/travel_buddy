"""Itinerary generation routes using MongoDB."""

import time
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends

from app.models.request import ItineraryRequest
from app.models.response import ItineraryResponse
from app.services.itinerary_service import itinerary_service
from app.services.openai_service import openai_service
from app.services.groq_service import groq_service
from app.services.static_service import static_service
from app.api.dependencies import get_current_active_user
from app.models.database import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate_itinerary", response_model=ItineraryResponse)
async def generate_itinerary(
    request: ItineraryRequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Generate a travel itinerary using AI or static responses.
    
    Supports authentication - if user is logged in, itinerary will be saved.
    """
    logger.info(f"Generating itinerary from {request.from_location} to {request.to_location} using {request.model}")
    
    start_time = time.time()
    
    try:
        # Generate itinerary based on selected model
        if request.model == "openai":
            response = await openai_service.generate_itinerary(request)
        elif request.model == "groq":
            response = await groq_service.generate_itinerary(request)
        else:  # Default to static/local
            response = static_service.generate_itinerary(request)
        
        generation_time = (time.time() - start_time) * 1000
        
        # Save itinerary if user is authenticated
        if current_user:
            try:
                saved_itinerary = await itinerary_service.save_itinerary(
                    itinerary_request=request,
                    itinerary_response=response,
                    user_id=str(current_user.id),
                    generation_time_ms=generation_time
                )
                logger.info(f"Itinerary saved with ID: {saved_itinerary.id}")
            except Exception as e:
                logger.error(f"Failed to save itinerary: {e}")
                # Don't fail the request if saving fails
        
        logger.info(f"Itinerary generated successfully in {generation_time:.2f}ms")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating itinerary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate itinerary: {str(e)}"
        )


@router.get("/my-itineraries", response_model=List[ItineraryResponse])
async def get_my_itineraries(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Get saved itineraries for the current user."""
    try:
        itineraries = await itinerary_service.get_user_itineraries(
            user_id=str(current_user.id),
            limit=limit
        )
        
        # Convert MongoDB documents to response format
        response_list = []
        for itinerary in itineraries:
            response = ItineraryResponse(
                travel_itinerary={
                    "from_location": itinerary.travel_itinerary.from_location,
                    "to_location": itinerary.travel_itinerary.to_location,
                    "dates": itinerary.travel_itinerary.dates,
                    "budget": itinerary.travel_itinerary.budget
                },
                days=[
                    {
                        "theme": day.theme,
                        "morning": day.morning,
                        "afternoon": day.afternoon,
                        "evening": day.evening,
                        "budget": day.budget
                    }
                    for day in itinerary.days
                ],
                summary={
                    "total_estimated_cost": itinerary.summary.total_estimated_cost,
                    "remaining_budget": itinerary.summary.remaining_budget
                },
                tips=itinerary.tips
            )
            response_list.append(response)
        
        return response_list
        
    except Exception as e:
        logger.error(f"Error fetching user itineraries: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch itineraries"
        )


@router.get("/itinerary/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(
    itinerary_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific itinerary by ID."""
    try:
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary:
            raise HTTPException(status_code=404, detail="Itinerary not found")
        
        # Check if itinerary belongs to user
        if itinerary.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert to response format
        response = ItineraryResponse(
            travel_itinerary={
                "from_location": itinerary.travel_itinerary.from_location,
                "to_location": itinerary.travel_itinerary.to_location,
                "dates": itinerary.travel_itinerary.dates,
                "budget": itinerary.travel_itinerary.budget
            },
            days=[
                {
                    "theme": day.theme,
                    "morning": day.morning,
                    "afternoon": day.afternoon,
                    "evening": day.evening,
                    "budget": day.budget
                }
                for day in itinerary.days
            ],
            summary={
                "total_estimated_cost": itinerary.summary.total_estimated_cost,
                "remaining_budget": itinerary.summary.remaining_budget
            },
            tips=itinerary.tips
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching itinerary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch itinerary"
        )


@router.delete("/itinerary/{itinerary_id}")
async def delete_itinerary(
    itinerary_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a specific itinerary."""
    try:
        success = await itinerary_service.delete_itinerary(
            itinerary_id=itinerary_id,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Itinerary not found or access denied")
        
        return {"message": "Itinerary deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting itinerary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete itinerary"
        )
