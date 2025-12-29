"""Vercel 진입점"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
root_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(root_dir))

from app.main import app

# Vercel이 사용할 핸들러
handler = app
