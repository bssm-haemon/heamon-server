"""생물 목격 스키마"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.schemas.common import LocationBase


class SightingBase(LocationBase):
    memo: str | None = None


class SightingCreate(SightingBase):
    creature_id: str | None = None
    ai_suggestion: str | None = None
    ai_confidence: float | None = None


class SightingResponse(SightingBase):
    id: UUID
    user_id: UUID
    creature_id: str | None
    photo_url: str
    image_hash: str | None
    ai_suggestion: str | None
    ai_confidence: float | None
    status: str
    points_earned: int
    created_at: datetime

    class Config:
        from_attributes = True


class SightingListResponse(BaseModel):
    sightings: list[SightingResponse]
    total: int
    page: int
    limit: int


class SightingStatusUpdate(BaseModel):
    status: str  # approved, rejected
    creature_id: str | None = None  # 승인 시 생물 확정


class SightingDetailResponse(SightingResponse):
    user_nickname: str | None = None
    creature_name: str | None = None
