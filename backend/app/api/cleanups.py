"""쓰레기 수거 CRUD"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user, get_admin_user
from app.models.user import User
from app.models.cleanup import Cleanup
from app.schemas.cleanup import CleanupCreate, CleanupResponse, CleanupListResponse, CleanupDetailResponse
from app.services.storage import storage_service
from app.services.image_hash import image_hash_service
from app.services.point_service import point_service


router = APIRouter()


@router.post("", response_model=CleanupResponse, status_code=status.HTTP_201_CREATED)
async def create_cleanup(
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_name: Optional[str] = Form(None),
    trash_type: str = Form(...),
    amount: str = Form(...),
    ai_verified: bool = Form(False),
    ai_confidence: Optional[float] = Form(None),
    before_photo: UploadFile = File(...),
    after_photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수거 인증 등록
    - Before/After 사진 업로드
    - AI 검증 결과 포함 가능
    """
    # 이미지 읽기
    before_bytes = await before_photo.read()
    after_bytes = await after_photo.read()

    # 이미지 해시 계산 (실패해도 업로드는 진행)
    try:
        before_hash = image_hash_service.compute_hash(before_bytes)
        after_hash = image_hash_service.compute_hash(after_bytes)
    except Exception:
        before_hash = None
        after_hash = None

    # Supabase Storage에 업로드
    before_url = await storage_service.upload_image(before_bytes, folder="cleanups/before")
    after_url = await storage_service.upload_image(after_bytes, folder="cleanups/after")

    # 수거 기록 생성
    cleanup = Cleanup(
        user_id=current_user.id,
        before_photo_url=before_url,
        after_photo_url=after_url,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        trash_type=trash_type,
        amount=amount,
        before_image_hash=before_hash,
        after_image_hash=after_hash,
        ai_verified=ai_verified,
        ai_confidence=ai_confidence,
        status="pending"
    )

    db.add(cleanup)
    db.commit()
    db.refresh(cleanup)

    return cleanup


@router.get("", response_model=CleanupListResponse)
async def list_cleanups(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    user_id: Optional[UUID] = None,
    trash_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    수거 목록
    - 페이지네이션
    - 상태/유저/쓰레기 종류 필터링
    """
    query = db.query(Cleanup)

    if status:
        query = query.filter(Cleanup.status == status)
    if user_id:
        query = query.filter(Cleanup.user_id == user_id)
    if trash_type:
        query = query.filter(Cleanup.trash_type == trash_type)

    total = query.count()

    cleanups = query.order_by(desc(Cleanup.created_at)).offset(
        (page - 1) * limit
    ).limit(limit).all()

    return CleanupListResponse(
        cleanups=cleanups,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{cleanup_id}", response_model=CleanupDetailResponse)
async def get_cleanup(
    cleanup_id: UUID,
    db: Session = Depends(get_db)
):
    """수거 상세"""
    cleanup = db.query(Cleanup).filter(Cleanup.id == cleanup_id).first()
    if not cleanup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="수거 기록을 찾을 수 없습니다"
        )

    user = db.query(User).filter(User.id == cleanup.user_id).first()

    return CleanupDetailResponse(
        id=cleanup.id,
        user_id=cleanup.user_id,
        before_photo_url=cleanup.before_photo_url,
        after_photo_url=cleanup.after_photo_url,
        latitude=cleanup.latitude,
        longitude=cleanup.longitude,
        location_name=cleanup.location_name,
        trash_type=cleanup.trash_type,
        amount=cleanup.amount,
        before_image_hash=cleanup.before_image_hash,
        after_image_hash=cleanup.after_image_hash,
        ai_verified=cleanup.ai_verified,
        ai_confidence=cleanup.ai_confidence,
        status=cleanup.status,
        points_earned=cleanup.points_earned,
        created_at=cleanup.created_at,
        user_nickname=user.nickname if user else None
    )


@router.patch("/{cleanup_id}/approve", response_model=CleanupResponse)
async def approve_cleanup(
    cleanup_id: UUID,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    수거 승인 (관리자)
    - 포인트 지급
    """
    cleanup = db.query(Cleanup).filter(Cleanup.id == cleanup_id).first()
    if not cleanup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="수거 기록을 찾을 수 없습니다"
        )

    if cleanup.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 처리된 수거 기록입니다"
        )

    cleanup.status = "approved"

    # 포인트 계산
    points_result = point_service.calculate_cleanup_points(
        db, str(cleanup.user_id), cleanup.amount,
        cleanup.latitude, cleanup.longitude
    )

    cleanup.points_earned = points_result["total_points"]

    # 유저 포인트 추가
    point_service.add_points(db, str(cleanup.user_id), points_result["total_points"])

    db.commit()
    db.refresh(cleanup)

    return cleanup


@router.patch("/{cleanup_id}/reject", response_model=CleanupResponse)
async def reject_cleanup(
    cleanup_id: UUID,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """수거 거절 (관리자)"""
    cleanup = db.query(Cleanup).filter(Cleanup.id == cleanup_id).first()
    if not cleanup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="수거 기록을 찾을 수 없습니다"
        )

    if cleanup.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 처리된 수거 기록입니다"
        )

    cleanup.status = "rejected"
    db.commit()
    db.refresh(cleanup)

    return cleanup
