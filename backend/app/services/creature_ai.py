"""
해양 생물 자동 판별 서비스
- 1차: HuggingFace 이미지 분류
- 결과: 카테고리 + 신뢰도 반환
- 최종 판정은 관리자 승인
"""
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# 분류 카테고리 (종 단위 X, 카테고리 단위 O)
CREATURE_CATEGORIES = {
    "cetacean": ["고래", "돌고래", "상괭이"],      # 고래류
    "turtle": ["바다거북"],                        # 거북류
    "pinniped": ["물범", "바다사자"],              # 기각류
    "fish": ["가오리", "상어"],                    # 어류
    "jellyfish": ["해파리"],                       # 해파리류
    "crustacean": ["게", "새우"],                  # 갑각류
    "mollusk": ["조개", "문어", "오징어"],         # 연체류
    "bird": ["갈매기", "펠리컨"],                  # 조류
}

RARITY_MAP = {
    "갈매기": "common",
    "조개": "common",
    "해파리": "common",
    "게": "common",
    "새우": "common",
    "돌고래": "rare",
    "바다거북": "rare",
    "가오리": "rare",
    "문어": "rare",
    "오징어": "rare",
    "고래": "legendary",
    "상괭이": "legendary",
    "점박이물범": "legendary",
    "물범": "legendary",
    "바다사자": "legendary",
    "상어": "legendary",
}

# ImageNet 라벨 → 해양 생물 매핑 (일부)
IMAGENET_MAPPING = {
    "killer_whale": ("고래", "cetacean"),
    "grey_whale": ("고래", "cetacean"),
    "dugong": ("돌고래", "cetacean"),
    "sea_lion": ("바다사자", "pinniped"),
    "loggerhead": ("바다거북", "turtle"),
    "leatherback_turtle": ("바다거북", "turtle"),
    "jellyfish": ("해파리", "jellyfish"),
    "starfish": ("불가사리", "other"),
    "sea_urchin": ("성게", "other"),
    "sea_cucumber": ("해삼", "other"),
    "hermit_crab": ("게", "crustacean"),
    "king_crab": ("게", "crustacean"),
    "rock_crab": ("게", "crustacean"),
    "crayfish": ("새우", "crustacean"),
    "lobster": ("새우", "crustacean"),
    "octopus": ("문어", "mollusk"),
    "sea_slug": ("갯민숭달팽이", "mollusk"),
    "conch": ("조개", "mollusk"),
    "snail": ("조개", "mollusk"),
    "stingray": ("가오리", "fish"),
    "electric_ray": ("가오리", "fish"),
    "great_white_shark": ("상어", "fish"),
    "tiger_shark": ("상어", "fish"),
    "hammerhead": ("상어", "fish"),
    "albatross": ("갈매기", "bird"),
}


class CreatureClassifier:
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

    async def classify(self, image_bytes: bytes) -> dict:
        """
        이미지 → 생물 카테고리 + 신뢰도
        """
        self._load_model()

        if self.classifier is None:
            # 모델 로드 실패 시 기본값 반환
            return {
                "suggested_creature": "unknown",
                "category": "unknown",
                "confidence": 0.0,
                "rarity": "common",
                "is_confident": False
            }

        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != "RGB":
                image = image.convert("RGB")

            results = self.classifier(image)

            # 결과 매핑 (ImageNet 라벨 → 우리 카테고리)
            for result in results:
                label = result["label"].lower().replace(" ", "_")
                score = result["score"]

                if label in IMAGENET_MAPPING:
                    creature, category = IMAGENET_MAPPING[label]
                    rarity = RARITY_MAP.get(creature, "common")

                    return {
                        "suggested_creature": creature,
                        "category": category,
                        "confidence": round(score, 2),
                        "rarity": rarity,
                        "is_confident": score > 0.7
                    }

            # 매핑되지 않은 경우
            return {
                "suggested_creature": "unknown",
                "category": "unknown",
                "confidence": results[0]["score"] if results else 0.0,
                "rarity": "common",
                "is_confident": False
            }

        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {
                "suggested_creature": "unknown",
                "category": "unknown",
                "confidence": 0.0,
                "rarity": "common",
                "is_confident": False
            }


# 싱글톤 인스턴스
creature_classifier = CreatureClassifier()
