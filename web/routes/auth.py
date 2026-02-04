from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from ..auth import authenticate_user, create_access_token, get_current_user
from ..config import settings
from ..logging import get_logger
from ..database import User, get_db

router = APIRouter(prefix="/api/auth", tags=["authentication"])
logger = get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str


class UserResponse(BaseModel):
    """User information response model"""

    id: int
    username: str
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login endpoint - accepts username and password, returns JWT token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Set cookie for browser navigation
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,  # Convert to seconds
        samesite="lax",
        secure=settings.secure_cookies,  # Controlled by SECURE_COOKIES environment variable
    )

    logger.info(f"Login: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    """Logout endpoint - clears authentication cookie"""
    # Clear the authentication cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=settings.secure_cookies,
    )

    logger.info(f"Logout: {current_user.username}")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information - requires valid JWT token"""
    return current_user
