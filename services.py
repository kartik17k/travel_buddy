from fastapi import HTTPException
from models import ItineraryRequest, ItineraryResponse, DayActivity, TravelSummary, TravelItinerary
from config import settings
import json
import re

try:
    from openai import OpenAI # Ensure OpenAI package is installed
except ImportError:
    OpenAI = None

async def generate_itinerary(request: ItineraryRequest) -> ItineraryResponse:
    """
    Generate a travel itinerary using OpenAI or static response
    """
    return await generate_json_itinerary(request)

async def generate_json_itinerary(request: ItineraryRequest) -> ItineraryResponse:
    """Generate structured JSON itinerary"""
    prompt = (
    f"Create a detailed travel itinerary for a trip from {request.from_location} to {request.to_location} "
    f"for the dates {request.dates} with a total budget of ${request.budget} USD. "

    f"Return ONLY a valid JSON object in the following structure:\n\n"

    f"""{{
    "travel_itinerary": {{
        "from_location": "{request.from_location}",
        "to_location": "{request.to_location}",
        "dates": "{request.dates}",
        "budget": {request.budget}
    }},
    "days": [
        {{
        "theme": "Day theme like Travel, Adventure, Culture, places to visit",
        "morning": "Detailed activity with location name",
        "afternoon": "Detailed activity with specific place",
        "evening": "Detailed activity (e.g. café, walk, show)",
        "budget": float
        }}
        // Add one object per day
    ],
    "summary": {{
        "total_estimated_cost": float,
        "remaining_budget": float
    }},
    "tips": [
        "At least 3 practical travel tips for {request.to_location}"
    ],
    "raw_text": null
    }}"""

    f"\n\nInclude:\n"
    f"- Specific places to visit in {request.to_location}\n"
    f"- Local food or shopping experiences\n"
    f"- Adventure activities unique to {request.to_location} (if any)\n"
    f"- Realistic travel time and cost from {request.from_location}\n"
    f"- Keep budget close to {request.budget} and avoid overspending\n"
    f"- Use emojis where relevant\n"
    f"Return ONLY the JSON. No explanations or extra text."
    )

    if request.model == "openai":
        json_text = await _generate_with_openai(prompt)
    elif request.model == "groq":
        json_text = await _generate_with_groq(prompt)
    else:
        return _generate_static_json_response(request)
    
    try:
        # Parse the JSON response
        json_data = json.loads(json_text)
        return ItineraryResponse(**json_data)
    except json.JSONDecodeError:
        # Fallback to static response if JSON parsing fails
        return _generate_static_json_response(request)

def _generate_static_json_response(request: ItineraryRequest) -> ItineraryResponse:
    """Generate structured JSON response using static template"""
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


async def _generate_with_openai(prompt: str) -> str:
    """Generate itinerary using OpenAI GPT-3.5-turbo"""
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="OpenAI package not installed.")
    
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not set.")
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE
        )
        return response.choices[0].message.content
    except Exception as e:
        error_message = str(e)
        if "insufficient_quota" in error_message or "quota" in error_message.lower():
            raise HTTPException(
                status_code=402, 
                detail="OpenAI quota exceeded. Please check your billing at https://platform.openai.com/account/billing or use 'local' model for static response."
            )
        elif "invalid_api_key" in error_message.lower():
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key.")
        elif "model_not_found" in error_message.lower():
            raise HTTPException(status_code=400, detail="OpenAI model not available. Try using 'gpt-3.5-turbo' model.")
        else:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

async def _generate_with_groq(prompt: str) -> str:
    """Generate itinerary using Groq (fast inference)"""
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="OpenAI package not installed (needed for Groq compatibility).")
    
    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Groq API key not set.")
    
    try:
        # Groq uses OpenAI-compatible client with different base URL
        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.GROQ_MAX_TOKENS,
            temperature=settings.GROQ_TEMPERATURE
        )
        return response.choices[0].message.content
    except Exception as e:
        error_message = str(e)
        if "invalid_api_key" in error_message.lower():
            raise HTTPException(status_code=401, detail="Invalid Groq API key.")
        elif "model_not_found" in error_message.lower():
            raise HTTPException(status_code=400, detail="Groq model not available.")
        else:
            raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

def _generate_with_local_llm(request: ItineraryRequest) -> str:
    """Generate itinerary using local LLM (simulated for now)"""
    return _generate_static_response(request)

def _generate_static_response(request: ItineraryRequest) -> str:
    """Generate itinerary using static template"""
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
