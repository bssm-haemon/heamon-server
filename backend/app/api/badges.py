"""업적/뱃지"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_admin_user
from app.models.user import User
from app.models.badge import Badge, UserBadge
from app.schemas.badge import BadgeCreate, BadgeResponse, UserBadgeResponse, BadgeListResponse
from app.services.static_badges import STATIC_BADGES


router = APIRouter()


@router.get("", response_model=BadgeListResponse)
async def list_badges(db: Session = Depends(get_db)):
    """전체 뱃지 목록"""
    from app.services.badge_awarder import _seed_static_badges

    _seed_static_badges(db)
    badges = db.query(Badge).order_by(Badge.name).all()
    return BadgeListResponse(
        badges=badges,
        total=len(badges)
    )


@router.get("/my")
async def get_my_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """내 뱃지"""
    user_badges = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id
    ).all()

    result = []
    for ub in user_badges:
        badge = db.query(Badge).filter(Badge.id == ub.badge_id).first()
        if badge:
            result.append({
                "badge": badge,
                "earned_at": ub.earned_at
            })

    return {"badges": result, "total": len(result)}


@router.post("", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
async def create_badge(
    badge_data: BadgeCreate,
    db: Session = Depends(get_db)
):
    """정적 뱃지로 관리 → 생성 비활성화"""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="뱃지는 정적으로 관리됩니다"
    )


@router.post("/{badge_id}/award/{user_id}")
async def award_badge(
    badge_id: UUID,
    user_id: UUID,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """뱃지 수여 (관리자)"""
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="뱃지를 찾을 수 없습니다"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유저를 찾을 수 없습니다"
        )

    # 이미 보유 중인지 확인
    existing = db.query(UserBadge).filter(
        UserBadge.user_id == user_id,
        UserBadge.badge_id == badge_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 보유한 뱃지입니다"
        )

    user_badge = UserBadge(
        user_id=user_id,
        badge_id=badge_id
    )

    db.add(user_badge)
    db.commit()

    return {"message": "뱃지가 수여되었습니다"}
