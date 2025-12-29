"""정적 뱃지 정의 (프론트에서 아이콘 관리)"""

from uuid import UUID

STATIC_BADGES = [
    {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "name": "위대한 여정의 첫걸음",
        "description": "동물을 1개 발견했습니다",
        "condition_type": "collection_count",
        "condition_value": 1,
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000003"),
        "name": "바다 달인",
        "description": "동물을 3개 발견했습니다",
        "condition_type": "collection_count",
        "condition_value": 3,
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000005"),
        "name": "바다 장인",
        "description": "동물을 5개 발견했습니다",
        "condition_type": "collection_count",
        "condition_value": 5,
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000009"),
        "name": "여긴 이제 내 바다야",
        "description": "동물을 9개 발견했습니다",
        "condition_type": "collection_count",
        "condition_value": 9,
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000011"),
        "name": "바다의 왕자",
        "description": "동물을 11개 발견했습니다",
        "condition_type": "collection_count",
        "condition_value": 11,
    },
]

