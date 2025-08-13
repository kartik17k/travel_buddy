
import logging
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.models.auth import UserCreate, User as UserResponse, Token, LoginRequest
from app.services.user_service import user_service
from app.core.auth import create_access_token
from app.core.config import settings
from app.api.dependencies import get_current_active_user, require_mongodb
from app.models.database import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, _: None = Depends(require_mongodb)):
    """Register a new user."""
    try:
        db_user = await user_service.create_user(user)
        user_id = getattr(db_user, 'id', None) or getattr(db_user, '_id', None)
        created_at = db_user.created_at.isoformat() if db_user.created_at else None
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "message": "User registered successfully",
                "data": {
                    "id": str(user_id),
                    "email": db_user.email,
                    "full_name": db_user.full_name,
                    "is_active": db_user.is_active,
                    "created_at": created_at
                }
            }
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": str(e)
            }
        )
    except Exception as e:
        import traceback
        logger = logging.getLogger("register_user")
        logger.error(f"Registration failed: {e}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": f"Failed to create user account: {str(e)}"
            }
        )


@router.post("/login", response_model=Token)
async def login_user(login_data: LoginRequest, _: None = Depends(require_mongodb)):
    """Authenticate user and return access token."""
    user = await user_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status": "error",
                "message": "Incorrect email or password"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not user.is_active:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "User account is deactivated"
            }
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "message": "Login successful",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_data
            }
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "message": "Fetched user info successfully",
            "data": UserResponse(
                id=str(current_user.id),
                email=current_user.email,
                full_name=current_user.full_name,
                is_active=current_user.is_active,
                created_at=current_user.created_at
            ).dict()
        }
    )


@router.post("/logout")
async def logout_user():
    """Logout user (client should delete the token)."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "message": "Successfully logged out. Please delete the token on client side."
        }
    )


@router.get("/users", response_model=list[UserResponse])
async def get_all_users(_: None = Depends(require_mongodb)):
    """Get all users (public endpoint)."""
    try:
        users = await user_service.get_all_users()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": "Fetched all users successfully",
                "data": [
                    UserResponse(
                        id=str(user.id),
                        email=user.email,
                        full_name=user.full_name,
                        is_active=user.is_active,
                        created_at=user.created_at
                    ).dict() for user in users
                ]
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Failed to retrieve users"
            }
        )


@router.get("/verify-token")
async def verify_user_token(current_user: User = Depends(get_current_active_user)):
    """Verify if the current token is valid."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "message": "Token is valid",
            "data": {
                "valid": True,
                "user_id": str(current_user.id),
                "email": current_user.email,
                "full_name": current_user.full_name
            }
        }
    )
