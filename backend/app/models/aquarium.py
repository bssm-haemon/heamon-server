"""아쿠아리움 & 구매 내역 모델"""
import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Float, DateTime, Integer, UniqueConstraint, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Aquarium(Base):
    __tablename__ = "aquarium"
    __table_args__ = (
        Index("idx_aquarium_user", "user_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creature_id = Column(String(50), nullable=False)  # 정적 도감 ID
    position_x = Column(Float, default=0)
    position_y = Column(Float, default=0)
    purchased_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User")


class PurchaseHistory(Base):
    __tablename__ = "purchase_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creature_id = Column(String(50), nullable=False)  # 정적 도감 ID
    points_spent = Column(Integer, nullable=False)
    purchased_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User")
