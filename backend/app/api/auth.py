"""인증 (구글 OAuth)"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from pydantic import BaseModel
import httpx

from app.api.deps import get_db, get_current_user
from app.config import settings
from app.models.user import User
from app.schemas.user import UserResponse, TokenResponse


router = APIRouter()


class GoogleLoginRequest(BaseModel):
    id_token: str


class GoogleUserInfo(BaseModel):
    email: str
    name: str
    picture: str | None = None
    sub: str  # Google user ID


def create_access_token(user_id: str) -> str:
    """JWT 액세스 토큰 생성"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "exp": expire
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def verify_google_token(id_token: str) -> GoogleUserInfo:
    """Google ID 토큰 검증"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 Google 토큰입니다"
            )

        data = response.json()

        # 클라이언트 ID 검증
        if data.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰의 대상이 올바르지 않습니다"
            )

        return GoogleUserInfo(
            email=data["email"],
            name=data.get("name", data["email"].split("@")[0]),
            picture=data.get("picture"),
            sub=data["sub"]
        )


@router.post("/google", response_model=TokenResponse)
async def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """
    구글 로그인
    - Google ID 토큰을 검증하고 JWT 발급
    - 신규 유저인 경우 자동 회원가입
    """
    # Google 토큰 검증
    google_user = await verify_google_token(request.id_token)

    # 기존 유저 조회
    user = db.query(User).filter(User.email == google_user.email).first()

    if not user:
        # 신규 유저 생성
        user = User(
            email=google_user.email,
            nickname=google_user.name,
            profile_image=google_user.picture,
            provider="google",
            provider_id=google_user.sub
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # 기존 유저 정보 업데이트
        if google_user.picture and user.profile_image != google_user.picture:
            user.profile_image = google_user.picture
            db.commit()

    # JWT 토큰 생성
    access_token = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    로그아웃
    - 클라이언트에서 토큰 삭제하면 됨
    - 서버에서는 특별한 처리 없음 (stateless)
    """
    return {"message": "로그아웃되었습니다"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 유저 정보"""
    return current_user
