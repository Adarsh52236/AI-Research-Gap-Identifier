from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, TokenResponse, CurrentUser
from app.api.deps import get_current_user_dep
from app.models.user import User

router = APIRouter()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))

@router.post("/register", response_model=CurrentUser, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user."""
    user = auth_service.register_user(request)
    return user

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return a JWT token.
    FastAPI's OAuth2PasswordRequestForm uses 'username' for the identifier.
    In our system, we require this to be the user's email address.
    """
    user = auth_service.authenticate_user(email=form_data.username, password=form_data.password)
    return auth_service.create_access_token(user)

@router.get("/me", response_model=CurrentUser)
def get_current_user(current_user: User = Depends(get_current_user_dep)):
    """Retrieve the details of the currently authenticated user."""
    return current_user
