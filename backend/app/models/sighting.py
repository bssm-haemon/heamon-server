"""생물 목격 기록 모델"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Sighting(Base):
    __tablename__ = "sightings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creature_id = Column(UUID(as_uuid=True), ForeignKey("creatures.id"), nullable=True)
    photo_url = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(100), nullable=True)
    memo = Column(Text, nullable=True)
    image_hash = Column(String(64), nullable=True)
    ai_suggestion = Column(String(50), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sightings")
    creature = relationship("Creature", back_populates="sightings")
