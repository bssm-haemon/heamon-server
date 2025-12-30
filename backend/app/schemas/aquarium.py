"""아쿠아리움 스키마"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class AquariumItem(BaseModel):
    id: UUID
    creature_id: str
    creature_name: Optional[str] = None
    creature_image: Optional[str] = None
    rarity: Optional[str] = None
    position_x: float
    position_y: float
    purchased_at: datetime

    class Config:
        from_attributes = True


class AquariumListResponse(BaseModel):
    aquarium: List[AquariumItem]
    total: int
