"""아쿠아리움 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.aquarium import Aquarium
from app.schemas.aquarium import AquariumListResponse, AquariumItem
from app.services.static_creatures import NAME_BY_ID, CATEGORY_BY_ID, RARITY_BY_ID

router = APIRouter(prefix="/aquarium", tags=["아쿠아리움"])


@router.get("", response_model=AquariumListResponse)
async def get_my_aquarium(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """내 아쿠아리움 목록"""
    items = db.query(Aquarium).filter(Aquarium.user_id == current_user.id).all()

    result = []
    for item in items:
        result.append(
            AquariumItem(
                id=item.id,
                creature_id=item.creature_id,
                creature_name=NAME_BY_ID.get(item.creature_id),
                creature_image=None,
                rarity=RARITY_BY_ID.get(item.creature_id),
                position_x=item.position_x,
                position_y=item.position_y,
                purchased_at=item.purchased_at,
            )
        )

    return AquariumListResponse(aquarium=result, total=len(result))


@router.delete("/{creature_id}")
async def remove_from_aquarium(
    creature_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """아쿠아리움에서 제거 (포인트 환불 없음)"""
    item = (
        db.query(Aquarium)
        .filter(Aquarium.user_id == current_user.id, Aquarium.creature_id == creature_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="아쿠아리움에서 찾을 수 없습니다",
        )

    db.delete(item)
    db.commit()
    return {"message": "아쿠아리움에서 제거되었습니다"}
