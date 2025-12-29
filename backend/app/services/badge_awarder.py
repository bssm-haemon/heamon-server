"""정적 뱃지 지급 로직"""
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.badge import UserBadge, Badge
from app.models.user_creature import UserCollection
from app.services.static_badges import STATIC_BADGES


def _seed_static_badges(db: Session) -> None:
    """DB에 정적 뱃지가 없으면 삽입 (업데이트는 하지 않음)"""
    existing_ids = {
        str(bid)
        for (bid,) in db.query(Badge.id).all()
    }

    to_create = [b for b in STATIC_BADGES if str(b["id"]) not in existing_ids]
    if not to_create:
        return

    for badge in to_create:
        new_badge = Badge(
            id=badge["id"],
            name=badge["name"],
            description=badge["description"],
            condition_type=badge["condition_type"],
            condition_value=badge["condition_value"],
        )
        if hasattr(new_badge, "name_ko"):
            new_badge.name_ko = badge["name"]
        if hasattr(new_badge, "created_at"):
            new_badge.created_at = datetime.utcnow()

        db.add(new_badge)

    db.commit()


def award_collection_badges(db: Session, user_id: UUID) -> list[UserBadge]:
    """도감 수집 개수에 따른 뱃지 지급"""
    _seed_static_badges(db)

    earned = []
    collection_count = db.query(UserCollection).filter(UserCollection.user_id == user_id).count()

    # 이미 획득한 뱃지
    existing = {
        str(ub.badge_id)
        for ub in db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    }

    for badge in STATIC_BADGES:
        if badge["condition_type"] != "collection_count":
            continue
        if collection_count < badge["condition_value"]:
            continue
        if str(badge["id"]) in existing:
            continue

        user_badge = UserBadge(user_id=user_id, badge_id=badge["id"])
        db.add(user_badge)
        earned.append(user_badge)

    if earned:
        db.commit()

    return earned
