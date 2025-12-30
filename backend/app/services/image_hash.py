"""
이미지 중복/악용 방지
- Perceptual Hash로 유사 이미지 탐지
- 인터넷 다운로드 이미지 필터링
"""
import io
import imagehash
from PIL import Image, UnidentifiedImageError
from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.sighting import Sighting
from app.models.cleanup import Cleanup


class ImageHashService:
    SIMILARITY_THRESHOLD = 5  # hamming distance < 5 → 유사 이미지

    def compute_hash(self, image_bytes: bytes) -> str:
        """이미지 해시 계산"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except UnidentifiedImageError:
            # HEIC 등 지원되지 않는 포맷을 위해 pillow-heif가 있으면 시도
            try:
                from pillow_heif import register_heif_opener

                register_heif_opener()
                image = Image.open(io.BytesIO(image_bytes))
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="유효하지 않은 이미지 파일입니다. JPEG/PNG 또는 HEIC 지원 패키지(pillow-heif)가 필요합니다."
                )
        return str(imagehash.phash(image))

    def _hamming_distance(self, hash1: str, hash2: str) -> int:
        """두 해시 간의 해밍 거리 계산"""
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            return h1 - h2
        except Exception:
            return 100  # 비교 불가 시 큰 값 반환

    async def check_duplicate(
        self,
        db: Session,
        image_bytes: bytes,
        user_id: UUID
    ) -> dict:
        """
        중복 검사
        - 같은 유저가 같은 사진 재업로드
        - 다른 유저의 사진 도용
        """
        new_hash = self.compute_hash(image_bytes)

        # DB에서 모든 이미지 해시 조회
        sighting_hashes = db.query(Sighting.id, Sighting.image_hash, Sighting.user_id).filter(
            Sighting.image_hash.isnot(None)
        ).all()

        cleanup_before_hashes = db.query(Cleanup.id, Cleanup.before_image_hash, Cleanup.user_id).filter(
            Cleanup.before_image_hash.isnot(None)
        ).all()

        cleanup_after_hashes = db.query(Cleanup.id, Cleanup.after_image_hash, Cleanup.user_id).filter(
            Cleanup.after_image_hash.isnot(None)
        ).all()

        # 유사 이미지 검색
        for sighting_id, existing_hash, existing_user_id in sighting_hashes:
            if existing_hash:
                distance = self._hamming_distance(new_hash, existing_hash)
                if distance < self.SIMILARITY_THRESHOLD:
                    return {
                        "is_duplicate": True,
                        "similar_image_id": str(sighting_id),
                        "hash": new_hash,
                        "is_same_user": str(existing_user_id) == str(user_id),
                        "distance": distance,
                    }

        for cleanup_id, existing_hash, existing_user_id in cleanup_before_hashes + cleanup_after_hashes:
            if existing_hash:
                distance = self._hamming_distance(new_hash, existing_hash)
                if distance < self.SIMILARITY_THRESHOLD:
                    return {
                        "is_duplicate": True,
                        "similar_image_id": str(cleanup_id),
                        "hash": new_hash,
                        "is_same_user": str(existing_user_id) == str(user_id),
                        "distance": distance,
                    }

        return {
            "is_duplicate": False,
            "similar_image_id": None,
            "hash": new_hash,
            "is_same_user": False,
            "distance": None,
        }

    def check_similarity_between_hashes(self, hash1: str, hash2: str) -> dict:
        """두 해시 간 유사도 검사 (Before/After 등)."""
        distance = self._hamming_distance(hash1, hash2)
        return {
            "distance": distance,
            "is_similar": distance < self.SIMILARITY_THRESHOLD
        }


# 싱글톤 인스턴스
image_hash_service = ImageHashService()
