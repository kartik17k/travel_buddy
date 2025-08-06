"""API routes for Travel Buddy."""

from fastapi import APIRouter
from .health import router as health_router
from .itinerary import router as itinerary_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(health_router, tags=["health"])
api_router.include_router(itinerary_router, tags=["itinerary"])

__all__ = ["api_router"]
