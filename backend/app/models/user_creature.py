"""유저 도감 (발견한 생물) 모델 - 정적 ID만 저장"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class UserCollection(Base):
    __tablename__ = "user_collections"
    __table_args__ = (
        UniqueConstraint("user_id", "creature_id", name="uq_user_collection"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creature_id = Column(String(50), nullable=False)  # 정적 도감 ID (ex: creature-001)
    first_sighting_id = Column(UUID(as_uuid=True), ForeignKey("sightings.id"), nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_collections")
