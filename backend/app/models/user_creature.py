"""유저 도감 (발견한 생물) 모델"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class UserCreature(Base):
    __tablename__ = "user_creatures"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    creature_id = Column(UUID(as_uuid=True), ForeignKey("creatures.id"), primary_key=True)
    first_sighting_id = Column(UUID(as_uuid=True), ForeignKey("sightings.id"), nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_creatures")
    creature = relationship("Creature", back_populates="user_creatures")
