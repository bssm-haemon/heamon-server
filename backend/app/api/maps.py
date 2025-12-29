"""지도 데이터 (히트맵)"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.sighting import Sighting
from app.models.cleanup import Cleanup
from app.models.creature import Creature
from app.schemas.map import SightingMarker, CleanupMarker, HeatmapPoint, MapDataResponse, HeatmapResponse


router = APIRouter()


@router.get("/sightings", response_model=MapDataResponse)
async def get_sighting_markers(
    status: Optional[str] = "approved",
    category: Optional[str] = None,
    rarity: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """
    목격 위치 데이터
    - 지도에 마커 표시용
    """
    query = db.query(Sighting)

    if status:
        query = query.filter(Sighting.status == status)

    sightings = query.limit(limit).all()

    markers = []
    for s in sightings:
        creature = None
        if s.creature_id:
            creature = db.query(Creature).filter(Creature.id == s.creature_id).first()

        # 필터링
        if category and creature and creature.category != category:
            continue
        if rarity and creature and creature.rarity != rarity:
            continue

        markers.append(SightingMarker(
            id=s.id,
            latitude=s.latitude,
            longitude=s.longitude,
            type="sighting",
            created_at=s.created_at,
            creature_name=creature.name if creature else s.ai_suggestion,
            rarity=creature.rarity if creature else None,
            photo_url=s.photo_url
        ))

    return MapDataResponse(
        markers=markers,
        total=len(markers)
    )


@router.get("/cleanups", response_model=MapDataResponse)
async def get_cleanup_markers(
    status: Optional[str] = "approved",
    trash_type: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """
    수거 위치 데이터
    - 지도에 마커 표시용
    """
    query = db.query(Cleanup)

    if status:
        query = query.filter(Cleanup.status == status)
    if trash_type:
        query = query.filter(Cleanup.trash_type == trash_type)

    cleanups = query.limit(limit).all()

    markers = []
    for c in cleanups:
        markers.append(CleanupMarker(
            id=c.id,
            latitude=c.latitude,
            longitude=c.longitude,
            type="cleanup",
            created_at=c.created_at,
            trash_type=c.trash_type,
            amount=c.amount
        ))

    return MapDataResponse(
        markers=markers,
        total=len(markers)
    )


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    type: str = "combined",  # sighting, cleanup, combined
    db: Session = Depends(get_db)
):
    """
    히트맵 데이터
    - 목격/수거/통합 선택
    """
    points = []

    if type in ["sighting", "combined"]:
        sightings = db.query(Sighting).filter(Sighting.status == "approved").all()
        for s in sightings:
            # 희귀도에 따라 가중치 부여
            weight = 1.0
            if s.creature_id:
                creature = db.query(Creature).filter(Creature.id == s.creature_id).first()
                if creature:
                    weight = {"common": 1.0, "rare": 2.0, "legendary": 3.0}.get(creature.rarity, 1.0)

            points.append(HeatmapPoint(
                latitude=s.latitude,
                longitude=s.longitude,
                weight=weight
            ))

    if type in ["cleanup", "combined"]:
        cleanups = db.query(Cleanup).filter(Cleanup.status == "approved").all()
        for c in cleanups:
            # 수거량에 따라 가중치 부여
            weight = {"handful": 1.0, "one_bag": 2.0, "large": 3.0}.get(c.amount, 1.0)
            points.append(HeatmapPoint(
                latitude=c.latitude,
                longitude=c.longitude,
                weight=weight
            ))

    return HeatmapResponse(
        points=points,
        type=type
    )
