"""사용자 스키마"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    nickname: str


class UserCreate(UserBase):
    provider: str = "google"
    provider_id: str | None = None
    profile_image: str | None = None


class UserUpdate(BaseModel):
    nickname: str | None = None
    profile_image: str | None = None


class UserResponse(UserBase):
    id: UUID
    profile_image: str | None
    points: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    sighting_count: int = 0
    cleanup_count: int = 0
    creature_count: int = 0
    badge_count: int = 0


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
