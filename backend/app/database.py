"""DB 연결 설정"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings


# Supabase session 모드: 제한을 넘지 않도록 풀 크기를 낮추되 타임아웃/재활용을 설정한다.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,        # 풀러의 권장치(10 이하)보다 작게 유지
    max_overflow=0,     # 초과 연결 생성 금지
    pool_timeout=5,     # 대기 시간을 줄여 타임아웃을 빨리 반환
    pool_recycle=1800,  # 오래된 커넥션 재활용(30분)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """DB 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
