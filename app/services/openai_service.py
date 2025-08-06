"""OpenAI service for generating itineraries."""

from fastapi import HTTPException
from app.core.config import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


async def generate_with_openai(prompt: str) -> str:
    """Generate itinerary using OpenAI GPT models."""
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
