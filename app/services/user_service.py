"""User service for MongoDB operations."""

from datetime import datetime
from typing import Optional
from passlib.context import CryptContext

from app.models.database import User
from app.models.auth import UserCreate, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user-related database operations."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        return await User.find_one(User.email == email)
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await User.get(user_id)
    
    @staticmethod
    async def create_user(user_create: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await UserService.get_user_by_email(user_create.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create new user
        hashed_password = UserService.get_password_hash(user_create.password)
        
        user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        await user.create()
        return user
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
        if not UserService.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await user.save()
        
        return user
    
    @staticmethod
    async def update_last_login(user_id: str) -> None:
        """Update user's last login timestamp."""
        user = await UserService.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            await user.save()
    
    @staticmethod
    async def get_all_users() -> list[User]:
        """Get all users."""
        return await User.find_all().to_list()
    
    @staticmethod
    async def get_user_count() -> int:
        """Get total number of users."""
        return await User.count()
    
    @staticmethod
    async def get_active_user_count() -> int:
        """Get number of active users."""
        return await User.find(User.is_active == True).count()


user_service = UserService()
