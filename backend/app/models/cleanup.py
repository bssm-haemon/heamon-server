"""쓰레기 수거 기록 모델"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Cleanup(Base):
    __tablename__ = "cleanups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    before_photo_url = Column(String, nullable=False)
    after_photo_url = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(100), nullable=True)
    trash_type = Column(String(30), nullable=False)  # plastic, styrofoam, fishing_gear...
    amount = Column(String(20), nullable=False)  # handful, one_bag, large
    before_image_hash = Column(String(64), nullable=True)
    after_image_hash = Column(String(64), nullable=True)
    ai_verified = Column(Boolean, default=False)
    ai_confidence = Column(Float, nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="cleanups")
