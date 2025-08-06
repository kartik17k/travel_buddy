"""Main itinerary generation service."""

import json
from fastapi import HTTPException

from app.models import ItineraryRequest, ItineraryResponse
from .openai_service import generate_with_openai
from .groq_service import generate_with_groq
from .static_service import generate_static_json_response


async def generate_itinerary(request: ItineraryRequest) -> ItineraryResponse:
    """
    Generate a travel itinerary using OpenAI, Groq, or static response.
    
    Args:
        request: The itinerary request containing destination, budget, dates, etc.
        
    Returns:
        ItineraryResponse: A structured itinerary with days, activities, and tips.
    """
    return await generate_json_itinerary(request)


async def generate_json_itinerary(request: ItineraryRequest) -> ItineraryResponse:
    """Generate structured JSON itinerary based on the selected model."""
    
    prompt = _build_prompt(request)
    
    try:
        if request.model == "openai":
            print(f"Calling OpenAI API for {request.to_location} itinerary...")
            json_text = await generate_with_openai(prompt)
        elif request.model == "groq":
            print(f"Calling Groq API for {request.to_location} itinerary...")
            json_text = await generate_with_groq(prompt)
            print(f"Groq API response received: {len(json_text)} characters")
        else:
            print(f"Using static response for {request.to_location} itinerary...")
            return generate_static_json_response(request)
        
        # Parse the JSON response
        print(f"Parsing JSON response...")

        # Clean the response - sometimes AI models add extra text
        if json_text.strip().startswith("Here is"):
            # Find the first { and extract JSON from there
            json_start = json_text.find('{')
            if json_start != -1:
                json_text = json_text[json_start:]
                print(f"Cleaned response, extracted JSON from position {json_start}")

        json_data = json.loads(json_text)
        return ItineraryResponse(**json_data)
        
    except json.JSONDecodeError as e:
        # Fallback to static response if JSON parsing fails
        print(f"JSON parsing failed: {str(e)}")
        print(f"Raw response that failed to parse: {json_text[:500]}...")
        return generate_static_json_response(request)
    except Exception as e:
        # Log the error and fallback to static response
        print(f"Error generating itinerary: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        return generate_static_json_response(request)


def _build_prompt(request: ItineraryRequest) -> str:
    """Build the prompt for AI models."""
    return (
        f"You are a travel planning assistant. Create a detailed travel itinerary for a trip from {request.from_location} to {request.to_location} "
        f"for the dates {request.dates} with a total budget of ${request.budget} USD.\n\n"
        f"IMPORTANT: Return ONLY a valid JSON object with no additional text, explanations, or formatting. Start directly with {{ and end with }}.\n\n"
        f"JSON Structure:\n"
        f"""{{
            "travel_itinerary": {{
                "from_location": "{request.from_location}",
                "to_location": "{request.to_location}",
                "dates": "{request.dates}",
                "budget": {request.budget}
            }},
            "days": [
                {{
                    "theme": "Day theme like Travel, Adventure, Culture, etc.",
                    "morning": "Include a specific named place to visit, with detailed activity (e.g., 'Visit Raja's Seat viewpoint for sunrise 🌄 and have coffee at Beans N Brews Cafe')",
                    "afternoon": "Specific activity with place (e.g., 'Explore Madikeri Fort 🏰 and have lunch at Raintree Restaurant')",
                    "evening": "Include named café, show, local market, or walk (e.g., 'Enjoy a traditional Kodava dinner at Coorg Cuisine 🍛 and shop at Kushalnagar market 🛍️')",
                    "budget": float
                }}
            ],
            "summary": {{
                "total_estimated_cost": float,
                "remaining_budget": float
            }},
            "tips": [
                "Include 3-5 specific and practical travel tips for visiting {request.to_location}"
            ],
            "raw_text": null
        }}"""
        f"\n\nConstraints:\n"
        f"- DO NOT EXCEED the given budget of ${request.budget} USD.\n"
        f"- Calculate reasonable travel time and cost from {request.from_location} to {request.to_location}.\n"
        f"- Use real locations, restaurants, cafes, tourist spots, or cultural landmarks in and around {request.to_location}.\n"
        f"- Use emojis to make the experience lively.\n"
        f"- Include at least one adventure activity if available (like rafting, trekking, etc.)\n"
        f"- Avoid generic placeholders like 'main museums' or 'hotel check-in' — be specific.\n"
        f"- Return ONLY the JSON object. No explanation, introduction, or extra text before or after the JSON."
    )
