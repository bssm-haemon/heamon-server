"""뱃지 스키마"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class BadgeBase(BaseModel):
    name: str
    description: str | None = None
    icon_url: str | None = None
    condition_type: str | None = None  # sighting_count, cleanup_count, streak...
    condition_value: int | None = None


class BadgeCreate(BadgeBase):
    pass


class BadgeResponse(BadgeBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserBadgeResponse(BaseModel):
    badge: BadgeResponse
    earned_at: datetime

    class Config:
        from_attributes = True


class BadgeListResponse(BaseModel):
    badges: list[BadgeResponse]
    total: int
