#!/bin/bash

# 해몬도감 서버 실행 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
VENV_DIR="$SCRIPT_DIR/.venv"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

# 가상환경 확인 및 생성
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_status "가상환경 생성 중..."
        python3 -m venv "$VENV_DIR"
        print_success "가상환경 생성 완료"
    fi
}

# 가상환경 활성화
activate_venv() {
    print_status "가상환경 활성화..."
    source "$VENV_DIR/bin/activate"
    print_success "가상환경 활성화됨: $VIRTUAL_ENV"
}

# 의존성 설치
install_deps() {
    print_status "의존성 설치 중..."
    pip install -q --upgrade pip
    pip install -q -r "$BACKEND_DIR/requirements.txt"
    print_success "의존성 설치 완료"
}

# .env 파일 확인
check_env() {
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        print_warning ".env 파일이 없습니다. .env.example을 복사합니다..."
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
        print_warning ".env 파일을 수정해주세요!"
    fi
}

# 서버 실행
run_server() {
    cd "$BACKEND_DIR"

    print_success "서버 시작!"
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  해몬도감 API 서버${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "  API:  ${BLUE}http://localhost:8000${NC}"
    echo -e "  Docs: ${BLUE}http://localhost:8000/docs${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# 도움말
show_help() {
    echo "사용법: ./run.sh [옵션]"
    echo ""
    echo "옵션:"
    echo "  (없음)     서버 실행 (기본)"
    echo "  install    의존성만 설치"
    echo "  dev        개발 모드로 서버 실행 (reload 활성화)"
    echo "  prod       프로덕션 모드로 서버 실행"
    echo "  migrate    DB 마이그레이션 실행"
    echo "  test       테스트 실행"
    echo "  help       도움말 표시"
}

# 메인
main() {
    case "${1:-dev}" in
        install)
            setup_venv
            activate_venv
            install_deps
            print_success "설치 완료!"
            ;;
        dev)
            setup_venv
            activate_venv
            install_deps
            check_env
            run_server
            ;;
        prod)
            setup_venv
            activate_venv
            install_deps
            check_env
            cd "$BACKEND_DIR"
            print_success "프로덕션 모드로 서버 시작..."
            uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
            ;;
        migrate)
            setup_venv
            activate_venv
            cd "$BACKEND_DIR"
            print_status "마이그레이션 실행..."
            alembic upgrade head
            print_success "마이그레이션 완료!"
            ;;
        test)
            setup_venv
            activate_venv
            install_deps
            cd "$BACKEND_DIR"
            print_status "테스트 실행..."
            pytest tests/ -v
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
