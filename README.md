# Travel Buddy API

This FastAPI app accepts user input (destination, budget, dates) and generates a static sample itinerary using OpenAI or a local LLM (gpt-4, mistral).

## Features
- `/generate_itinerary` endpoint: Accepts destination, budget, and dates.
- Uses OpenAI or local LLM to generate a sample itinerary.

## Setup
1. Install dependencies: `pip install fastapi uvicorn openai`
2. Run the app: `uvicorn main:app --reload`

## Usage
Send a POST request to `/generate_itinerary` with JSON body:
```
{
  "destination": "Paris",
  "budget": 1500,
  "dates": "2025-08-10 to 2025-08-15"
}
```

## Note
- You need an OpenAI API key for OpenAI integration. For local LLM, configure the endpoint accordingly.
