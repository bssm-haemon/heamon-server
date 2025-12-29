"""생물 도감은 프론트 정적 데이터로 관리"""
from fastapi import APIRouter, HTTPException, status
from app.services.static_creatures import STATIC_CREATURES, TOTAL_CREATURES, TOTAL_BY_RARITY


router = APIRouter()


@router.get("")
async def list_creatures():
    """
    생물 도감은 프론트엔드에 정적으로 포함되어 있습니다.
    """
    return {
        "message": "생물 데이터는 프론트엔드에 정적으로 포함되어 있습니다.",
        "total_creatures": TOTAL_CREATURES,
        "total": TOTAL_CREATURES,  # 하위 호환
        "by_rarity": TOTAL_BY_RARITY,
        "creatures": STATIC_CREATURES,
    }


@router.get("/{creature_id}")
async def get_creature(creature_id: str):
    """정적 데이터 상세 조회"""
    creature = next((c for c in STATIC_CREATURES if c["id"] == creature_id), None)
    if not creature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="생물을 찾을 수 없습니다"
        )
    return creature


@router.post("")
async def create_creature():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="생물 데이터는 정적으로 관리됩니다"
    )


@router.put("/{creature_id}")
async def update_creature(creature_id: str):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="생물 데이터는 정적으로 관리됩니다"
    )


@router.delete("/{creature_id}")
async def delete_creature(creature_id: str):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="생물 데이터는 정적으로 관리됩니다"
    )
