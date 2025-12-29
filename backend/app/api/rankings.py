"""랭킹"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.api.deps import get_db, get_current_user_optional
from app.models.user import User
from app.models.cleanup import Cleanup
from app.models.user_creature import UserCreature
from app.schemas.ranking import RankingEntry, RankingResponse


router = APIRouter()


@router.get("/collection", response_model=RankingResponse)
async def get_collection_ranking(
    limit: int = 100,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    도감 완성률 랭킹
    - 발견한 생물 수 기준
    """
    # 유저별 발견 수 집계
    subquery = db.query(
        UserCreature.user_id,
        func.count(UserCreature.creature_id).label("count")
    ).group_by(UserCreature.user_id).subquery()

    results = db.query(
        User.id,
        User.nickname,
        User.profile_image,
        subquery.c.count
    ).outerjoin(
        subquery, User.id == subquery.c.user_id
    ).order_by(
        desc(subquery.c.count)
    ).limit(limit).all()

    rankings = []
    my_rank = None

    for idx, row in enumerate(results, 1):
        rankings.append(RankingEntry(
            rank=idx,
            user_id=row.id,
            nickname=row.nickname,
            profile_image=row.profile_image,
            value=row.count or 0
        ))

        if current_user and row.id == current_user.id:
            my_rank = idx

    total_users = db.query(User).count()

    return RankingResponse(
        rankings=rankings,
        my_rank=my_rank,
        total_users=total_users
    )


@router.get("/cleanup", response_model=RankingResponse)
async def get_cleanup_ranking(
    limit: int = 100,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    수거왕 랭킹
    - 승인된 수거 횟수 기준
    """
    # 유저별 수거 횟수 집계
    subquery = db.query(
        Cleanup.user_id,
        func.count(Cleanup.id).label("count")
    ).filter(
        Cleanup.status == "approved"
    ).group_by(Cleanup.user_id).subquery()

    results = db.query(
        User.id,
        User.nickname,
        User.profile_image,
        subquery.c.count
    ).outerjoin(
        subquery, User.id == subquery.c.user_id
    ).order_by(
        desc(subquery.c.count)
    ).limit(limit).all()

    rankings = []
    my_rank = None

    for idx, row in enumerate(results, 1):
        rankings.append(RankingEntry(
            rank=idx,
            user_id=row.id,
            nickname=row.nickname,
            profile_image=row.profile_image,
            value=row.count or 0
        ))

        if current_user and row.id == current_user.id:
            my_rank = idx

    total_users = db.query(User).count()

    return RankingResponse(
        rankings=rankings,
        my_rank=my_rank,
        total_users=total_users
    )


@router.get("/points", response_model=RankingResponse)
async def get_points_ranking(
    limit: int = 100,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    포인트 랭킹
    """
    results = db.query(User).order_by(
        desc(User.points)
    ).limit(limit).all()

    rankings = []
    my_rank = None

    for idx, user in enumerate(results, 1):
        rankings.append(RankingEntry(
            rank=idx,
            user_id=user.id,
            nickname=user.nickname,
            profile_image=user.profile_image,
            value=user.points
        ))

        if current_user and user.id == current_user.id:
            my_rank = idx

    total_users = db.query(User).count()

    return RankingResponse(
        rankings=rankings,
        my_rank=my_rank,
        total_users=total_users
    )
