"""AI 이미지 분류 통합 서비스"""
from app.services.creature_ai import creature_classifier, CreatureClassifier
from app.services.trash_ai import trash_classifier, TrashClassifier
from app.services.image_hash import image_hash_service, ImageHashService


class AIClassifierService:
    """AI 분류 서비스 통합"""

    def __init__(self):
        self.creature_classifier = creature_classifier
        self.trash_classifier = trash_classifier
        self.image_hash_service = image_hash_service

    async def classify_creature(self, image_bytes: bytes) -> dict:
        """생물 분류"""
        return await self.creature_classifier.classify(image_bytes)

    async def classify_trash(self, image_bytes: bytes) -> dict:
        """쓰레기 분류"""
        return await self.trash_classifier.classify_trash(image_bytes)

    async def verify_cleanup(self, before_bytes: bytes, after_bytes: bytes) -> dict:
        """Before/After 검증"""
        return await self.trash_classifier.verify_cleanup(before_bytes, after_bytes)

    def compute_hash(self, image_bytes: bytes) -> str:
        """이미지 해시 계산"""
        return self.image_hash_service.compute_hash(image_bytes)


# 싱글톤 인스턴스
ai_classifier_service = AIClassifierService()
