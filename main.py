from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import api_router


def create_app() -> FastAPI:
    # Initialize FastAPI app with configuration
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION
    )
    
    # Register all routes
    app.include_router(api_router)
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
