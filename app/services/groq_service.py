"""Groq service for generating itineraries."""

from fastapi import HTTPException
from app.core.config import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


async def generate_with_groq(prompt: str) -> str:
    """Generate itinerary using Groq (fast inference)."""
    print(f"🔧 Checking Groq service prerequisites...")
    
    if OpenAI is None:
        print("❌ OpenAI package not available")
        raise HTTPException(status_code=500, detail="OpenAI package not installed (needed for Groq compatibility).")
    
    if not settings.GROQ_API_KEY:
        print("❌ Groq API key not set")
        raise HTTPException(status_code=500, detail="Groq API key not set.")
    
    print(f"✅ Using Groq model: {settings.GROQ_MODEL}")
    print(f"✅ Max tokens: {settings.GROQ_MAX_TOKENS}")
    print(f"✅ Temperature: {settings.GROQ_TEMPERATURE}")
    
    try:
        # Groq uses OpenAI-compatible client with different base URL
        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        print(f"🚀 Making Groq API call...")
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.GROQ_MAX_TOKENS,
            temperature=settings.GROQ_TEMPERATURE
        )
        result = response.choices[0].message.content
        print(f"✅ Groq API call successful! Response length: {len(result)}")
        return result
    except Exception as e:
        error_message = str(e)
        print(f"❌ Groq API error: {error_message}")
        print(f"🔧 Error type: {type(e).__name__}")
        
        if "invalid_api_key" in error_message.lower():
            raise HTTPException(status_code=401, detail="Invalid Groq API key.")
        elif "model_not_found" in error_message.lower():
            raise HTTPException(status_code=400, detail="Groq model not available.")
        else:
            raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")
