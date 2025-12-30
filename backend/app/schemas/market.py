"""마켓 스키마"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class MarketItem(BaseModel):
    creature_id: str
    name: str
    name_en: Optional[str] = None
    category: str
    image_url: Optional[str] = None
    rarity: str
    price: int
    in_aquarium: bool


class MarketListResponse(BaseModel):
    items: List[MarketItem]
    total: int
    user_points: int


class PurchaseRequest(BaseModel):
    creature_ids: List[str]


class PurchaseResponse(BaseModel):
    success: bool
    purchased: List[str]
    total_spent: int
    remaining_points: int
    message: str
