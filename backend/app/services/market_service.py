"""마켓 비즈니스 로직"""
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_creature import UserCollection
from app.models.aquarium import Aquarium, PurchaseHistory
from app.services.static_creatures import RARITY_BY_ID, NAME_BY_ID, CATEGORY_BY_ID

# 희귀도별 구매 가격
CREATURE_PRICES = {
    "common": 50,
    "rare": 150,
    "legendary": 300,
}


class MarketService:
    def __init__(self, db: Session):
        self.db = db

    def get_market_items(self, user_id) -> dict:
        """
        마켓 목록 조회
        - 도감에 있는 생물만 노출
        - 아쿠아리움 보유 여부 표시
        """
        user_creatures = self.db.query(UserCollection).filter(
            UserCollection.user_id == user_id
        ).all()
        creature_ids = [uc.creature_id for uc in user_creatures]

        aquarium_ids = {
            row.creature_id
            for row in self.db.query(Aquarium.creature_id).filter(
                Aquarium.user_id == user_id
            )
        }

        user = self.db.query(User).filter(User.id == user_id).first()

        items = []
        for cid in creature_ids:
            rarity = RARITY_BY_ID.get(cid, "common")
            price = CREATURE_PRICES.get(rarity, 100)
            items.append({
                "creature_id": cid,
                "name": NAME_BY_ID.get(cid),
                "name_en": None,
                "category": CATEGORY_BY_ID.get(cid, ""),
                "image_url": None,
                "rarity": rarity,
                "price": price,
                "in_aquarium": cid in aquarium_ids,
            })

        return {
            "items": items,
            "total": len(items),
            "user_points": user.points if user else 0,
        }

    def purchase_creatures(self, user_id, creature_ids: List[str]) -> dict:
        """
        생물 구매 (다중 구매)
        - 도감에 있는 생물만
        - 이미 아쿠아리움에 있으면 불가
        - 포인트 부족 시 불가
        """
        user = (
            self.db.query(User)
            .filter(User.id == user_id)
            .with_for_update()
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다",
            )

        # 도감 보유 확인
        owned_ids = {
            row.creature_id
            for row in self.db.query(UserCollection.creature_id).filter(
                UserCollection.user_id == user_id
            )
        }

        purchasable = []
        total_price = 0

        for cid in creature_ids:
            if cid not in owned_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"도감에 없는 생물입니다: {cid}",
                )

            rarity = RARITY_BY_ID.get(cid, "common")
            price = CREATURE_PRICES.get(rarity, 100)
            purchasable.append((cid, price))
            total_price += price

        if not purchasable:
            return {
                "success": False,
                "purchased": [],
                "total_spent": 0,
                "remaining_points": user.points,
                "message": "구매할 생물이 없습니다.",
            }

        if user.points < total_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"포인트가 부족합니다. 필요: {total_price}, 보유: {user.points}",
            )

        try:
            user.points -= total_price
            purchased_ids: List[UUID] = []

            for cid, price in purchasable:
                self.db.add(
                    Aquarium(
                        user_id=user_id,
                        creature_id=cid,
                    )
                )
                self.db.add(
                    PurchaseHistory(
                        user_id=user_id,
                        creature_id=cid,
                        points_spent=price,
                    )
                )
                purchased_ids.append(cid)

            self.db.commit()

            return {
                "success": True,
                "purchased": purchased_ids,
                "total_spent": total_price,
                "remaining_points": user.points,
                "message": f"{len(purchased_ids)}마리 생물을 아쿠아리움에 추가했습니다!",
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"구매 처리 중 오류: {str(e)}",
            )
