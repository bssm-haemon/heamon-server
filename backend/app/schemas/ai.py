"""AI 응답 스키마"""
from pydantic import BaseModel


class CreatureClassifyResponse(BaseModel):
    suggested_creature: str
    category: str
    confidence: float
    rarity: str
    is_confident: bool  # confidence > 0.7


class TrashClassifyResponse(BaseModel):
    trash_type: str
    confidence: float
    has_trash: bool


class CleanupVerifyResponse(BaseModel):
    is_valid: bool
    before_had_trash: bool
    after_has_trash: bool
    confidence: float


class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    similar_image_id: str | None
    hash: str
    is_same_user: bool | None = None
    distance: int | None = None
