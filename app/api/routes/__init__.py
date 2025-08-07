"""API routes for Travel Buddy using MongoDB."""

from fastapi import APIRouter
from .health import router as health_router
from .itinerary import router as itinerary_router
from .auth import router as auth_router

api_router = APIRouter()

# Include core route modules
api_router.include_router(health_router, tags=["health"])
api_router.include_router(itinerary_router, tags=["itinerary"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

__all__ = ["api_router"]
