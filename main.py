from fastapi import FastAPI
from models import ItineraryRequest, ItineraryResponse
from services import generate_itinerary
from config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Travel Buddy API is running"}

# Endpoint to generate itinerary
@app.post("/generate_itinerary", response_model=ItineraryResponse)
async def generate_itinerary_endpoint(request: ItineraryRequest):
    """Generate a travel itinerary based on user input"""
    return await generate_itinerary(request)
