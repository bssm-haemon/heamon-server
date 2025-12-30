"""AI 분류 엔드포인트"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.ai import (
    CreatureClassifyResponse,
    TrashClassifyResponse,
    CleanupVerifyResponse,
    DuplicateCheckResponse
)
from app.services.creature_ai import creature_classifier
from app.services.trash_ai import trash_classifier
from app.services.image_hash import image_hash_service


router = APIRouter()


@router.post("/classify/creature", response_model=CreatureClassifyResponse)
async def classify_creature(
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    생물 사진 → 종류 판별
    - AI가 생물 종류 추천
    - 신뢰도 반환
    """
    image_bytes = await photo.read()
    result = await creature_classifier.classify(image_bytes)

    return CreatureClassifyResponse(
        suggested_creature=result["suggested_creature"],
        category=result["category"],
        confidence=result["confidence"],
        rarity=result["rarity"],
        is_confident=result["is_confident"]
    )


@router.post("/classify/trash", response_model=TrashClassifyResponse)
async def classify_trash(
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    쓰레기 사진 → 종류 분류
    """
    image_bytes = await photo.read()
    result = await trash_classifier.classify_trash(image_bytes)

    return TrashClassifyResponse(
        trash_type=result["trash_type"],
        confidence=result["confidence"],
        has_trash=result["has_trash"]
    )


@router.post("/verify/cleanup", response_model=CleanupVerifyResponse)
async def verify_cleanup(
    before_photo: UploadFile = File(...),
    after_photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Before/After 변화 검증
    - 실제로 청소가 되었는지 확인
    """
    before_bytes = await before_photo.read()
    after_bytes = await after_photo.read()

    result = await trash_classifier.verify_cleanup(before_bytes, after_bytes)

    return CleanupVerifyResponse(
        is_valid=result["is_valid"],
        before_had_trash=result["before_had_trash"],
        after_has_trash=result["after_has_trash"],
        confidence=result["confidence"]
    )


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
async def check_duplicate(
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    이미지 중복 검사
    - 같은 사진 재업로드 방지
    - 도용 방지
    """
    image_bytes = await photo.read()
    result = await image_hash_service.check_duplicate(
        db, image_bytes, current_user.id
    )

    return DuplicateCheckResponse(
        is_duplicate=result["is_duplicate"],
        similar_image_id=result["similar_image_id"],
        hash=result["hash"],
        is_same_user=result.get("is_same_user"),
        distance=result.get("distance"),
    )
