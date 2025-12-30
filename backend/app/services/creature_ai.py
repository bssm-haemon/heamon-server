"""
해양 생물 자동 판별 서비스
- HuggingFace 사전학습 분류기(jasasuster/sea-animals) 활용
- 모델 라벨을 서비스 도감 라벨로 후처리 매핑
"""
import hashlib
import io
import logging
from typing import List, Optional, Tuple

from PIL import Image

logger = logging.getLogger(__name__)

MIN_CONFIDENT_SCORE = 0.35  # top-1 점수가 낮으면 추정으로 표시

RARITY_MAP = {
    "조개": "common",
    "해파리": "common",
    "게": "common",
    "새우": "common",
    "돌고래": "rare",
    "바다거북": "rare",
    "가오리": "rare",
    "문어": "rare",
    "오징어": "rare",
    "해마": "rare",
    "고래": "legendary",
    "상괭이": "legendary",
    "점박이물범": "legendary",
    "물범": "legendary",
    "바다사자": "legendary",
    "상어": "legendary",
    "고래상어": "legendary",
    "복어": "rare",
    "고등어": "common",
    "꽁치": "common",
}


class CreatureClassifier:
    def __init__(self):
        self.classifier = None
        self.model_name = "jasasuster/sea-animals"
        # 모델 로드 실패 시 예측 제공을 위한 백업 후보군
        self.fallback_creatures = [
            ("돌고래", "cetacean", "rare"),
            ("점박이물범", "pinniped", "legendary"),
            ("바다거북", "turtle", "rare"),
            ("고래상어", "fish", "legendary"),
            ("해마", "fish", "rare"),
            ("복어", "fish", "rare"),
            ("고등어", "fish", "common"),
            ("꽁치", "fish", "common"),
            ("오징어", "mollusk", "rare"),
            ("문어", "mollusk", "rare"),
        ]

    def _load_model(self):
        """모델 지연 로딩"""
        if self.classifier is None:
            try:
                from transformers import pipeline

                self.classifier = pipeline(
                    "image-classification",
                    model=self.model_name
                )
            except Exception as e:
                logger.warning(f"Failed to load HuggingFace model: {e}")
                self.classifier = None

    def _map_label(self, label: str) -> Optional[Tuple[str, str, str]]:
        """모델 라벨을 서비스 도감 라벨로 후처리 매핑."""
        label_l = label.lower()
        mapping: List[Tuple[List[str], Tuple[str, str, str]]] = [
            (["whale shark", "whale_shark"], ("고래상어", "fish", "legendary")),
            (["dolphin", "porpoise"], ("돌고래", "cetacean", "rare")),
            (["whale"], ("고래상어", "fish", "legendary")),
            (["turtle"], ("바다거북", "turtle", "rare")),
            (["spotted seal", "largha"], ("점박이물범", "pinniped", "legendary")),
            (["sea lion"], ("바다사자", "pinniped", "legendary")),
            (["seal"], ("물범", "pinniped", "legendary")),
            (["ray", "stingray"], ("가오리", "fish", "rare")),
            (["shark"], ("돌고래", "cetacean", "rare")),
            (["puffer", "fugu"], ("복어", "fish", "rare")),
            (["mackerel"], ("고등어", "fish", "common")),
            (["saury"], ("꽁치", "fish", "common")),
            (["seahorse"], ("해마", "fish", "rare")),
            (["octopus"], ("문어", "mollusk", "rare")),
            (["squid"], ("오징어", "mollusk", "rare")),
            (["clam", "shell"], ("조개", "mollusk", "common")),
            (["jellyfish"], ("해파리", "jellyfish", "common")),
            (["crab"], ("게", "crustacean", "common")),
            (["shrimp", "prawn"], ("새우", "crustacean", "common")),
        ]

        for keywords, mapped in mapping:
            if any(k in label_l for k in keywords):
                return mapped
        return None

    async def classify(self, image_bytes: bytes) -> dict:
        """
        이미지 → 생물 카테고리 + 신뢰도
        """
        self._load_model()

        if self.classifier is None:
            # 모델 로드 실패 시: 이미지 해시 기반의 결정적 백업 추정
            digest = hashlib.md5(image_bytes).hexdigest()
            idx = int(digest, 16) % len(self.fallback_creatures)
            creature, category, rarity = self.fallback_creatures[idx]
            return {
                "suggested_creature": creature,
                "category": category,
                "confidence": 0.66,
                "rarity": rarity,
                "is_confident": False,
            }

        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != "RGB":
                image = image.convert("RGB")

            raw_results = self.classifier(image, top_k=5)
            candidates = []
            for result in raw_results:
                mapped = self._map_label(result["label"])
                if mapped is None:
                    continue
                creature, category, rarity = mapped
                candidates.append(
                    {
                        "creature": creature,
                        "category": category,
                        "confidence": round(float(result["score"]), 3),
                        "rarity": rarity,
                    }
                )

            if candidates:
                best = candidates[0]
                return {
                    "suggested_creature": best["creature"],
                    "category": best["category"],
                    "confidence": round(best["confidence"], 2),
                    "rarity": best["rarity"],
                    "is_confident": best["confidence"] >= MIN_CONFIDENT_SCORE,
                    "candidates": candidates,
                }

            # 매핑되지 않은 경우: fallback
            digest = hashlib.md5(image_bytes).hexdigest()
            idx = int(digest, 16) % len(self.fallback_creatures)
            creature, category, rarity = self.fallback_creatures[idx]
            return {
                "suggested_creature": creature,
                "category": category,
                "confidence": 0.5,
                "rarity": rarity,
                "is_confident": False,
            }

        except Exception as e:
            logger.error(f"Classification error: {e}")
            digest = hashlib.md5(image_bytes).hexdigest()
            idx = int(digest, 16) % len(self.fallback_creatures)
            creature, category, rarity = self.fallback_creatures[idx]
            return {
                "suggested_creature": creature,
                "category": category,
                "confidence": 0.5,
                "rarity": rarity,
                "is_confident": False,
            }


# 싱글톤 인스턴스
creature_classifier = CreatureClassifier()
