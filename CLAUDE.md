# 🌊 해몬도감 - 해양 생물 도감 & 쓰레기 수거 인증 앱

> 바다를 지키면서 도감을 채운다

## 📌 프로젝트 개요

해양 ESG 게이미피케이션 앱. 포켓몬GO 스타일 수집형 + 환경보호 액션 인증.

- **타겟**: 해변 방문객, MZ세대
- **차별점**: AI 기반 자동 분류 + 실제 ESG 데이터 수집

---

## 🛠️ 기술 스택

```

Backend
├── FastAPI (Python 3.11+)
├── PostgreSQL (Supabase)
├── Supabase Storage (이미지)
└── SQLAlchemy + Alembic

AI/ML
├── HuggingFace Transformers (이미지 분류)
├── OpenAI Vision API (백업/고도화)
└── ImageHash (중복 검증)

Deploy
├── Frontend: Vercel
├── Backend: Railway / Render
└── DB: Supabase
```

---

## 📁 백엔드 폴더 구조

```
backend/
├── app/
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 환경변수 설정
│   ├── database.py             # DB 연결
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # 의존성 (현재 유저, DB 세션)
│   │   ├── auth.py             # 인증 (구글 OAuth)
│   │   ├── users.py            # 유저 프로필, 포인트
│   │   ├── sightings.py        # 생물 목격 CRUD
│   │   ├── cleanups.py         # 쓰레기 수거 CRUD
│   │   ├── creatures.py        # 생물 도감 마스터
│   │   ├── collection.py       # 유저 도감 (발견 목록)
│   │   ├── badges.py           # 업적/뱃지
│   │   ├── rankings.py         # 랭킹
│   │   └── maps.py             # 지도 데이터 (히트맵)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_classifier.py    # AI 이미지 분류 통합
│   │   ├── creature_ai.py      # 해양 생물 판별
│   │   ├── trash_ai.py         # 쓰레기 분류 & Before/After 검증
│   │   ├── image_hash.py       # 중복/악용 방지
│   │   ├── point_service.py    # 포인트 계산
│   │   └── storage.py          # Supabase Storage 연동
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── creature.py
│   │   ├── sighting.py
│   │   ├── cleanup.py
│   │   ├── badge.py
│   │   └── user_creature.py
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── user.py
│       ├── creature.py
│       ├── sighting.py
│       ├── cleanup.py
│       ├── ai.py               # AI 응답 스키마
│       └── common.py
│
├── alembic/                    # DB 마이그레이션
├── tests/
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## 🔌 API 엔드포인트 설계

### 인증

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/auth/google` | 구글 로그인 |
| POST | `/api/auth/logout` | 로그아웃 |
| GET | `/api/auth/me` | 현재 유저 정보 |

### 생물 목격

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/sightings` | 목격 등록 |
| GET | `/api/sightings` | 목격 목록 (피드) |
| GET | `/api/sightings/{id}` | 목격 상세 |
| PATCH | `/api/sightings/{id}/status` | 승인/거절 (관리자) |

### 쓰레기 수거

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/cleanups` | 수거 인증 등록 |
| GET | `/api/cleanups` | 수거 목록 |
| GET | `/api/cleanups/{id}` | 수거 상세 |

### AI 분류 (핵심)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/ai/classify/creature` | 생물 사진 → 종류 판별 |
| POST | `/api/ai/classify/trash` | 쓰레기 사진 → 종류 분류 |
| POST | `/api/ai/verify/cleanup` | Before/After 변화 검증 |
| POST | `/api/ai/check-duplicate` | 이미지 중복 검사 |

### 도감 & 컬렉션

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/creatures` | 전체 생물 도감 |
| GET | `/api/collection` | 내 도감 (발견 목록) |
| GET | `/api/collection/stats` | 도감 완성률 |

### 랭킹 & 업적

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/rankings/collection` | 도감 완성률 랭킹 |
| GET | `/api/rankings/cleanup` | 수거왕 랭킹 |
| GET | `/api/badges` | 전체 뱃지 목록 |
| GET | `/api/badges/my` | 내 뱃지 |

