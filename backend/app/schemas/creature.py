"""생물 도감 스키마"""
from datetime import datetime
from pydantic import BaseModel


class CreatureBase(BaseModel):
    name: str
    name_en: str | None = None
    category: str
    description: str | None = None
    rarity: str  # common, rare, legendary
    points: int


class CreatureCreate(CreatureBase):
    image_url: str | None = None


class CreatureResponse(CreatureBase):
    id: str
    image_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class CreatureListResponse(BaseModel):
    creatures: list[CreatureResponse]
    total: int


class UserCreatureResponse(BaseModel):
    creature_id: str
    discovered_at: datetime
    first_sighting_id: str | None

    class Config:
        from_attributes = True


class CollectionStatsResponse(BaseModel):
    total_creatures: int
    discovered_count: int
    completion_rate: float
    by_rarity: dict[str, dict[str, int]]  # {"common": {"total": 10, "discovered": 5}, ...}
