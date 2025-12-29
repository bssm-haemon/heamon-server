"""정적 도감 데이터 (프론트와 동일한 ID/희귀도 매핑)"""

STATIC_CREATURES = [
    {"id": "creature-001", "name": "고등어", "category": "fish", "rarity": "common"},
    {"id": "creature-002", "name": "꽁치", "category": "fish", "rarity": "common"},
    {"id": "creature-003", "name": "가자미", "category": "fish", "rarity": "common"},
    {"id": "creature-004", "name": "복어", "category": "fish", "rarity": "rare"},
    {"id": "creature-005", "name": "오징어", "category": "mollusk", "rarity": "rare"},
    {"id": "creature-006", "name": "문어", "category": "mollusk", "rarity": "rare"},
    {"id": "creature-007", "name": "해마", "category": "fish", "rarity": "rare"},
    {"id": "creature-008", "name": "바다거북", "category": "turtle", "rarity": "rare"},
    {"id": "creature-009", "name": "돌고래", "category": "cetacean", "rarity": "legendary"},
    {"id": "creature-010", "name": "점박이물범", "category": "pinniped", "rarity": "legendary"},
    {"id": "creature-011", "name": "고래상어", "category": "fish", "rarity": "legendary"},
]

RARITY_BY_ID = {c["id"]: c["rarity"] for c in STATIC_CREATURES}
NAME_BY_ID = {c["id"]: c["name"] for c in STATIC_CREATURES}
CATEGORY_BY_ID = {c["id"]: c["category"] for c in STATIC_CREATURES}
ID_BY_NAME = {c["name"]: c["id"] for c in STATIC_CREATURES}
ID_BY_NAME_LOWER = {c["name"].lower(): c["id"] for c in STATIC_CREATURES}

TOTAL_BY_RARITY = {
    "common": len([c for c in STATIC_CREATURES if c["rarity"] == "common"]),
    "rare": len([c for c in STATIC_CREATURES if c["rarity"] == "rare"]),
    "legendary": len([c for c in STATIC_CREATURES if c["rarity"] == "legendary"]),
}

TOTAL_CREATURES = len(STATIC_CREATURES)
