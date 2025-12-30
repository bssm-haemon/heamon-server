"""API 라우터"""
from fastapi import APIRouter
from app.api import auth, users, sightings, cleanups, creatures, collection, badges, rankings, maps, ai, market, aquarium

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(users.router, prefix="/users", tags=["사용자"])
api_router.include_router(sightings.router, prefix="/sightings", tags=["생물 목격"])
api_router.include_router(cleanups.router, prefix="/cleanups", tags=["쓰레기 수거"])
api_router.include_router(creatures.router, prefix="/creatures", tags=["생물 도감"])
api_router.include_router(collection.router, prefix="/collection", tags=["내 도감"])
api_router.include_router(badges.router, prefix="/badges", tags=["뱃지"])
api_router.include_router(rankings.router, prefix="/rankings", tags=["랭킹"])
api_router.include_router(maps.router, prefix="/maps", tags=["지도"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI 분류"])
api_router.include_router(market.router)
api_router.include_router(aquarium.router)
