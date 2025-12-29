"""쓰레기 수거 스키마"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.schemas.common import LocationBase


class CleanupBase(LocationBase):
    trash_type: str  # plastic, styrofoam, fishing_gear, glass, metal, other
    amount: str  # handful, one_bag, large


class CleanupCreate(CleanupBase):
    ai_verified: bool = False
    ai_confidence: float | None = None


class CleanupResponse(CleanupBase):
    id: UUID
    user_id: UUID
    before_photo_url: str
    after_photo_url: str
    before_image_hash: str | None
    after_image_hash: str | None
    ai_verified: bool
    ai_confidence: float | None
    status: str
    points_earned: int
    created_at: datetime

    class Config:
        from_attributes = True


class CleanupListResponse(BaseModel):
    cleanups: list[CleanupResponse]
    total: int
    page: int
    limit: int


class CleanupDetailResponse(CleanupResponse):
    user_nickname: str | None = None
