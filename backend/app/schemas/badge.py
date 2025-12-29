"""뱃지 스키마"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class BadgeBase(BaseModel):
    name: str
    description: str | None = None
    condition_type: str | None = None  # sighting_count, cleanup_count, streak...
    condition_value: int | None = None


class BadgeCreate(BadgeBase):
    id: UUID | None = None  # 정적 ID를 지정해 등록할 수 있도록 허용


class BadgeResponse(BadgeBase):
    id: UUID
    created_at: datetime | None = None

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
