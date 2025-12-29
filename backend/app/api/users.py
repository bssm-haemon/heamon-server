"""유저 프로필, 포인트"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.sighting import Sighting
from app.models.cleanup import Cleanup
from app.models.user_creature import UserCollection
from app.models.badge import UserBadge
from app.schemas.user import UserResponse, UserUpdate, UserProfile


router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """내 프로필 상세 조회"""
    sighting_count = db.query(Sighting).filter(
        Sighting.user_id == current_user.id,
        Sighting.status == "approved"
    ).count()

    cleanup_count = db.query(Cleanup).filter(
        Cleanup.user_id == current_user.id,
        Cleanup.status == "approved"
    ).count()

    creature_count = db.query(UserCollection).filter(
        UserCollection.user_id == current_user.id
    ).count()

    badge_count = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id
    ).count()

    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        nickname=current_user.nickname,
        profile_image=current_user.profile_image,
        points=current_user.points,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        sighting_count=sighting_count,
        cleanup_count=cleanup_count,
        creature_count=creature_count,
        badge_count=badge_count
    )


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """내 프로필 수정"""
    if update_data.nickname is not None:
        current_user.nickname = update_data.nickname
    if update_data.profile_image is not None:
        current_user.profile_image = update_data.profile_image

    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """유저 프로필 조회 (공개)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유저를 찾을 수 없습니다"
        )

    sighting_count = db.query(Sighting).filter(
        Sighting.user_id == user.id,
        Sighting.status == "approved"
    ).count()

    cleanup_count = db.query(Cleanup).filter(
        Cleanup.user_id == user.id,
        Cleanup.status == "approved"
    ).count()

    creature_count = db.query(UserCollection).filter(
        UserCollection.user_id == user.id
    ).count()

    badge_count = db.query(UserBadge).filter(
        UserBadge.user_id == user.id
    ).count()

    return UserProfile(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        profile_image=user.profile_image,
        points=user.points,
        is_admin=user.is_admin,
        created_at=user.created_at,
        sighting_count=sighting_count,
        cleanup_count=cleanup_count,
        creature_count=creature_count,
        badge_count=badge_count
    )
