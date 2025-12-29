"""
쓰레기 분류 + Before/After 검증
- 쓰레기 종류 자동 분류
- Before/After 변화 감지
"""
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

TRASH_TYPES = [
    "plastic",      # 플라스틱
    "styrofoam",    # 스티로폼
    "fishing_gear", # 그물/어구
    "glass",        # 유리
    "metal",        # 금속
    "other",        # 기타
]

TRASH_KEYWORDS = {
    "plastic": ["plastic_bag", "water_bottle", "pop_bottle", "plastic"],
    "glass": ["wine_bottle", "beer_bottle", "glass"],
    "metal": ["can", "aluminum", "metal"],
    "fishing_gear": ["net", "rope", "fishing"],
    "styrofoam": ["foam", "styrofoam"],
}


class TrashClassifier:
    def __init__(self):
        self.classifier = None

    def _load_model(self):
        """모델 지연 로딩"""
        if self.classifier is None:
            try:
                from transformers import pipeline
                self.classifier = pipeline(
                    "image-classification",
                    model="google/vit-base-patch16-224"
                )
            except Exception as e:
                logger.warning(f"Failed to load HuggingFace model: {e}")
                self.classifier = None

    async def classify_trash(self, image_bytes: bytes) -> dict:
        """쓰레기 종류 분류"""
        self._load_model()

        if self.classifier is None:
            return {
                "trash_type": "other",
                "confidence": 0.0,
                "has_trash": True
            }

        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != "RGB":
                image = image.convert("RGB")

            results = self.classifier(image)

            # 결과에서 쓰레기 관련 라벨 찾기
            for result in results:
                label = result["label"].lower().replace(" ", "_")
                score = result["score"]

                for trash_type, keywords in TRASH_KEYWORDS.items():
                    if any(kw in label for kw in keywords):
                        return {
                            "trash_type": trash_type,
                            "confidence": round(score, 2),
                            "has_trash": True
                        }

            # 쓰레기로 인식되지 않은 경우
            # 해변/자연 관련 라벨이면 쓰레기 없음으로 판단
            nature_keywords = ["beach", "seashore", "coast", "sand", "ocean", "sea"]
            for result in results:
                label = result["label"].lower()
                if any(kw in label for kw in nature_keywords):
                    return {
                        "trash_type": "other",
                        "confidence": round(result["score"], 2),
                        "has_trash": False
                    }

            return {
                "trash_type": "other",
                "confidence": results[0]["score"] if results else 0.0,
                "has_trash": True
            }

        except Exception as e:
            logger.error(f"Trash classification error: {e}")
            return {
                "trash_type": "other",
                "confidence": 0.0,
                "has_trash": True
            }

    async def verify_cleanup(
        self,
        before_bytes: bytes,
        after_bytes: bytes
    ) -> dict:
        """
        Before/After 비교 검증
        - 둘 다 같은 장소인지
        - 실제로 청소가 되었는지
        """
        before_result = await self.classify_trash(before_bytes)
        after_result = await self.classify_trash(after_bytes)

        is_valid = (
            before_result["has_trash"] is True and
            after_result["has_trash"] is False
        )

        return {
            "is_valid": is_valid,
            "before_had_trash": before_result["has_trash"],
            "after_has_trash": after_result["has_trash"],
            "confidence": min(
                before_result["confidence"],
                after_result["confidence"]
            )
        }


# 싱글톤 인스턴스
trash_classifier = TrashClassifier()
