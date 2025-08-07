from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
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
        return UserResponse(
            id=str(db_user.id),
            email=db_user.email,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            created_at=db_user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


@router.post("/login", response_model=Token)
async def login_user(login_data: LoginRequest, _: None = Depends(require_mongodb)):
    """Authenticate user and return access token."""
    user = await user_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/logout")
async def logout_user():
    """Logout user (client should delete the token)."""
    return {"message": "Successfully logged out. Please delete the token on client side."}


@router.get("/verify-token")
async def verify_user_token(current_user: User = Depends(get_current_active_user)):
    """Verify if the current token is valid."""
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name
    }
