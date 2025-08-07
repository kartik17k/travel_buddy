#!/usr/bin/env python3
"""Database setup and initialization script for Travel Buddy."""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.database import User, Itinerary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialize MongoDB database and collections."""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        logger.info(f"Connected to MongoDB: {settings.MONGODB_URL}")
        logger.info(f"Using database: {settings.DATABASE_NAME}")
        
        # Create collections with indexes
        logger.info("Creating users collection...")
        users_collection = db.users
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("created_at")
        
        logger.info("Creating itineraries collection...")
        itineraries_collection = db.itineraries
        await itineraries_collection.create_index("user_id")
        await itineraries_collection.create_index("created_at")
        await itineraries_collection.create_index("to_location")
        await itineraries_collection.create_index("from_location")
        await itineraries_collection.create_index("model_used")
        
        # Test the connection
        await db.command("ping")
        logger.info("✅ Database connection successful!")
        
        # Display collection info
        collections = await db.list_collection_names()
        logger.info(f"Available collections: {collections}")
        
        user_count = await users_collection.count_documents({})
        itinerary_count = await itineraries_collection.count_documents({})
        
        logger.info(f"Current documents - Users: {user_count}, Itineraries: {itinerary_count}")
        
        client.close()
        logger.info("Database initialization completed!")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def test_connection():
    """Test database connection."""
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        # Test connection
        await db.command("ping")
        logger.info("✅ Database connection test successful!")
        
        # Display server info
        server_info = await db.command("serverStatus")
        logger.info(f"MongoDB version: {server_info.get('version', 'Unknown')}")
        logger.info(f"Host: {server_info.get('host', 'Unknown')}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


if __name__ == "__main__":
    print("Travel Buddy Database Setup")
    print("=" * 40)
    
    # Load environment variables
    import os
    from dotenv import load_dotenv
    
    if os.path.exists(".env"):
        load_dotenv()
        print("Loaded environment variables")

    print(f"Database URL: {settings.MONGODB_URL}")
    print(f"Database: {settings.DATABASE_NAME}")
    print()
    
    # Test connection first
    print("Testing database connection...")
    if asyncio.run(test_connection()):
        print("\nInitializing database...")
        asyncio.run(init_database())
    else:
        print("\nCannot proceed without database connection.")
        print("\nTo start MongoDB:")
        print("   1. Install MongoDB locally, or")
        print("   2. Run: docker-compose up -d")
        print("   3. Update MONGODB_URL in .env if needed")
