"""생물 목격 CRUD"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user, get_admin_user
from app.models.user import User
from app.models.sighting import Sighting
from app.models.creature import Creature
from app.models.user_creature import UserCreature
from app.schemas.sighting import (
    SightingCreate, SightingResponse, SightingListResponse,
    SightingStatusUpdate, SightingDetailResponse
)
from app.services.storage import storage_service
from app.services.image_hash import image_hash_service
from app.services.point_service import point_service


router = APIRouter()


@router.post("", response_model=SightingResponse, status_code=status.HTTP_201_CREATED)
async def create_sighting(
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_name: Optional[str] = Form(None),
    memo: Optional[str] = Form(None),
    creature_id: Optional[UUID] = Form(None),
    ai_suggestion: Optional[str] = Form(None),
    ai_confidence: Optional[float] = Form(None),
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    목격 등록
    - 사진 업로드
    - AI 추천 결과 포함 가능
    - status: pending으로 생성
    """
    # 이미지 읽기
    image_bytes = await photo.read()

    # 이미지 해시 계산
    image_hash = image_hash_service.compute_hash(image_bytes)

    # Supabase Storage에 업로드
    photo_url = await storage_service.upload_image(image_bytes, folder="sightings")

    # 목격 기록 생성
    sighting = Sighting(
        user_id=current_user.id,
        creature_id=creature_id,
        photo_url=photo_url,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        memo=memo,
        image_hash=image_hash,
        ai_suggestion=ai_suggestion,
        ai_confidence=ai_confidence,
        status="pending"
    )

    db.add(sighting)
    db.commit()
    db.refresh(sighting)

    return sighting


@router.get("", response_model=SightingListResponse)
async def list_sightings(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    목격 목록 (피드)
    - 페이지네이션
    - 상태/유저 필터링
    """
    query = db.query(Sighting)

    if status:
        query = query.filter(Sighting.status == status)
    if user_id:
        query = query.filter(Sighting.user_id == user_id)

    total = query.count()

    sightings = query.order_by(desc(Sighting.created_at)).offset(
        (page - 1) * limit
    ).limit(limit).all()

    return SightingListResponse(
        sightings=sightings,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{sighting_id}", response_model=SightingDetailResponse)
async def get_sighting(
    sighting_id: UUID,
    db: Session = Depends(get_db)
):
    """목격 상세"""
    sighting = db.query(Sighting).filter(Sighting.id == sighting_id).first()
    if not sighting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목격 기록을 찾을 수 없습니다"
        )

    user = db.query(User).filter(User.id == sighting.user_id).first()
    creature = None
    if sighting.creature_id:
        creature = db.query(Creature).filter(Creature.id == sighting.creature_id).first()

    return SightingDetailResponse(
        id=sighting.id,
        user_id=sighting.user_id,
        creature_id=sighting.creature_id,
        photo_url=sighting.photo_url,
        latitude=sighting.latitude,
        longitude=sighting.longitude,
        location_name=sighting.location_name,
        memo=sighting.memo,
        image_hash=sighting.image_hash,
        ai_suggestion=sighting.ai_suggestion,
        ai_confidence=sighting.ai_confidence,
        status=sighting.status,
        points_earned=sighting.points_earned,
        created_at=sighting.created_at,
        user_nickname=user.nickname if user else None,
        creature_name=creature.name if creature else None
    )


@router.patch("/{sighting_id}/status", response_model=SightingResponse)
async def update_sighting_status(
    sighting_id: UUID,
    status_update: SightingStatusUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    승인/거절 (관리자)
    - 승인 시 포인트 지급
    - 첫 발견 시 도감에 추가
    """
    sighting = db.query(Sighting).filter(Sighting.id == sighting_id).first()
    if not sighting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목격 기록을 찾을 수 없습니다"
        )

    if sighting.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 처리된 목격 기록입니다"
        )

    sighting.status = status_update.status

    if status_update.status == "approved":
        # 생물 확정
        if status_update.creature_id:
            sighting.creature_id = status_update.creature_id

        if sighting.creature_id:
            creature = db.query(Creature).filter(
                Creature.id == sighting.creature_id
            ).first()

            if creature:
                # 포인트 계산
                points_result = point_service.calculate_sighting_points(
                    db, str(sighting.user_id), str(sighting.creature_id), creature.rarity
                )

                sighting.points_earned = points_result["total_points"]

                # 유저 포인트 추가
                point_service.add_points(db, str(sighting.user_id), points_result["total_points"])

                # 도감에 추가 (첫 발견인 경우)
                existing = db.query(UserCreature).filter(
                    UserCreature.user_id == sighting.user_id,
                    UserCreature.creature_id == sighting.creature_id
                ).first()

                if not existing:
                    user_creature = UserCreature(
                        user_id=sighting.user_id,
                        creature_id=sighting.creature_id,
                        first_sighting_id=sighting.id
                    )
                    db.add(user_creature)

    db.commit()
    db.refresh(sighting)

    return sighting
