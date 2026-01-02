#!/bin/bash
#
# MyApp Store - 프로덕션 빌드 및 테스트 스크립트
#

set -e  # 에러 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 배너 출력
echo "=========================================="
echo "  MyApp Store - Production Build & Test"
echo "=========================================="
echo ""

# 1. 환경변수 파일 확인
log_info "환경변수 파일 확인 중..."
if [ ! -f ".env.production" ]; then
    log_warning ".env.production 파일이 없습니다. 예제 파일을 복사합니다."
    cp .env.production.example .env.production
    log_warning "⚠️  .env.production 파일을 편집하여 실제 값을 입력하세요!"
    log_warning "   특히 SECRET_KEY, POSTGRES_PASSWORD, CORS_ORIGINS를 변경해야 합니다."
    echo ""
    read -p "계속하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "빌드를 중단합니다."
        exit 1
    fi
else
    log_success ".env.production 파일 발견"
fi

# 2. 필수 디렉토리 생성
log_info "필수 디렉토리 생성 중..."
mkdir -p data/{db,logs,icons,screenshots,eximage,library,config}
mkdir -p data/logs/postgresql
log_success "디렉토리 생성 완료"

# 3. 기존 컨테이너 정리 (선택사항)
read -p "기존 프로덕션 컨테이너를 정리하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "기존 컨테이너 정리 중..."
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    log_success "기존 컨테이너 정리 완료"
fi

# 4. Docker 이미지 빌드
log_info "Docker 이미지 빌드 시작..."
log_info "이 작업은 5-10분 정도 소요될 수 있습니다."
echo ""

if docker-compose -f docker-compose.prod.yml --env-file .env.production build; then
    log_success "Docker 이미지 빌드 완료"
else
    log_error "Docker 이미지 빌드 실패"
    exit 1
fi

# 5. 빌드된 이미지 확인
log_info "빌드된 이미지 확인 중..."
echo ""
docker images | grep -E "(REPOSITORY|myappstore)"
echo ""

# 6. 컨테이너 실행
log_info "컨테이너 실행 중..."
if docker-compose -f docker-compose.prod.yml --env-file .env.production up -d; then
    log_success "컨테이너 실행 완료"
else
    log_error "컨테이너 실행 실패"
    exit 1
fi

# 7. 컨테이너 상태 확인 (30초 대기)
log_info "컨테이너 시작 대기 중 (30초)..."
sleep 30

log_info "컨테이너 상태 확인 중..."
echo ""
docker-compose -f docker-compose.prod.yml ps
echo ""

# 8. 헬스체크
log_info "헬스체크 실행 중..."
echo ""

# 백엔드 헬스체크
log_info "백엔드 헬스체크..."
if curl -sf http://localhost:8100/health > /dev/null; then
    log_success "✓ 백엔드: 정상"
else
    log_error "✗ 백엔드: 응답 없음"
fi

# 프론트엔드 헬스체크
log_info "프론트엔드 헬스체크..."
if curl -sf http://localhost:5900/ > /dev/null; then
    log_success "✓ 프론트엔드: 정상"
else
    log_error "✗ 프론트엔드: 응답 없음"
fi

# PostgreSQL 헬스체크
log_info "PostgreSQL 헬스체크..."
if docker exec myapp-db-prod pg_isready -U postgres > /dev/null 2>&1; then
    log_success "✓ PostgreSQL: 정상"
else
    log_error "✗ PostgreSQL: 연결 실패"
fi

# Redis 헬스체크
log_info "Redis 헬스체크..."
if docker exec myapp-redis-prod redis-cli ping > /dev/null 2>&1; then
    log_success "✓ Redis: 정상"
else
    log_error "✗ Redis: 연결 실패"
fi

echo ""
echo "=========================================="
log_success "빌드 및 테스트 완료!"
echo "=========================================="
echo ""

# 9. 접속 정보 출력
log_info "접속 정보:"
echo ""
echo "  프론트엔드:  http://localhost:5900"
echo "  백엔드 API:  http://localhost:8100"
echo "  API 문서:    http://localhost:8100/docs"
echo "  API 상태:    http://localhost:8100/api-status"
echo ""

# 10. 다음 단계 안내
log_info "다음 단계:"
echo ""
echo "  1. 브라우저에서 http://localhost:5900 접속"
echo "  2. 초기 관리자 계정 생성"
echo "  3. 스캔 경로 설정 (관리자 페이지)"
echo "  4. 자동 스캔 스케줄러 설정"
echo ""

# 11. 로그 확인 옵션
read -p "실시간 로그를 확인하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "로그 모니터링 시작 (Ctrl+C로 종료)..."
    docker-compose -f docker-compose.prod.yml logs -f
fi

log_success "스크립트 종료"
