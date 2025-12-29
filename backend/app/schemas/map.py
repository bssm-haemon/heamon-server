"""지도 데이터 스키마"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class MapMarker(BaseModel):
    id: UUID
    latitude: float
    longitude: float
    type: str  # sighting, cleanup
    created_at: datetime
    location_name: str | None = None


class SightingMarker(MapMarker):
    creature_name: str | None = None
    rarity: str | None = None
    photo_url: str | None = None


class CleanupMarker(MapMarker):
    trash_type: str
    amount: str


class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    weight: float = 1.0


class MapDataResponse(BaseModel):
    markers: list[MapMarker]
    total: int


class HeatmapResponse(BaseModel):
    points: list[HeatmapPoint]
    type: str  # sighting, cleanup, combined
