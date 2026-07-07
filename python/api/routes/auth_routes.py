# Niskala - Auth Routes
# API routes for authentication

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str


# In-memory user store (for demo)
_users = {}


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login and get access token"""
    # Demo: accept any credentials
    import secrets
    user_id = f"user_{secrets.token_hex(8)}"
    token = secrets.token_hex(32)
    
    _users[user_id] = {
        'username': request.username,
        'token': token,
    }
    
    logger.info(f"User logged in: {request.username}")
    
    return TokenResponse(
        access_token=token,
        user_id=user_id,
    )


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest):
    """Register new user"""
    import secrets
    user_id = f"user_{secrets.token_hex(8)}"
    
    _users[user_id] = {
        'username': request.username,
        'email': request.email,
    }
    
    logger.info(f"User registered: {request.username}")
    
    return UserResponse(
        user_id=user_id,
        username=request.username,
        email=request.email,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """Get current user info"""
    # Demo: return dummy user
    return UserResponse(
        user_id="user_demo",
        username="demo_user",
        email="demo@niskala.id",
    )


@router.post("/logout")
async def logout():
    """Logout current user"""
    return {"message": "Logged out successfully"}
