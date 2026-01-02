# MyApp Store - 빠른 시작 가이드

## 🚀 한 번에 빌드 및 실행

```bash
# 1. 자동 빌드 스크립트 실행 (권장)
./build-and-test.sh
```

이 스크립트가 자동으로 다음을 수행합니다:
- 환경변수 파일 확인 및 생성
- 필수 디렉토리 생성
- Docker 이미지 빌드
- 컨테이너 실행
- 헬스체크 수행

## 📝 수동 실행 방법

### 1단계: 환경변수 설정

```bash
# 환경변수 예제 파일 복사
cp .env.production.example .env.production

# 환경변수 파일 편집
nano .env.production
```

**필수 변경 항목:**
- `SECRET_KEY`: 강력한 랜덤 키 생성 (`openssl rand -hex 32`)
- `POSTGRES_PASSWORD`: 데이터베이스 비밀번호
- `CORS_ORIGINS`: 허용할 도메인
- `VITE_API_BASE_URL`: 백엔드 API URL (예: `http://192.168.0.8:8100/api`)

### 2단계: 빌드

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production build
```

### 3단계: 실행

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### 4단계: 확인

```bash
# 컨테이너 상태
docker-compose -f docker-compose.prod.yml ps

# 헬스체크
curl http://localhost:8100/health
curl http://localhost:5900/
```

## 🌐 접속 주소

- **프론트엔드**: http://localhost:5900
- **백엔드 API**: http://localhost:8100
- **API 문서**: http://localhost:8100/docs
- **API 상태**: http://localhost:8100/api-status

## 🔧 주요 명령어

### 로그 확인
```bash
# 전체 로그
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 재시작
```bash
# 전체 재시작
docker-compose -f docker-compose.prod.yml restart

# 특정 서비스
docker-compose -f docker-compose.prod.yml restart backend
```

### 중지
```bash
docker-compose -f docker-compose.prod.yml down
```

### 완전 삭제 (데이터 포함)
```bash
docker-compose -f docker-compose.prod.yml down -v
```

## 📚 상세 문서

자세한 내용은 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)를 참조하세요.

## ⚠️ 중요 보안 사항

프로덕션 환경에서는 반드시:
1. ✅ `SECRET_KEY` 변경
2. ✅ 데이터베이스 비밀번호 변경
3. ✅ `CORS_ORIGINS`를 실제 도메인으로 제한
4. ✅ 방화벽 설정 (필요한 포트만 개방)
5. ✅ 정기적인 백업 설정

## 🆘 문제 해결

### 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
sudo lsof -i :5900
sudo lsof -i :8100

# 또는 .env.production에서 포트 변경
FRONTEND_PORT=8080
BACKEND_PORT=8200
```

### 컨테이너가 시작되지 않음
```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs backend

# 환경변수 확인
docker-compose -f docker-compose.prod.yml config
```

### 데이터베이스 연결 오류
```bash
# PostgreSQL 상태 확인
docker exec myapp-db-prod pg_isready -U postgres

# 비밀번호 확인
docker-compose -f docker-compose.prod.yml exec backend env | grep DATABASE_URL
```

## 📊 모니터링

### 리소스 사용량
```bash
docker stats
```

### 헬스체크 상태
```bash
docker inspect myapp-backend-prod | grep -A 20 Health
```

### 로그 파일
```bash
# 애플리케이션 로그
tail -f data/logs/app.log

# 에러 로그
tail -f data/logs/error.log

# 액세스 로그
tail -f data/logs/access.log
```

---

**즐거운 사용 되세요! 🎉**
