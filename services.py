from fastapi import HTTPException
from models import ItineraryRequest
from config import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

async def generate_itinerary(request: ItineraryRequest) -> str:
    """
    Generate a travel itinerary using OpenAI or static response
    """
    prompt = (
        f"Generate a detailed travel itinerary for {request.destination} "
        f"with a budget of {request.budget} USD for the dates {request.dates}. "
        "Include daily activities, recommended restaurants, attractions, and budget breakdown."
    )
    
    if request.model == "openai":
        return await _generate_with_openai(prompt)
    else:
        return _generate_static_response(request)

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

def _generate_with_local_llm(request: ItineraryRequest) -> str:
    """Generate itinerary using local LLM (simulated for now)"""
    return _generate_static_response(request)

def _generate_static_response(request: ItineraryRequest) -> str:
    """Generate itinerary using local LLM (simulated for now)"""
    # This is a placeholder - replace with actual local LLM integration
    return f"""
    🌍 Travel Itinerary for {request.destination}
    📅 Dates: {request.dates}
    💰 Budget: ${request.budget} USD
    
    Day 1: Arrival & City Exploration
    - Morning: Airport transfer and hotel check-in
    - Afternoon: Walking tour of city center
    - Evening: Welcome dinner at local restaurant
    - Budget: $150
    
    Day 2: Cultural Immersion
    - Morning: Visit main museums and galleries
    - Afternoon: Historical landmarks tour
    - Evening: Local cultural show or performance
    - Budget: $120
    
    Day 3: Local Cuisine & Shopping
    - Morning: Food market tour and cooking class
    - Afternoon: Shopping at local markets
    - Evening: Fine dining experience
    - Budget: $180
    
    Day 4: Adventure & Nature
    - Full day: Outdoor activities or nature excursion
    - Evening: Relaxation and local nightlife
    - Budget: $200
    
    Day 5: Departure
    - Morning: Last-minute shopping or sightseeing
    - Afternoon: Airport transfer and departure
    - Budget: $80
    
    Total Estimated Cost: $730
    Remaining Budget: ${request.budget - 730}
    
    💡 Tips: Book accommodations in advance, try local transportation, and always have emergency contacts handy!
    """
