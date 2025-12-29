"""포인트 계산 서비스"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.sighting import Sighting
from app.models.cleanup import Cleanup
from app.models.user_creature import UserCreature


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
    "streak_7_days": 200,       # 7일 연속 참여
    "same_location_10": 100,    # 같은 장소 10회 청소
}


class PointService:
    def calculate_sighting_points(
        self,
        db: Session,
        user_id: str,
        creature_id: str,
        rarity: str
    ) -> dict:
        """생물 목격 포인트 계산"""
        base_points = SIGHTING_POINTS.get(rarity, 30)
        bonus_points = 0
        bonus_reasons = []

        # 첫 발견 보너스 체크
        existing = db.query(UserCreature).filter(
            UserCreature.user_id == user_id,
            UserCreature.creature_id == creature_id
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
        """쓰레기 수거 포인트 계산"""
        base_points = CLEANUP_POINTS.get(amount, 30)
        bonus_points = 0
        bonus_reasons = []

        # 7일 연속 참여 체크
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_activity = db.query(
            func.date(Cleanup.created_at).label("date")
        ).filter(
            Cleanup.user_id == user_id,
            Cleanup.created_at >= seven_days_ago,
            Cleanup.status == "approved"
        ).group_by(func.date(Cleanup.created_at)).all()

        if len(daily_activity) >= 7:
            bonus_points += BONUS["streak_7_days"]
            bonus_reasons.append("streak_7_days")

        # 같은 장소 10회 청소 체크 (반경 100m 이내)
        # 간단한 구현: 정확히 같은 좌표만 체크
        same_location_count = db.query(Cleanup).filter(
            Cleanup.user_id == user_id,
            Cleanup.latitude == latitude,
            Cleanup.longitude == longitude,
            Cleanup.status == "approved"
        ).count()

        if same_location_count >= 9:  # 현재 것 포함 10회
            bonus_points += BONUS["same_location_10"]
            bonus_reasons.append("same_location_10")

        total_points = base_points + bonus_points

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

        creature_count = db.query(UserCreature).filter(
            UserCreature.user_id == user_id
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
