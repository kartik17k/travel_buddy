"""Itinerary generation routes."""

from fastapi import APIRouter

from app.models import ItineraryRequest, ItineraryResponse
from app.services import generate_itinerary

router = APIRouter()


@router.post("/generate_itinerary", response_model=ItineraryResponse)
async def generate_itinerary_endpoint(request: ItineraryRequest):
    """Generate a travel itinerary based on user input."""
    return await generate_itinerary(request)
