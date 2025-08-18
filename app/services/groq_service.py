"""Groq service for generating itineraries."""

import json
from typing import Dict, Any
from fastapi import HTTPException
from app.core.config import settings
from app.models.request import ItineraryRequest
from app.models.response import ItineraryResponse

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class GroqService:
    """Service for generating itineraries using Groq."""
    
    async def generate_itinerary(self, request: ItineraryRequest) -> ItineraryResponse:
        """Generate itinerary using Groq models."""
        if OpenAI is None:
            raise HTTPException(status_code=500, detail="OpenAI package not installed (needed for Groq compatibility).")
        
        if not settings.GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="Groq API key not set.")
        
        # Create the prompt for Groq
        prompt = self._create_prompt(request)
        
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
            
            # Parse the response and convert to ItineraryResponse
            content = response.choices[0].message.content
            return self._parse_response(content, request)
            
        except Exception as e:
            error_message = str(e)
            if "insufficient_quota" in error_message or "quota" in error_message.lower():
                raise HTTPException(
                    status_code=402, 
                    detail="Groq quota exceeded. Please check your usage at https://console.groq.com or use 'local' model for static response."
                )
            elif "invalid_api_key" in error_message.lower():
                raise HTTPException(status_code=401, detail="Invalid Groq API key.")
            elif "model_not_found" in error_message.lower():
                raise HTTPException(status_code=400, detail="Groq model not available.")
            else:
                raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")
    
    def _create_prompt(self, request: ItineraryRequest) -> str:
        """Create a prompt for Groq to generate an itinerary in INR."""
        return f"""
        Create a detailed travel itinerary in JSON format for the following trip:

        From: {request.from_location}
        To: {request.to_location}
        Dates: {request.dates}
        Budget: ₹{request.budget} INR

        Please return a JSON response with the following structure:
        {{
            "travel_itinerary": {{
                "from_location": "{request.from_location}",
                "to_location": "{request.to_location}",
                "dates": "{request.dates}",
                "budget": {request.budget}
            }},
            "days": [
                {{
                    "theme": "Day theme",
                    "morning": "Morning activity",
                    "afternoon": "Afternoon activity", 
                    "evening": "Evening activity",
                    "budget": 1500
                }}
            ],
            "summary": {{
                "total_estimated_cost": 7500,
                "remaining_budget": {request.budget - 7500}
            }},
            "tips": ["Tip 1", "Tip 2", "Tip 3"]
        }}

        Make sure the itinerary is realistic, fits within the budget, and includes local experiences.
        """
    
    def _parse_response(self, content: str, request: ItineraryRequest) -> ItineraryResponse:
        """Parse Groq response and convert to ItineraryResponse."""
        try:
            # Try to extract JSON from the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                return ItineraryResponse(**data)
            else:
                # Fallback to static response if parsing fails
                from app.services.static_service import static_service
                return static_service.generate_itinerary(request)
                
        except Exception:
            # Fallback to static response if parsing fails
            from app.services.static_service import static_service
            return static_service.generate_itinerary(request)


async def generate_with_groq(prompt: str) -> str:
    """Legacy function - Generate itinerary using Groq (fast inference)."""
    print(f"Checking Groq service prerequisites...")
    
    if OpenAI is None:
        print("OpenAI package not available")
        raise HTTPException(status_code=500, detail="OpenAI package not installed (needed for Groq compatibility).")
    
    if not settings.GROQ_API_KEY:
        print("Groq API key not set")
        raise HTTPException(status_code=500, detail="Groq API key not set.")
    
    print(f"Using Groq model: {settings.GROQ_MODEL}")
    print(f"Max tokens: {settings.GROQ_MAX_TOKENS}")
    print(f"Temperature: {settings.GROQ_TEMPERATURE}")
    
    try:
        # Groq uses OpenAI-compatible client with different base URL
        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        print(f"Making Groq API call...")
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.GROQ_MAX_TOKENS,
            temperature=settings.GROQ_TEMPERATURE
        )
        result = response.choices[0].message.content
        print(f"Groq API call successful! Response length: {len(result)}")
        return result
    except Exception as e:
        error_message = str(e)
        print(f"Groq API error: {error_message}")
        print(f"Error type: {type(e).__name__}")
        
        if "invalid_api_key" in error_message.lower():
            raise HTTPException(status_code=401, detail="Invalid Groq API key.")
        elif "model_not_found" in error_message.lower():
            raise HTTPException(status_code=400, detail="Groq model not available.")
        else:
            raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")


# Create service instance
groq_service = GroqService()
