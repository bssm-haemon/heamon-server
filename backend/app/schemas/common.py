"""공통 스키마"""
from pydantic import BaseModel


class Message(BaseModel):
    message: str


class LocationBase(BaseModel):
    latitude: float
    longitude: float
    location_name: str | None = None
