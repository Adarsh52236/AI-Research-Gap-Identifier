from fastapi import HTTPException, status
from app.schemas.auth import RegisterRequest, TokenResponse
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token
from app.schemas.user import UserCreate
from datetime import datetime, timezone

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    def register_user(self, request: RegisterRequest) -> User:
        """Register a new user after validating uniqueness."""
        if self.user_repo.get_by_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        if self.user_repo.get_by_username(request.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
            
        hashed_pwd = hash_password(request.password)
        
        user_in = UserCreate(
            full_name=request.full_name,
            email=request.email,
            username=request.username,
            password=request.password
        )
        
        return self.user_repo.create(user_in, hashed_pwd)

    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user by email and password, returning the User object if valid."""
        user = self.user_repo.get_by_email(email)
        
        # We always verify password to prevent timing attacks, even if user isn't found
        # (Though returning early is standard if user is None, but let's just return early with generic error)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Update last login time
        user.last_login_at = datetime.now(timezone.utc)
        self.user_repo.session.commit()
        
        return user

    def create_access_token(self, user: User) -> TokenResponse:
        """Create a standard TokenResponse for a given User."""
        token = create_access_token(subject=str(user.id))
        return TokenResponse(access_token=token)
