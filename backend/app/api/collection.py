"""유저 도감 (발견 목록)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.user_creature import UserCollection
from app.schemas.creature import CollectionStatsResponse
from app.services.static_creatures import TOTAL_CREATURES, TOTAL_BY_RARITY, RARITY_BY_ID


router = APIRouter()


@router.get("")
async def get_my_collection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 도감 (발견 목록)
    """
    user_collections = db.query(UserCollection).filter(
        UserCollection.user_id == current_user.id
    ).all()

    result = [
        {
            "creature_id": uc.creature_id,
            "discovered_at": uc.discovered_at,
            "first_sighting_id": uc.first_sighting_id
        }
        for uc in user_collections
    ]

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
    discovered = db.query(UserCollection).filter(
        UserCollection.user_id == current_user.id
    ).all()

    discovered_ids = {uc.creature_id for uc in discovered}

    by_rarity: dict[str, dict[str, int]] = {}
    for rarity in ["common", "rare", "legendary"]:
        total = TOTAL_BY_RARITY.get(rarity, 0)
        discovered_count = len(
            [cid for cid in discovered_ids if RARITY_BY_ID.get(cid) == rarity]
        )
        by_rarity[rarity] = {
            "total": total,
            "discovered": discovered_count
        }

    discovered_count = len(discovered_ids)
    completion_rate = (discovered_count / TOTAL_CREATURES * 100) if TOTAL_CREATURES else 0

    return CollectionStatsResponse(
        total_creatures=TOTAL_CREATURES,
        discovered_count=discovered_count,
        completion_rate=round(completion_rate, 2),
        by_rarity=by_rarity
    )
