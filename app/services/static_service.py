"""Static response service for generating fallback itineraries."""

from app.models import (
    ItineraryRequest, 
    ItineraryResponse, 
    DayActivity, 
    TravelSummary, 
    TravelItinerary
)


def generate_static_json_response(request: ItineraryRequest) -> ItineraryResponse:
    """Generate structured JSON response using static template."""
    return ItineraryResponse(
        travel_itinerary=TravelItinerary(
            from_location=request.from_location,
            to_location=request.to_location,
            dates=request.dates,
            budget=request.budget
        ),
        days=[
            DayActivity(
                theme="Travel Day & Arrival",
                morning=f"Departure from {request.from_location}",
                afternoon=f"Journey to {request.to_location} and hotel check-in",
                evening="Welcome dinner and local area exploration",
                budget=150
            ),
            DayActivity(
                theme="Cultural Immersion",
                morning=f"Visit main museums and galleries in {request.to_location}",
                afternoon="Historical landmarks tour",
                evening="Local cultural show or performance",
                budget=120
            ),
            DayActivity(
                theme="Local Cuisine & Shopping",
                morning="Food market tour and cooking class",
                afternoon="Shopping at local markets",
                evening="Fine dining experience",
                budget=180
            ),
            DayActivity(
                theme="Adventure & Nature",
                morning=f"Outdoor activities or nature excursion near {request.to_location}",
                afternoon="Continue outdoor activities",
                evening="Relaxation and local nightlife",
                budget=200
            ),
            DayActivity(
                theme="Departure",
                morning="Last-minute shopping or sightseeing",
                afternoon=f"Return journey to {request.from_location}",
                evening="Departure",
                budget=80
            )
        ],
        summary=TravelSummary(
            total_estimated_cost=730,
            remaining_budget=request.budget - 730
        ),
        tips=[
            f"Book accommodations in {request.to_location} in advance",
            "Try local transportation for authentic experience",
            "Always have emergency contacts handy",
            f"Learn basic phrases in the local language of {request.to_location}",
            "Keep digital and physical copies of important documents"
        ]
    )


def generate_static_text_response(request: ItineraryRequest) -> str:
    """Generate itinerary using static template (text format)."""
    return f"""🌍 Travel Itinerary: {request.from_location} → {request.to_location}
📅 Dates: {request.dates}
💰 Budget: ${request.budget} USD

Day 1: Travel Day & Arrival
- Morning: Departure from {request.from_location}
- Afternoon: Journey to {request.to_location} and hotel check-in
- Evening: Welcome dinner and local area exploration
- Budget: $150

Day 2: Cultural Immersion
- Morning: Visit main museums and galleries in {request.to_location}
- Afternoon: Historical landmarks tour
- Evening: Local cultural show or performance
- Budget: $120

Day 3: Local Cuisine & Shopping
- Morning: Food market tour and cooking class
- Afternoon: Shopping at local markets
- Evening: Fine dining experience
- Budget: $180

Day 4: Adventure & Nature
- Full day: Outdoor activities or nature excursion near {request.to_location}
- Evening: Relaxation and local nightlife
- Budget: $200

Day 5: Departure
- Morning: Last-minute shopping or sightseeing
- Afternoon: Return journey to {request.from_location}
- Budget: $80

Total Estimated Cost: $730
Remaining Budget: ${request.budget - 730}

💡 Tips: Book accommodations in {request.to_location} in advance, try local transportation, and always have emergency contacts handy!
"""
