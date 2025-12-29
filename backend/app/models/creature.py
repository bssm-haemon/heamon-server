"""생물 도감 마스터 모델"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Creature(Base):
    __tablename__ = "creatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    name_en = Column(String(50), nullable=True)
    category = Column(String(30), nullable=False)  # cetacean, turtle, fish...
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    rarity = Column(String(20), nullable=False)  # common, rare, legendary
    points = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 현재 정적 데이터로 전환되어 관계는 사용하지 않음
