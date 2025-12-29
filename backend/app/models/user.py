"""사용자 모델"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nickname = Column(String(50), nullable=False)
    profile_image = Column(String, nullable=True)
    points = Column(Integer, default=0)
    provider = Column(String(20), default="google")
    provider_id = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sightings = relationship("Sighting", back_populates="user", cascade="all, delete-orphan")
    cleanups = relationship("Cleanup", back_populates="user", cascade="all, delete-orphan")
    user_badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    user_creatures = relationship("UserCreature", back_populates="user", cascade="all, delete-orphan")