### 지도

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/maps/sightings` | 목격 위치 데이터 |
| GET | `/api/maps/cleanups` | 수거 위치 데이터 |
| GET | `/api/maps/heatmap` | 히트맵 데이터 |

---

## 🤖 AI 서비스 구현 가이드

### 1. 생물 판별 AI (`creature_ai.py`)

```python
"""
해양 생물 자동 판별 서비스
- 1차: HuggingFace 이미지 분류
- 결과: 카테고리 + 신뢰도 반환
- 최종 판정은 관리자 승인
"""

from transformers import pipeline
from PIL import Image
import io

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
    "돌고래": "rare",
    "바다거북": "rare",
    "가오리": "rare",
    "고래": "legendary",
    "상괭이": "legendary",
    "점박이물범": "legendary",
}

class CreatureClassifier:
    def __init__(self):
        # 가벼운 모델 사용 (해커톤용)
        self.classifier = pipeline(
            "image-classification",
            model="google/vit-base-patch16-224"
        )
    
    async def classify(self, image_bytes: bytes) -> dict:
        """
        이미지 → 생물 카테고리 + 신뢰도
        """
        image = Image.open(io.BytesIO(image_bytes))
        results = self.classifier(image)
        
        # 결과 매핑 (ImageNet 라벨 → 우리 카테고리)
        # 실제로는 fine-tuned 모델 또는 프롬프트 기반 필요
        
        return {
            "suggested_creature": "돌고래",
            "category": "cetacean",
            "confidence": 0.85,
            "rarity": "rare",
            "is_confident": True  # confidence > 0.7
        }
```

### 2. 쓰레기 분류 AI (`trash_ai.py`)

```python
"""
쓰레기 분류 + Before/After 검증
- 쓰레기 종류 자동 분류
- Before/After 변화 감지
"""

TRASH_TYPES = [
    "plastic",      # 플라스틱
    "styrofoam",    # 스티로폼
    "fishing_gear", # 그물/어구
    "glass",        # 유리
    "metal",        # 금속
    "other",        # 기타
]

class TrashClassifier:
    def __init__(self):
        self.classifier = pipeline(
            "image-classification",
            model="google/vit-base-patch16-224"
        )
    
    async def classify_trash(self, image_bytes: bytes) -> dict:
        """쓰레기 종류 분류"""
        return {
            "trash_type": "plastic",
            "confidence": 0.82,
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
            before_result["has_trash"] == True and
            after_result["has_trash"] == False
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
```

### 3. 이미지 중복 검사 (`image_hash.py`)

```python
"""
이미지 중복/악용 방지
- Perceptual Hash로 유사 이미지 탐지
- 인터넷 다운로드 이미지 필터링
"""

import imagehash
from PIL import Image
import io

class ImageHashService:
    def __init__(self, db_session):
        self.db = db_session
    
    def compute_hash(self, image_bytes: bytes) -> str:
        """이미지 해시 계산"""
        image = Image.open(io.BytesIO(image_bytes))
        return str(imagehash.phash(image))
    
    async def check_duplicate(
        self, 
        image_bytes: bytes,
        user_id: str
    ) -> dict:
        """
        중복 검사
        - 같은 유저가 같은 사진 재업로드
        - 다른 유저의 사진 도용
        """
        new_hash = self.compute_hash(image_bytes)
        
        # DB에서 유사 해시 검색
        # hamming distance < 5 → 유사 이미지
        
        return {
            "is_duplicate": False,
            "similar_image_id": None,
            "hash": new_hash
        }
```

---

## 🗄️ DB 스키마

```sql
-- 사용자
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    profile_image TEXT,
    points INTEGER DEFAULT 0,
    provider VARCHAR(20), --google
    provider_id VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 생물 도감 마스터
CREATE TABLE creatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    name_en VARCHAR(50),
    category VARCHAR(30) NOT NULL, -- cetacean, turtle, fish...
    description TEXT,
    image_url TEXT,
    rarity VARCHAR(20) NOT NULL, -- common, rare, legendary
    points INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 생물 목격 기록
CREATE TABLE sightings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    creature_id UUID REFERENCES creatures(id),
    photo_url TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    location_name VARCHAR(100),
    memo TEXT,
    image_hash VARCHAR(64),
    ai_suggestion VARCHAR(50),
    ai_confidence DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 쓰레기 수거 기록
CREATE TABLE cleanups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    before_photo_url TEXT NOT NULL,
    after_photo_url TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    location_name VARCHAR(100),
    trash_type VARCHAR(30) NOT NULL, -- plastic, styrofoam, fishing_gear...
    amount VARCHAR(20) NOT NULL, -- handful, one_bag, large
    before_image_hash VARCHAR(64),
    after_image_hash VARCHAR(64),
    ai_verified BOOLEAN DEFAULT FALSE,
    ai_confidence DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'pending',
    points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 업적/뱃지
CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    icon_url TEXT,
    condition_type VARCHAR(30), -- sighting_count, cleanup_count, streak...
    condition_value INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 유저 뱃지
CREATE TABLE user_badges (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID REFERENCES badges(id),
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, badge_id)
);

