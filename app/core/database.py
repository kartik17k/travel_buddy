"""MongoDB database configuration and connection."""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from app.core.config import settings
from app.models.database import User, Itinerary

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None
    connected: bool = False


db = MongoDB()


async def connect_to_mongo():
    """Create database connection."""
    try:
        logger.info(f"Attempting to connect to MongoDB Atlas...")
        
        # MongoDB Atlas connection with optimized settings
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=10000,  # 10 second timeout for Atlas
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            retryWrites=True,
            w='majority'
        )
        
        # Test the connection
        await db.client.admin.command('ping')
        
        db.database = db.client[settings.DATABASE_NAME]
        
        # Initialize Beanie with document models
        await init_beanie(
            database=db.database,
            document_models=[User, Itinerary]
        )
        
        db.connected = True
        logger.info(f"Connected to MongoDB Atlas: {settings.DATABASE_NAME}")
        
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB Atlas: {e}")
        logger.warning("API will start but MongoDB features will be disabled")
        logger.warning("To fix this:")
        logger.warning("   1. Replace <db_password> with your actual password in .env")
        logger.warning("   2. Whitelist your IP in MongoDB Atlas Network Access")
        logger.warning("   3. Ensure your MongoDB Atlas cluster is running")
        
        db.connected = False
        # Don't raise exception - let the app start without MongoDB


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")
        db.connected = False


async def get_database():
    """Get database instance."""
    if not db.connected:
        raise Exception("MongoDB not connected. Please start MongoDB and restart the server.")
    return db.database


def is_mongodb_connected() -> bool:
    """Check if MongoDB is connected."""
    return db.connected
