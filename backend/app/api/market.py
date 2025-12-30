"""마켓 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.market import MarketListResponse, PurchaseRequest, PurchaseResponse
from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["마켓"])


@router.get("", response_model=MarketListResponse)
async def get_market_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """마켓 목록 조회 (내 도감 보유 생물만 표시)"""
    service = MarketService(db)
    return service.get_market_items(current_user.id)


@router.post("/purchase", response_model=PurchaseResponse)
async def purchase_creatures(
    request: PurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    생물 구매 (다중 구매)
    - 도감에 있는 생물만 구매 가능
    - 이미 아쿠아리움에 있으면 불가
    - 포인트 부족 시 에러
    """
    service = MarketService(db)
    return service.purchase_creatures(current_user.id, request.creature_ids)
