"""Pydantic 스키마"""
from app.schemas.common import Message, LocationBase
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserProfile
from app.schemas.creature import CreatureCreate, CreatureResponse, CreatureListResponse
from app.schemas.sighting import SightingCreate, SightingResponse, SightingListResponse, SightingStatusUpdate
from app.schemas.cleanup import CleanupCreate, CleanupResponse, CleanupListResponse
from app.schemas.ai import (
    CreatureClassifyResponse,
    TrashClassifyResponse,
    CleanupVerifyResponse,
    DuplicateCheckResponse,
)

__all__ = [
    "Message",
    "LocationBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "CreatureCreate",
    "CreatureResponse",
    "CreatureListResponse",
    "SightingCreate",
    "SightingResponse",
    "SightingListResponse",
    "SightingStatusUpdate",
    "CleanupCreate",
    "CleanupResponse",
    "CleanupListResponse",
    "CreatureClassifyResponse",
    "TrashClassifyResponse",
    "CleanupVerifyResponse",
    "DuplicateCheckResponse",
]
