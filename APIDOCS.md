# 해몬도감 API 문서

> 해양 생물 도감 & 쓰레기 수거 인증 앱 API

**Base URL**: `http://localhost:8000/api`

**인증 방식**: Bearer Token (JWT)

---

## 목차

1. [인증 (Auth)](#인증-auth)
2. [사용자 (Users)](#사용자-users)
3. [생물 목격 (Sightings)](#생물-목격-sightings)
4. [쓰레기 수거 (Cleanups)](#쓰레기-수거-cleanups)
5. [생물 도감 (Creatures)](#생물-도감-creatures)
6. [내 도감 (Collection)](#내-도감-collection)
7. [뱃지 (Badges)](#뱃지-badges)
8. [랭킹 (Rankings)](#랭킹-rankings)
9. [지도 (Maps)](#지도-maps)
10. [AI 분류 (AI)](#ai-분류-ai)

---

## 인증 (Auth)

### POST `/auth/google`
구글 로그인 (OAuth 2.0 Authorization Code Flow)

**Request Body**
```json
{
  "code": "Google OAuth Authorization Code"
}
```

**백엔드 처리 로직**
1. 프론트엔드로부터 `code`를 전달받음
2. Google Token Endpoint(`https://oauth2.googleapis.com/token`)에 아래 파라미터로 POST
   - `code`: 전달받은 authorization code
   - `client_id`: 환경변수 `GOOGLE_CLIENT_ID`
   - `client_secret`: 환경변수 `GOOGLE_CLIENT_SECRET`
   - `redirect_uri`: 환경변수 `GOOGLE_REDIRECT_URI` (예: `http://localhost:3000/login`)
   - `grant_type`: `authorization_code`
3. 응답으로 받은 `id_token`을 검증하고 유저 정보를 DB에 저장/업데이트 후 JWT 발급

> 개발 모드(`DEBUG=true`)에서는 구글 호출 없이 `{"code": "dev:{email}"}` 형식으로 로그인할 수 있습니다. 예) `dev:user@local.test`

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "nickname": "홍길동",
    "profile_image": "https://...",
    "points": 0,
    "is_admin": false,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### POST `/auth/logout`
로그아웃

**Headers**: `Authorization: Bearer {token}`

**Response** `200 OK`
```json
{
  "message": "로그아웃되었습니다"
}
```

---

### GET `/auth/me`
현재 유저 정보

**Headers**: `Authorization: Bearer {token}`

**Response** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "홍길동",
  "profile_image": "https://...",
  "points": 150,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 사용자 (Users)

### GET `/users/me`
내 프로필 상세 조회

**Headers**: `Authorization: Bearer {token}`

**Response** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "홍길동",
  "profile_image": "https://...",
  "points": 150,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00Z",
  "sighting_count": 10,
  "cleanup_count": 5,
  "creature_count": 8,
  "badge_count": 3
}
```

---

### PATCH `/users/me`
내 프로필 수정

**Headers**: `Authorization: Bearer {token}`

**Request Body**
```json
{
  "nickname": "새닉네임",
  "profile_image": "https://..."
}
```

**Response** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "새닉네임",
  "profile_image": "https://...",
  "points": 150,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### GET `/users/{user_id}`
유저 프로필 조회 (공개)

**Response** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "홍길동",
  "profile_image": "https://...",
  "points": 150,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00Z",
  "sighting_count": 10,
  "cleanup_count": 5,
  "creature_count": 8,
  "badge_count": 3
}
```

---

## 생물 목격 (Sightings)

### POST `/sightings`
목격 등록

**Headers**: `Authorization: Bearer {token}`

**Content-Type**: `multipart/form-data`

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| photo | File | O | 사진 파일 |
| latitude | float | O | 위도 |
| longitude | float | O | 경도 |
| location_name | string | X | 장소명 |
| memo | string | X | 메모 |
| creature_id | string | X | 정적 도감 ID (예: `creature-009`) |
| ai_suggestion | string | X | AI 추천 생물명 |
| ai_confidence | float | X | AI 신뢰도 (0~1) |

**Response** `201 Created`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "creature_id": null,
  "photo_url": "https://supabase.co/storage/...",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "location_name": "해운대해수욕장",
  "memo": "돌고래 발견!",
  "image_hash": "a1b2c3d4...",
  "ai_suggestion": "돌고래",
  "ai_confidence": 0.85,
  "status": "pending",
  "points_earned": 0,
  "created_at": "2024-01-01T12:00:00Z"
}
```

---

### GET `/sightings`
목격 목록 (피드)

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| page | int | 1 | 페이지 번호 |
| limit | int | 20 | 페이지당 개수 |
| status | string | - | 상태 필터 (pending/approved/rejected) |
| user_id | uuid | - | 유저 필터 |

**Response** `200 OK`
```json
{
  "sightings": [...],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

---

### GET `/sightings/{sighting_id}`
목격 상세

**Response** `200 OK`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "creature_id": "creature-009",
  "photo_url": "https://...",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "location_name": "해운대해수욕장",
  "memo": "돌고래 발견!",
  "image_hash": "a1b2c3d4...",
  "ai_suggestion": "돌고래",
  "ai_confidence": 0.85,
  "status": "approved",
  "points_earned": 80,
  "created_at": "2024-01-01T12:00:00Z",
  "user_nickname": "홍길동",
  "creature_name": "돌고래"
}
```

---

### PATCH `/sightings/{sighting_id}/status`
승인/거절 (관리자 전용)

**Headers**: `Authorization: Bearer {admin_token}`

**Request Body**
```json
{
  "status": "approved",
  "creature_id": "creature-009"
}
```

**Response** `200 OK`
- 승인 시: 포인트 지급, 도감에 추가 (첫 발견 시)

---

## 쓰레기 수거 (Cleanups)

### POST `/cleanups`
수거 인증 등록

**Headers**: `Authorization: Bearer {token}`

**Content-Type**: `multipart/form-data`

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| before_photo | File | O | Before 사진 |
| after_photo | File | O | After 사진 |
| latitude | float | O | 위도 |
| longitude | float | O | 경도 |
| location_name | string | X | 장소명 |
| trash_type | string | O | 쓰레기 종류 |
| amount | string | O | 수거량 |
| ai_verified | bool | X | AI 검증 여부 |
| ai_confidence | float | X | AI 신뢰도 |

**trash_type 옵션**
- `plastic`: 플라스틱
- `styrofoam`: 스티로폼
- `fishing_gear`: 그물/어구
- `glass`: 유리
- `metal`: 금속
- `other`: 기타

**amount 옵션**
- `handful`: 한 줌
- `one_bag`: 봉지 하나
- `large`: 대량

**Response** `201 Created`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "before_photo_url": "https://...",
  "after_photo_url": "https://...",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "location_name": "해운대해수욕장",
  "trash_type": "plastic",
  "amount": "one_bag",
  "before_image_hash": "a1b2c3d4...",
  "after_image_hash": "e5f6g7h8...",
  "ai_verified": true,
  "ai_confidence": 0.9,
  "status": "pending",
  "points_earned": 0,
  "created_at": "2024-01-01T12:00:00Z"
}
```

---

### GET `/cleanups`
수거 목록

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| page | int | 1 | 페이지 번호 |
| limit | int | 20 | 페이지당 개수 |
| status | string | - | 상태 필터 |
| user_id | uuid | - | 유저 필터 |
| trash_type | string | - | 쓰레기 종류 필터 |

**Response** `200 OK`
```json
{
  "cleanups": [...],
  "total": 50,
  "page": 1,
  "limit": 20
}
```

---

### GET `/cleanups/{cleanup_id}`
수거 상세

**Response** `200 OK`

---

### PATCH `/cleanups/{cleanup_id}/approve`
수거 승인 (관리자 전용)

**Headers**: `Authorization: Bearer {admin_token}`

**Response** `200 OK`
- 포인트 지급

---

### PATCH `/cleanups/{cleanup_id}/reject`
수거 거절 (관리자 전용)

**Headers**: `Authorization: Bearer {admin_token}`

**Response** `200 OK`

---

## 생물 도감 (Creatures)

### GET `/creatures`
정적 도감 안내 (프론트에 데이터 포함)

**Response** `200 OK`
```json
{
  "message": "생물 데이터는 프론트엔드에 정적으로 포함되어 있습니다.",
  "total_creatures": 11,
  "by_rarity": {
    "common": 3,
    "rare": 5,
    "legendary": 3
  },
  "creatures": [
    { "id": "creature-001", "name": "고등어", "rarity": "common" },
    { "id": "creature-009", "name": "돌고래", "rarity": "legendary" }
  ]
}
```

---

### GET `/creatures/{creature_id}`
생물 상세

**Response** `200 OK`

---

### POST `/creatures`
생물 등록 (관리자 전용)

**Headers**: `Authorization: Bearer {admin_token}`

**Request Body**
```json
{
  "name": "돌고래",
  "name_en": "Dolphin",
  "category": "cetacean",
  "description": "지능이 높은 해양 포유류",
  "image_url": "https://...",
  "rarity": "rare",
  "points": 80
}
```

**Response** `201 Created`

---

### PUT `/creatures/{creature_id}`
생물 수정 (관리자 전용)

**Headers**: `Authorization: Bearer {admin_token}`

---

### DELETE `/creatures/{creature_id}`
생물 삭제 (관리자 전용)

**Headers**: `Authorization: Bearer {admin_token}`

**Response** `204 No Content`

---

## 내 도감 (Collection)

### GET `/collection`
내 도감 (발견 목록)

**Headers**: `Authorization: Bearer {token}`

**Response** `200 OK`
```json
{
  "collection": [
    {
      "creature_id": "creature-009",
      "discovered_at": "2024-01-15T12:00:00Z",
      "first_sighting_id": "uuid"
    }
  ],
  "total": 8
}
```

---

### GET `/collection/stats`
도감 완성률

**Headers**: `Authorization: Bearer {token}`

**Response** `200 OK`
```json
{
  "total_creatures": 11,
  "discovered_count": 8,
  "completion_rate": 26.67,
  "by_rarity": {
    "common": {
      "total": 4,
      "discovered": 5
    },
    "rare": {
      "total": 4,
      "discovered": 2
    },
    "legendary": {
      "total": 3,
      "discovered": 1
    }
  }
}
```

---

## 뱃지 (Badges)

### GET `/badges`
전체 뱃지 목록 (정적)

**Response** `200 OK`
```json
{
  "badges": [
    {
      "id": "00000000-0000-0000-0000-000000000001",
      "name": "위대한 여정의 첫걸음",
      "name_ko": "위대한 여정의 첫걸음",
      "description": "동물을 1개 발견했습니다",
      "condition_type": "collection_count",
      "condition_value": 1
    }
  ],
  "total": 10
}
```

---

### GET `/badges/my`
내 뱃지

**Headers**: `Authorization: Bearer {token}`

**Response** `200 OK`
```json
{
  "badges": [
    {
      "badge": {...},
      "earned_at": "2024-01-20T12:00:00Z"
    }
  ],
  "total": 3
}
```

---

### POST `/badges`
정적 관리로 비활성화 (`410 Gone`)  
뱃지는 고정 ID/조건으로 DB에 삽입되며 아이콘은 프론트에서 관리합니다. 스키마에 `name_ko`가 있으므로 응답에도 포함됩니다.

---

### POST `/badges/{badge_id}/award/{user_id}`
뱃지 수여 (관리자 전용)

**Headers**: `Authorization: Bearer {admin_token}`

**Response** `200 OK`
```json
{
  "message": "뱃지가 수여되었습니다"
}
```

---

## 랭킹 (Rankings)

### GET `/rankings/collection`
도감 완성률 랭킹

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| limit | int | 100 | 최대 개수 |

**Response** `200 OK`
```json
{
  "rankings": [
    {
      "rank": 1,
      "user_id": "uuid",
      "nickname": "바다지킴이",
      "profile_image": "https://...",
      "value": 25
    }
  ],
  "my_rank": 15,
  "total_users": 500
}
```

---

### GET `/rankings/cleanup`
수거왕 랭킹

**Response** `200 OK`
- 승인된 수거 횟수 기준

---

### GET `/rankings/points`
포인트 랭킹

**Response** `200 OK`
- 총 포인트 기준

---

## 지도 (Maps)

### GET `/maps/sightings`
목격 위치 데이터

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| status | string | approved | 상태 필터 |
| category | string | - | 카테고리 필터 |
| rarity | string | - | 희귀도 필터 |
| limit | int | 1000 | 최대 개수 |

**Response** `200 OK`
```json
{
  "markers": [
    {
      "id": "uuid",
      "latitude": 37.5665,
      "longitude": 126.9780,
      "type": "sighting",
      "created_at": "2024-01-15T12:00:00Z",
      "location_name": "해운대해수욕장",
      "creature_name": "돌고래",
      "rarity": "rare",
      "photo_url": "https://..."
    }
  ],
  "total": 150
}
```

---

### GET `/maps/cleanups`
수거 위치 데이터

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| status | string | approved | 상태 필터 |
| trash_type | string | - | 쓰레기 종류 필터 |
| limit | int | 1000 | 최대 개수 |

**Response** `200 OK`
```json
{
  "markers": [
    {
      "id": "uuid",
      "latitude": 37.5665,
      "longitude": 126.9780,
      "type": "cleanup",
      "created_at": "2024-01-15T12:00:00Z",
      "location_name": "광안리",
      "trash_type": "plastic",
      "amount": "one_bag"
    }
  ],
  "total": 80
}
```

---

### GET `/maps/heatmap`
히트맵 데이터

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| type | string | combined | sighting/cleanup/combined |

**Response** `200 OK`
```json
{
  "points": [
    {
      "latitude": 37.5665,
      "longitude": 126.9780,
      "weight": 2.0
    }
  ],
  "type": "combined"
}
```

---

## AI 분류 (AI)

### POST `/ai/classify/creature`
생물 사진 → 종류 판별

**Headers**: `Authorization: Bearer {token}`

**Content-Type**: `multipart/form-data`

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| photo | File | O | 사진 파일 |

**Response** `200 OK`
```json
{
  "suggested_creature": "돌고래",
  "category": "cetacean",
  "confidence": 0.85,
  "rarity": "rare",
  "is_confident": true
}
```

---

### POST `/ai/classify/trash`
쓰레기 사진 → 종류 분류

**Headers**: `Authorization: Bearer {token}`

**Content-Type**: `multipart/form-data`

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| photo | File | O | 사진 파일 |

**Response** `200 OK`
```json
{
  "trash_type": "plastic",
  "confidence": 0.82,
  "has_trash": true
}
```

---

### POST `/ai/verify/cleanup`
Before/After 변화 검증

**Headers**: `Authorization: Bearer {token}`

**Content-Type**: `multipart/form-data`

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| before_photo | File | O | Before 사진 |
| after_photo | File | O | After 사진 |

**Response** `200 OK`
```json
{
  "is_valid": true,
  "before_had_trash": true,
  "after_has_trash": false,
  "confidence": 0.78
}
```

---

### POST `/ai/check-duplicate`
이미지 중복 검사

**Headers**: `Authorization: Bearer {token}`

**Content-Type**: `multipart/form-data`

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| photo | File | O | 사진 파일 |

**Response** `200 OK`
```json
{
  "is_duplicate": false,
  "similar_image_id": null,
  "hash": "a1b2c3d4e5f6..."
}
```

---

## 포인트 시스템

### 목격 포인트
| 희귀도 | 기본 포인트 |
|--------|-------------|
| common | 30 |
| rare | 80 |
| legendary | 150 |

### 수거 포인트
| 수거량 | 기본 포인트 |
|--------|-------------|
| handful | 30 |
| one_bag | 50 |
| large | 100 |

### 보너스 포인트
| 조건 | 보너스 |
|------|--------|
| 첫 발견 (도감에 없던 생물) | +20 |

---

## 에러 응답

모든 에러는 다음 형식으로 반환됩니다:

```json
{
  "detail": "에러 메시지"
}
```

### HTTP 상태 코드
| 코드 | 설명 |
|------|------|
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 500 | 서버 오류 |
