"""랭킹 스키마"""
from uuid import UUID
from pydantic import BaseModel


class RankingEntry(BaseModel):
    rank: int
    user_id: UUID
    nickname: str
    profile_image: str | None
    value: int  # 포인트, 도감 수, 수거 횟수 등


class RankingResponse(BaseModel):
    rankings: list[RankingEntry]
    my_rank: int | None = None
    total_users: int
