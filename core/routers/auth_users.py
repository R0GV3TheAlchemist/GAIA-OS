"""
core/routers/auth_users.py
GAIA Auth Endpoints — Register + Login

POST /auth/register  — create account (email, username, password)
POST /auth/login     — sign in (username or email + password)
GET  /auth/me        — return current user profile

Canon: C01, C15
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, field_validator
from typing import Optional

from core.auth import create_access_token, require_auth, TokenPayload
from core.user_store import register_user, login_user, get_user_by_id, AuthError
import os

router = APIRouter(prefix="/auth", tags=["auth"])

_TOKEN_EXPIRE = int(os.environ.get("GAIA_TOKEN_EXPIRE", "60"))


class RegisterRequest(BaseModel):
    email:    str
    username: str
    password: str

    @field_validator('email')
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v or '@' not in v:
            raise ValueError('A valid email is required.')
        return v.strip().lower()

    @field_validator('username')
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Username must be at least 2 characters.')
        return v

    @field_validator('password')
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters.')
        return v


class LoginRequest(BaseModel):
    username: str   # accepts username OR email
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int
    user_id:      str
    username:     str
    email:        str
    role:         str


class MeResponse(BaseModel):
    user_id:  str
    username: Optional[str] = None
    email:    Optional[str] = None
    role:     str


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest):
    """
    POST /auth/register
    Create a new GAIA account.
    Returns a JWT access token on success.
    """
    try:
        user = register_user(
            email=req.email,
            username=req.username,
            password=req.password,
        )
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token(
        user_id=user.user_id,
        role=user.role,
        expires_in=_TOKEN_EXPIRE,
    )
    return AuthResponse(
        access_token=token,
        expires_in=_TOKEN_EXPIRE * 60,
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role,
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    """
    POST /auth/login
    Sign in with username (or email) + password.
    Returns a JWT access token on success.
    """
    try:
        user = login_user(req.username, req.password)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))

    token = create_access_token(
        user_id=user.user_id,
        role=user.role,
        expires_in=_TOKEN_EXPIRE,
    )
    return AuthResponse(
        access_token=token,
        expires_in=_TOKEN_EXPIRE * 60,
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role,
    )


@router.get("/me", response_model=MeResponse)
def auth_me(user: TokenPayload = Depends(require_auth)):
    """
    GET /auth/me
    Returns the profile for the authenticated user.
    """
    record = get_user_by_id(user.user_id)
    return MeResponse(
        user_id=user.user_id,
        username=record.username if record else None,
        email=record.email if record else None,
        role=user.role,
    )
