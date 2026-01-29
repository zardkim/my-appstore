# MyApp Store - 프로덕션 빌드 및 배포 가이드

## 📋 목차

1. [사전 준비](#사전-준비)
2. [환경 설정](#환경-설정)
3. [프로덕션 빌드](#프로덕션-빌드)
4. [배포 및 실행](#배포-및-실행)
5. [헬스체크 및 모니터링](#헬스체크-및-모니터링)
6. [트러블슈팅](#트러블슈팅)

---

## 사전 준비

### 필수 소프트웨어

- **Docker**: 20.10 이상
- **Docker Compose**: 2.0 이상
- **Git**: 2.0 이상 (선택사항)

### 시스템 요구사항

- **CPU**: 2 코어 이상 권장
- **메모리**: 4GB 이상 권장
- **디스크**: 20GB 이상 여유 공간
- **포트**: 5900 (프론트엔드), 8110 (백엔드), 5432 (PostgreSQL), 6379 (Redis)

---

## 환경 설정

### 1. 환경변수 파일 생성

프로덕션 환경변수 예제 파일을 복사하여 실제 환경변수 파일을 생성합니다:

```bash
cp .env.production.example .env.production
```

### 2. 환경변수 설정

`.env.production` 파일을 편집하여 실제 값을 입력합니다:

```bash
nano .env.production
```

#### 필수 변경 항목

**⚠️ 보안**: 다음 항목들은 반드시 변경해야 합니다!

1. **SECRET_KEY** - JWT 토큰 서명에 사용되는 비밀 키
   ```bash
   # 강력한 SECRET_KEY 생성
   openssl rand -hex 32
   ```
   생성된 값을 `SECRET_KEY`에 설정

2. **POSTGRES_PASSWORD** - PostgreSQL 데이터베이스 비밀번호
   ```
   POSTGRES_PASSWORD=your-strong-password-here
   ```

3. **REDIS_PASSWORD** - Redis 비밀번호 (선택사항이지만 권장)
   ```
   REDIS_PASSWORD=your-redis-password-here
   ```

4. **CORS_ORIGINS** - 허용할 프론트엔드 도메인
   ```
   # 예시: 실제 서버 IP로 변경
   CORS_ORIGINS=http://192.168.0.8:5900,http://your-domain.com:5900
   ```

5. **VITE 환경변수** - 프론트엔드에서 백엔드 접근 URL
   ```
   VITE_API_BASE_URL=http://your-server-ip:8110/api
   VITE_BACKEND_URL=http://your-server-ip:8110
   VITE_APP_URL=http://your-server-ip:5900
   ```

#### 선택 항목

- **OPENAI_API_KEY**: AI 메타데이터 자동 생성을 사용하려면 설정
- **LOG_LEVEL**: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### 3. 디렉토리 구조 확인

필요한 데이터 디렉토리가 존재하는지 확인합니다:

```bash
mkdir -p data/{db,logs,icons,screenshots,eximage,library,config}
mkdir -p data/logs/postgresql
```

---

## 프로덕션 빌드

### 1. 이미지 빌드

프로덕션 Docker 이미지를 빌드합니다:

```bash
# 환경변수 파일을 사용하여 빌드
docker-compose -f docker-compose.prod.yml --env-file .env.production build

# 또는 캐시 없이 빌드 (깨끗한 빌드)
docker-compose -f docker-compose.prod.yml --env-file .env.production build --no-cache
```

빌드 시간: 첫 빌드는 5-10분 소요 (인터넷 속도에 따라 다름)

### 2. 빌드 확인

빌드된 이미지 확인:

```bash
docker images | grep myappstore
```

출력 예시:
```
myappstore-backend   latest   abc123def456   5 minutes ago   250MB
myappstore-frontend  latest   def456ghi789   3 minutes ago   50MB
```

---

## 배포 및 실행

### 1. 컨테이너 실행

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

옵션 설명:
- `-f docker-compose.prod.yml`: 프로덕션 설정 파일 사용
- `--env-file .env.production`: 환경변수 파일 지정
- `-d`: 백그라운드 실행 (detached mode)

### 2. 실행 확인

컨테이너 상태 확인:

```bash
docker-compose -f docker-compose.prod.yml ps
```

정상 실행 시 출력:
```
NAME                    STATUS              PORTS
myapp-backend-prod      Up (healthy)        0.0.0.0:8110->8110/tcp
myapp-frontend-prod     Up (healthy)        0.0.0.0:80->80/tcp
myapp-db-prod           Up (healthy)        0.0.0.0:5432->5432/tcp
myapp-redis-prod        Up (healthy)        0.0.0.0:6379->6379/tcp
```

### 3. 로그 확인

전체 로그 확인:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

특정 서비스 로그만 확인:
```bash
# 백엔드 로그
docker-compose -f docker-compose.prod.yml logs -f backend

# 프론트엔드 로그
docker-compose -f docker-compose.prod.yml logs -f frontend

# 데이터베이스 로그
docker-compose -f docker-compose.prod.yml logs -f db
```

---

## 헬스체크 및 모니터링

### 1. 헬스체크 엔드포인트

각 서비스의 헬스체크:

```bash
# 백엔드 헬스체크
curl http://localhost:8110/health

# 프론트엔드 헬스체크
curl http://localhost:5900/

# PostgreSQL 헬스체크
docker exec myapp-db-prod pg_isready -U postgres

# Redis 헬스체크
docker exec myapp-redis-prod redis-cli ping
```

### 2. API 상태 페이지

브라우저에서 접속:
```
http://localhost:8110/api-status
```

이 페이지에서 다음을 확인할 수 있습니다:
- 서버 정보
- 접속 URL
- API 엔드포인트 테스트
- 로그인 테스트

### 3. 컨테이너 리소스 사용량

```bash
# 실시간 리소스 모니터링
docker stats

# 특정 컨테이너만 모니터링
docker stats myapp-backend-prod myapp-frontend-prod
```

### 4. 로그 파일 확인

애플리케이션 로그는 `data/logs/` 디렉토리에 저장됩니다:

```bash
# 백엔드 애플리케이션 로그
tail -f data/logs/app.log

# 에러 로그
tail -f data/logs/error.log

# 액세스 로그 (HTTP 요청)
tail -f data/logs/access.log

# PostgreSQL 로그
tail -f data/logs/postgresql/postgresql-*.log
```

---

## 운영 관리

### 1. 컨테이너 중지

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production down
```

데이터를 유지하면서 중지 (볼륨 삭제 안 함):
```bash
docker-compose -f docker-compose.prod.yml down
```

### 2. 컨테이너 재시작

```bash
# 전체 재시작
docker-compose -f docker-compose.prod.yml restart

# 특정 서비스만 재시작
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart frontend
```

### 3. 업데이트 배포

코드 변경 후 재배포:

```bash
# 1. 이미지 재빌드
docker-compose -f docker-compose.prod.yml --env-file .env.production build

# 2. 컨테이너 재시작 (다운타임 최소화)
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### 4. 데이터베이스 백업

```bash
# PostgreSQL 백업
docker exec myapp-db-prod pg_dump -U postgres myappstore > backup_$(date +%Y%m%d_%H%M%S).sql

# 백업 복원
cat backup_20260103_120000.sql | docker exec -i myapp-db-prod psql -U postgres myappstore
```

### 5. 완전 초기화 (주의!)

⚠️ **경고**: 모든 데이터가 삭제됩니다!

```bash
# 컨테이너, 볼륨, 네트워크 모두 삭제
docker-compose -f docker-compose.prod.yml down -v

# 이미지까지 삭제
docker-compose -f docker-compose.prod.yml down -v --rmi all
```

---

## 트러블슈팅

### 1. 컨테이너가 시작되지 않는 경우

```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs backend

# 일반적인 원인:
# - 환경변수 오류 (.env.production 파일 확인)
# - 포트 충돌 (8110, 80 포트가 이미 사용 중인지 확인)
# - 디스크 공간 부족
```

### 2. 데이터베이스 연결 오류

```bash
# PostgreSQL 상태 확인
docker exec myapp-db-prod pg_isready -U postgres

# 데이터베이스 로그 확인
docker-compose -f docker-compose.prod.yml logs db

# 연결 테스트
docker exec myapp-backend-prod curl -f http://db:5432
```

### 3. 프론트엔드에서 백엔드 접속 안 됨

원인: CORS 설정 또는 URL 불일치

해결:
1. `.env.production` 파일에서 `CORS_ORIGINS` 확인
2. `VITE_API_BASE_URL`이 실제 백엔드 URL과 일치하는지 확인
3. 브라우저 개발자 도구에서 네트워크 탭 확인

### 4. 헬스체크 실패

```bash
# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 헬스체크 로그 확인
docker inspect myapp-backend-prod | grep -A 20 Health

# 수동 헬스체크
curl -v http://localhost:8110/health
```

### 5. 메모리 부족 오류

```bash
# 메모리 사용량 확인
docker stats

# 불필요한 이미지/컨테이너 정리
docker system prune -a
```

---

## 성능 최적화 팁

### 1. 백엔드 워커 수 조정

`docker-compose.prod.yml`에서 uvicorn 워커 수 조정:
```yaml
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8110", "--workers", "4"]
```

권장: CPU 코어 수 × 2 + 1

### 2. 데이터베이스 커넥션 풀

`backend/app/database.py`:
```python
pool_size=10      # 기본 연결 수
max_overflow=20   # 최대 추가 연결 수
```

### 3. Redis 메모리 제한

`docker-compose.prod.yml`:
```yaml
redis:
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

---

## 보안 체크리스트

- [ ] SECRET_KEY가 강력한 랜덤 값으로 설정됨
- [ ] 데이터베이스 비밀번호가 기본값이 아님
- [ ] Redis 비밀번호가 설정됨
- [ ] CORS_ORIGINS가 실제 도메인으로 제한됨
- [ ] 방화벽에서 필요한 포트만 개방 (5900, 8110)
- [ ] 백업 스크립트가 설정됨
- [ ] 로그 파일 로테이션 설정 확인
- [ ] SSL/TLS 인증서 적용 (선택사항, Nginx 리버스 프록시 사용 시)

---

## 다음 단계

프로덕션 배포 후:

1. **초기 설정**: http://your-server-ip:5900 접속 → 관리자 계정 생성
2. **스캔 경로 설정**: 관리자 페이지에서 소프트웨어 폴더 경로 지정
3. **AI API 설정**: OpenAI API 키 입력 (선택사항)
4. **자동 스캔 설정**: 스케줄러 cron 표현식 설정 (예: `0 2 * * *`)
5. **모니터링 설정**: 로그 확인 및 알림 설정

---

## 지원 및 문의

- **GitHub Issues**: https://github.com/your-repo/issues
- **문서**: /docs 디렉토리
- **API 문서**: http://localhost:8110/docs (Swagger UI)

---

## 버전 정보

- **프로덕션 설정 버전**: 1.0.0
- **Docker Compose 버전**: 3.8
- **Python**: 3.11
- **Node.js**: 20
- **PostgreSQL**: 15
- **Redis**: 7
