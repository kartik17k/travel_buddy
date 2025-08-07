"""OpenAI service for generating itineraries."""

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


class OpenAIService:
    """Service for generating itineraries using OpenAI."""
    
    async def generate_itinerary(self, request: ItineraryRequest) -> ItineraryResponse:
        """Generate itinerary using OpenAI GPT models."""
        if OpenAI is None:
            raise HTTPException(status_code=500, detail="OpenAI package not installed.")
        
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API key not set.")
        
        # Create the prompt for OpenAI
        prompt = self._create_prompt(request)
        
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE
            )
            
            # Parse the response and convert to ItineraryResponse
            content = response.choices[0].message.content
            return self._parse_response(content, request)
            
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
    
    def _create_prompt(self, request: ItineraryRequest) -> str:
        """Create a prompt for OpenAI to generate an itinerary."""
        return f"""
        Create a detailed travel itinerary in JSON format for the following trip:

        From: {request.from_location}
        To: {request.to_location}
        Dates: {request.dates}
        Budget: ${request.budget} USD

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
                    "budget": 150
                }}
            ],
            "summary": {{
                "total_estimated_cost": 750,
                "remaining_budget": {request.budget - 750}
            }},
            "tips": ["Tip 1", "Tip 2", "Tip 3"]
        }}

        Make sure the itinerary is realistic, fits within the budget, and includes local experiences.
        """
    
    def _parse_response(self, content: str, request: ItineraryRequest) -> ItineraryResponse:
        """Parse OpenAI response and convert to ItineraryResponse."""
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


async def generate_with_openai(prompt: str) -> str:
    """Legacy function for backward compatibility."""
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


# Create service instance
openai_service = OpenAIService()
