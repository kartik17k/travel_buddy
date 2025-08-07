# Configuration settings for the Travel Buddy API
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Groq Configuration
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "1000"))
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    
    # API Configuration
    APP_NAME: str = os.getenv("APP_NAME", "Travel Buddy API")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DESCRIPTION: str = os.getenv("DESCRIPTION", "Generate personalized travel itineraries using AI")
    
    # Authentication Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production-make-it-very-long-and-random")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "travel_buddy")
    
    # Development Settings
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
