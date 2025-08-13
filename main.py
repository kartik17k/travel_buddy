"""FastAPI application with MongoDB."""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.routes import api_router


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting Travel Buddy API v{settings.VERSION} with MongoDB")
    
    # Connect to MongoDB
    await connect_to_mongo()
    logger.info("Connected to MongoDB")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Travel Buddy API")
    await close_mongo_connection()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # CORS Middleware for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Global Exception Handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc) if settings.DEBUG else "Contact support"
            }
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "MongoDB"
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        from app.core.database import is_mongodb_connected
        
        return {
            "message": "🍃 Welcome to Travel Buddy API",
            "version": settings.VERSION,
            "description": settings.DESCRIPTION,
            "mongodb_connected": is_mongodb_connected(),
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc"
            },
            "endpoints": {
                "health": "GET /health",
                "generate_itinerary": "POST /generate_itinerary",
                "auth_register": "POST /auth/register",
                "auth_login": "POST /auth/login"
            },
            "status": "🚀 API is running!"
        }
    
    # Documentation redirect endpoints for common typos
    @app.get("/redocs")
    async def redirect_redocs():
        """Redirect /redocs to /redoc."""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/redoc")
    
    # Register all routes
    app.include_router(api_router)
    
    return app


# Create the app instance
app = create_app()


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
