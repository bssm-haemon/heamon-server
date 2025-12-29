"""생물 도감 마스터"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_admin_user
from app.models.user import User
from app.models.creature import Creature
from app.schemas.creature import CreatureCreate, CreatureResponse, CreatureListResponse


router = APIRouter()


@router.get("", response_model=CreatureListResponse)
async def list_creatures(
    category: Optional[str] = None,
    rarity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    전체 생물 도감
    - 카테고리/희귀도 필터링
    """
    query = db.query(Creature)

    if category:
        query = query.filter(Creature.category == category)
    if rarity:
        query = query.filter(Creature.rarity == rarity)

    creatures = query.order_by(Creature.name).all()
    total = len(creatures)

    return CreatureListResponse(
        creatures=creatures,
        total=total
    )


@router.get("/{creature_id}", response_model=CreatureResponse)
async def get_creature(
    creature_id: UUID,
    db: Session = Depends(get_db)
):
    """생물 상세"""
    creature = db.query(Creature).filter(Creature.id == creature_id).first()
    if not creature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="생물을 찾을 수 없습니다"
        )

    return creature


@router.post("", response_model=CreatureResponse, status_code=status.HTTP_201_CREATED)
async def create_creature(
    creature_data: CreatureCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """생물 등록 (관리자)"""
    creature = Creature(
        name=creature_data.name,
        name_en=creature_data.name_en,
        category=creature_data.category,
        description=creature_data.description,
        image_url=creature_data.image_url,
        rarity=creature_data.rarity,
        points=creature_data.points
    )

    db.add(creature)
    db.commit()
    db.refresh(creature)

    return creature


@router.put("/{creature_id}", response_model=CreatureResponse)
async def update_creature(
    creature_id: UUID,
    creature_data: CreatureCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """생물 수정 (관리자)"""
    creature = db.query(Creature).filter(Creature.id == creature_id).first()
    if not creature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="생물을 찾을 수 없습니다"
        )

    creature.name = creature_data.name
    creature.name_en = creature_data.name_en
    creature.category = creature_data.category
    creature.description = creature_data.description
    creature.image_url = creature_data.image_url
    creature.rarity = creature_data.rarity
    creature.points = creature_data.points

    db.commit()
    db.refresh(creature)

    return creature


@router.delete("/{creature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_creature(
    creature_id: UUID,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """생물 삭제 (관리자)"""
    creature = db.query(Creature).filter(Creature.id == creature_id).first()
    if not creature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="생물을 찾을 수 없습니다"
        )

    db.delete(creature)
    db.commit()
