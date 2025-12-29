"""유저 도감 (발견 목록)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.creature import Creature
from app.models.user_creature import UserCreature
from app.schemas.creature import UserCreatureResponse, CollectionStatsResponse


router = APIRouter()


@router.get("")
async def get_my_collection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 도감 (발견 목록)
    """
    user_creatures = db.query(UserCreature).filter(
        UserCreature.user_id == current_user.id
    ).all()

    result = []
    for uc in user_creatures:
        creature = db.query(Creature).filter(Creature.id == uc.creature_id).first()
        if creature:
            result.append({
                "creature": creature,
                "discovered_at": uc.discovered_at,
                "first_sighting_id": uc.first_sighting_id
            })

    return {"collection": result, "total": len(result)}


@router.get("/stats", response_model=CollectionStatsResponse)
async def get_collection_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    도감 완성률
    - 전체 생물 수
    - 발견한 생물 수
    - 희귀도별 통계
    """
    # 전체 생물 수
    total_creatures = db.query(Creature).count()

    # 발견한 생물 수
    discovered_count = db.query(UserCreature).filter(
        UserCreature.user_id == current_user.id
    ).count()

    # 완성률
    completion_rate = (discovered_count / total_creatures * 100) if total_creatures > 0 else 0

    # 희귀도별 통계
    by_rarity = {}

    for rarity in ["common", "rare", "legendary"]:
        total = db.query(Creature).filter(Creature.rarity == rarity).count()

        discovered = db.query(UserCreature).join(
            Creature, UserCreature.creature_id == Creature.id
        ).filter(
            UserCreature.user_id == current_user.id,
            Creature.rarity == rarity
        ).count()

        by_rarity[rarity] = {
            "total": total,
            "discovered": discovered
        }

    return CollectionStatsResponse(
        total_creatures=total_creatures,
        discovered_count=discovered_count,
        completion_rate=round(completion_rate, 2),
        by_rarity=by_rarity
    )
