"""포인트 계산 서비스"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.sighting import Sighting
from app.models.cleanup import Cleanup
from app.models.user_creature import UserCollection
from app.services.static_creatures import RARITY_BY_ID


SIGHTING_POINTS = {
    "common": 30,
    "rare": 80,
    "legendary": 150,
}

CLEANUP_POINTS = {
    "handful": 30,
    "one_bag": 50,
    "large": 100,
}

BONUS = {
    "first_discovery": 20,      # 도감에 없던 생물 첫 발견
}


class PointService:
    def calculate_sighting_points(
        self,
        db: Session,
        user_id: str,
        creature_id: str,
        rarity: str | None = None
    ) -> dict:
        """생물 목격 포인트 계산"""
        rarity = rarity or RARITY_BY_ID.get(creature_id, "common")
        base_points = SIGHTING_POINTS.get(rarity, 30)
        bonus_points = 0
        bonus_reasons = []

        # 첫 발견 보너스 체크
        existing = db.query(UserCollection).filter(
            UserCollection.user_id == user_id,
            UserCollection.creature_id == creature_id
        ).first()

        if not existing:
            bonus_points += BONUS["first_discovery"]
            bonus_reasons.append("first_discovery")

        total_points = base_points + bonus_points

        return {
            "base_points": base_points,
            "bonus_points": bonus_points,
            "bonus_reasons": bonus_reasons,
            "total_points": total_points
        }

    def calculate_cleanup_points(
        self,
        db: Session,
        user_id: str,
        amount: str,
        latitude: float,
        longitude: float
    ) -> dict:
        """쓰레기 수거 포인트 계산 (기본 포인트만)"""
        base_points = CLEANUP_POINTS.get(amount, 30)
        bonus_points = 0
        bonus_reasons = []

        total_points = base_points

        return {
            "base_points": base_points,
            "bonus_points": bonus_points,
            "bonus_reasons": bonus_reasons,
            "total_points": total_points
        }

    def add_points(self, db: Session, user_id: str, points: int) -> int:
        """유저에게 포인트 추가"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.points += points
            db.commit()
            return user.points
        return 0

    def get_user_stats(self, db: Session, user_id: str) -> dict:
        """유저 통계 조회"""
        sighting_count = db.query(Sighting).filter(
            Sighting.user_id == user_id,
            Sighting.status == "approved"
        ).count()

        cleanup_count = db.query(Cleanup).filter(
            Cleanup.user_id == user_id,
            Cleanup.status == "approved"
        ).count()

        creature_count = db.query(UserCollection).filter(
            UserCollection.user_id == user_id
        ).count()

        user = db.query(User).filter(User.id == user_id).first()

        return {
            "total_points": user.points if user else 0,
            "sighting_count": sighting_count,
            "cleanup_count": cleanup_count,
            "creature_count": creature_count
        }


# 싱글톤 인스턴스
point_service = PointService()