-- 유저 도감 (발견한 생물)
CREATE TABLE user_creatures (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    creature_id UUID REFERENCES creatures(id),
    first_sighting_id UUID REFERENCES sightings(id),
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, creature_id)
);

-- 인덱스
CREATE INDEX idx_sightings_location ON sightings USING GIST (location);
CREATE INDEX idx_cleanups_location ON cleanups USING GIST (location);
CREATE INDEX idx_sightings_user ON sightings(user_id);
CREATE INDEX idx_cleanups_user ON cleanups(user_id);
CREATE INDEX idx_sightings_status ON sightings(status);
```

---

## 🔄 핵심 플로우

### 생물 목격 등록 플로우

```
1. 사용자가 사진 촬영
2. POST /api/ai/classify/creature (이미지)
   → AI가 생물 종류 추천 + 신뢰도 반환
3. POST /api/ai/check-duplicate (이미지)
   → 중복 검사
4. 사용자가 종류 확인/수정 후 제출
5. POST /api/sightings
   → DB 저장 (status: pending)
   → 이미지 Supabase Storage 업로드
6. 관리자 승인 시
   → status: approved
   → 포인트 지급
   → user_creatures에 추가 (첫 발견 시)
   → 뱃지 체크
```

### 쓰레기 수거 인증 플로우

```
1. 사용자가 Before 사진 촬영
2. 청소 진행
3. 사용자가 After 사진 촬영
4. POST /api/ai/verify/cleanup (before, after)
   → AI가 변화 검증
5. POST /api/ai/classify/trash (before 이미지)
   → 쓰레기 종류 자동 분류
6. 사용자가 확인 후 제출
7. POST /api/cleanups
   → DB 저장
8. 자동 또는 관리자 승인
   → 포인트 지급
   → 뱃지 체크
```

---

## ⚡ 포인트 계산 로직

```python
# point_service.py

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
```

---

## 🚀 MVP 구현 우선순위

### Phase 1 - 기본 동작 (Day 1)

- [ ] FastAPI 프로젝트 세팅
- [ ] Supabase 연결 + DB 마이그레이션
- [ ] 구글로그인
- [ ] 이미지 업로드 (Supabase Storage)

### Phase 2 - 핵심 기능 (Day 1-2)

- [ ] 생물 목격 등록 API
- [ ] 쓰레기 수거 등록 API
- [ ] AI 분류 엔드포인트 (HuggingFace)
- [ ] 이미지 해시 중복 검사

### Phase 3 - 도감 & 지도 (Day 2)

- [ ] 생물 도감 API
- [ ] 유저 컬렉션 API
- [ ] 지도 데이터 API

### Phase 4 - 게이미피케이션 (Day 2-3)

- [ ] 포인트 시스템
- [ ] 랭킹 API
- [ ] 뱃지 시스템

---

## 📝 환경변수 (.env)

```env
# Database
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
SUPABASE_SERVICE_KEY=xxx

# Auth
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
JWT_SECRET=xxx

# AI
HUGGINGFACE_API_KEY=xxx
OPENAI_API_KEY=xxx  # 백업용

# App
FRONTEND_URL=http://localhost:3000
```

---

## 🧪 테스트 명령어

```bash
# 서버 실행
cd backend
uvicorn app.main:app --reload

# DB 마이그레이션
alembic upgrade head

# 테스트
pytest tests/
```

---

## 📌 주의사항

1. **AI는 보조 역할**: 최종 판정은 관리자 승인으로
2. **이미지 해시 필수**: 악용 방지
3. **위치 검증**: GPS 메타데이터 확인
4. **해커톤 데모용**: 실제 fine-tuned 모델은 추후 적용