# Synology NAS Docker 설치 가이드

이 문서는 Synology NAS에서 MyApp Store를 Docker를 통해 설치하고 실행하는 방법을 안내합니다.

## 목차
1. [사전 요구사항](#사전-요구사항)
2. [설치 준비](#설치-준비)
3. [Docker Compose 설치](#docker-compose-설치)
4. [환경 설정](#환경-설정)
5. [빌드 및 실행](#빌드-및-실행)
6. [데이터베이스 초기화](#데이터베이스-초기화)
7. [접속 및 테스트](#접속-및-테스트)
8. [NAS 소프트웨어 폴더 연동](#nas-소프트웨어-폴더-연동)
9. [문제 해결](#문제-해결)

---

## 사전 요구사항

### 1. Synology NAS 요구사항
- DSM 7.0 이상
- Docker 패키지 설치됨
- 최소 2GB RAM (권장 4GB 이상)
- 최소 10GB 여유 공간

### 2. 필수 패키지 설치
Synology 패키지 센터에서 다음 패키지를 설치하세요:

1. **Docker** - Container Manager
2. **Git Server** (선택사항, 코드 업데이트용)

설치 방법:
- `패키지 센터` → `모두` → `Docker` 검색 → 설치
- 또는 `Container Manager` 검색 → 설치

---

## 설치 준비

### 1. SSH 접속 활성화

**DSM 설정:**
1. `제어판` → `터미널 및 SNMP`
2. `터미널` 탭에서 `SSH 서비스 활성화` 체크
3. 포트: 기본값 22 (또는 보안을 위해 변경)
4. `적용` 클릭

**SSH 접속:**
```bash
# Windows: PowerShell 또는 PuTTY 사용
# Mac/Linux: 터미널 사용
ssh admin@YOUR_NAS_IP

# 예시
ssh admin@192.168.0.100
```

### 2. 프로젝트 디렉토리 생성

SSH 접속 후:
```bash
# Docker 프로젝트 디렉토리 생성
sudo mkdir -p /volume1/docker/myappstore
cd /volume1/docker/myappstore

# 권한 설정
sudo chown -R $(whoami):users /volume1/docker/myappstore
```

### 3. 프로젝트 파일 업로드

**방법 1: Git 사용 (권장)**
```bash
cd /volume1/docker/myappstore
git clone https://github.com/zardkim/my-appstore.git .
```

**방법 2: File Station 사용**
1. DSM에서 `File Station` 열기
2. `docker/myappstore` 폴더로 이동
3. 로컬에서 프로젝트 파일을 압축 (zip)
4. 압축 파일을 업로드하고 압축 해제

**방법 3: SFTP 사용**
- FileZilla, WinSCP 등의 SFTP 클라이언트 사용
- 호스트: NAS IP 주소
- 포트: 22
- 사용자: admin
- 디렉토리: `/volume1/docker/myappstore`

---

## Docker Compose 설치

Synology Docker에는 기본적으로 Docker Compose가 포함되어 있지 않습니다.

### 설치 방법

```bash
# Docker Compose 다운로드 (v2.24.0)
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 실행 권한 부여
sudo chmod +x /usr/local/bin/docker-compose

# 설치 확인
docker-compose --version
```

출력 예시:
```
Docker Compose version v2.24.0
```

---

## 환경 설정

### 1. 환경 변수 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다:

```bash
cd /volume1/docker/myappstore
nano .env
```

`.env` 파일 내용:
```bash
# 보안 키 (반드시 변경하세요!)
SECRET_KEY=your-very-secure-secret-key-change-this-123456

# OpenAI API 키 (선택사항, AI 메타데이터 생성용)
OPENAI_API_KEY=sk-your-openai-api-key

# NAS IP 주소 (자신의 NAS IP로 변경)
NAS_IP=192.168.0.100

# API 및 프론트엔드 URL 설정
VITE_API_BASE_URL=http://${NAS_IP}:8100/api
VITE_BACKEND_URL=http://${NAS_IP}:8100
VITE_APP_URL=http://${NAS_IP}:5900
```

**저장 방법 (nano):**
- `Ctrl + O` (저장)
- `Enter` (파일명 확인)
- `Ctrl + X` (종료)

### 2. docker-compose.yml 수정 (선택사항)

NAS의 기존 소프트웨어 폴더를 연동하려면:

```bash
nano docker-compose.yml
```

63번 줄 근처의 주석을 해제하고 경로를 수정:
```yaml
volumes:
  - ./backend:/app
  - ./data/icons:/app/static/icons
  - ./data/library:/library
  - ./data:/app/data
  # NAS 소프트웨어 폴더 연동 (읽기 전용)
  - /volume1/Software:/library/NAS:ro  # 이 줄의 주석 해제 및 경로 수정
```

---

## 빌드 및 실행

### 1. 데이터 디렉토리 생성

```bash
# 프로젝트 루트에서
mkdir -p data/db/postgres_data
mkdir -p data/redis
mkdir -p data/icons
mkdir -p data/screenshots
mkdir -p data/library
mkdir -p data/logs/postgresql

# 권한 설정
chmod -R 755 data
```

### 2. Docker 이미지 빌드

```bash
# 프로젝트 루트에서
docker-compose build

# 또는 캐시 없이 빌드 (문제 발생 시)
docker-compose build --no-cache
```

빌드 시간: 약 5-10분 소요 (NAS 성능에 따라 다름)

### 3. 컨테이너 시작

```bash
# 백그라운드에서 실행
docker-compose up -d

# 로그 확인 (실시간)
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. 컨테이너 상태 확인

```bash
docker-compose ps
```

정상 출력 예시:
```
NAME              IMAGE                    STATUS         PORTS
myapp-backend     myappstore_backend       Up 2 minutes   0.0.0.0:8100->8100/tcp
myapp-db          postgres:15-alpine       Up 2 minutes   0.0.0.0:5432->5432/tcp
myapp-frontend    myappstore_frontend      Up 2 minutes   0.0.0.0:5900->5900/tcp
myapp-redis       redis:7-alpine           Up 2 minutes   0.0.0.0:6379->6379/tcp
```

---

## 데이터베이스 초기화

### 1. 데이터베이스 마이그레이션

```bash
# 백엔드 컨테이너 접속
docker exec -it myapp-backend /bin/sh

# 컨테이너 내부에서
alembic upgrade head

# 종료
exit
```

### 2. 초기 관리자 계정 생성

웹 브라우저에서 처음 접속하면 자동으로 설정 페이지로 리다이렉트됩니다.

---

## 접속 및 테스트

### 1. 서비스 접속

**프론트엔드:**
```
http://YOUR_NAS_IP:5900
예: http://192.168.0.100:5900
```

**백엔드 API (헬스체크):**
```
http://YOUR_NAS_IP:8100/api/health
예: http://192.168.0.100:8100/api/health
```

**API 문서 (Swagger):**
```
http://YOUR_NAS_IP:8100/docs
```

### 2. 초기 설정

1. 웹 브라우저에서 `http://YOUR_NAS_IP:5900` 접속
2. 자동으로 `/setup` 페이지로 이동
3. 관리자 계정 생성:
   - 사용자명: admin (또는 원하는 이름)
   - 비밀번호: 안전한 비밀번호 입력
4. `계정 생성` 클릭
5. 로그인 페이지로 이동하여 로그인

### 3. 기본 테스트 시나리오

#### 테스트 1: 수동 스캔
1. 관리자로 로그인
2. `관리자` 메뉴 선택
3. `스캔` 탭에서 스캔 경로 설정: `/library`
4. `스캔 시작` 클릭
5. 스캔 결과 확인

#### 테스트 2: 제품 조회
1. `스토어` 메뉴 선택
2. 스캔된 제품 목록 확인
3. 제품 클릭하여 상세 정보 확인

#### 테스트 3: 설정
1. `설정` 메뉴 선택
2. 카테고리 관리
3. 일반 설정 (언어 변경)

---

## NAS 소프트웨어 폴더 연동

### 1. 기존 소프트웨어 폴더 연동

Synology NAS에 이미 소프트웨어가 저장되어 있는 경우:

```bash
# docker-compose.yml 수정
nano docker-compose.yml
```

backend 서비스의 volumes 섹션에 추가:
```yaml
volumes:
  - ./backend:/app
  - ./data/icons:/app/static/icons
  - ./data/library:/library
  - ./data:/app/data
  # 기존 소프트웨어 폴더 연동 (읽기 전용)
  - /volume1/Software:/library/NAS:ro
```

### 2. 컨테이너 재시작

```bash
docker-compose down
docker-compose up -d
```

### 3. NAS 폴더 스캔

1. 웹 UI → `관리자` → `스캔`
2. 스캔 경로: `/library/NAS`
3. `스캔 시작` 클릭

---

## 문제 해결

### 컨테이너가 시작되지 않는 경우

```bash
# 로그 확인
docker-compose logs

# 특정 서비스 로그
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 컨테이너 재시작
docker-compose restart

# 완전히 재시작 (데이터 유지)
docker-compose down
docker-compose up -d
```

### 포트 충돌 해결

기본 포트가 이미 사용 중인 경우 `docker-compose.yml`에서 포트 변경:

```yaml
# 예: 프론트엔드 포트 변경
ports:
  - "5901:5900"  # 5900 대신 5901 사용
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 컨테이너 상태 확인
docker-compose ps db

# PostgreSQL 로그 확인
docker-compose logs db

# 데이터베이스 재시작
docker-compose restart db
```

### 권한 오류

```bash
# 데이터 폴더 권한 재설정
sudo chown -R 999:999 data/db/postgres_data
sudo chmod -R 755 data
```

### 빌드 오류

```bash
# 캐시 없이 재빌드
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 메모리 부족

Synology NAS의 메모리가 부족한 경우:

1. DSM → `리소스 모니터` → 메모리 사용량 확인
2. 다른 서비스 중지
3. Docker 메모리 제한 설정:

```yaml
# docker-compose.yml에 추가
services:
  backend:
    mem_limit: 512m
  frontend:
    mem_limit: 512m
```

### 네트워크 접속 불가

1. **방화벽 확인:**
   - DSM → `제어판` → `보안` → `방화벽`
   - 포트 5900, 8100 허용

2. **Docker 네트워크 재생성:**
   ```bash
   docker-compose down
   docker network prune
   docker-compose up -d
   ```

---

## 유용한 명령어

### Docker Compose 명령어

```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart

# 로그 실시간 확인
docker-compose logs -f

# 특정 서비스만 재시작
docker-compose restart backend

# 컨테이너 상태 확인
docker-compose ps

# 리소스 사용량 확인
docker stats
```

### 데이터베이스 명령어

```bash
# PostgreSQL 접속
docker exec -it myapp-db psql -U postgres -d myappstore

# 백업
docker exec myapp-db pg_dump -U postgres myappstore > backup.sql

# 복원
docker exec -i myapp-db psql -U postgres myappstore < backup.sql
```

### 컨테이너 관리

```bash
# 컨테이너 접속
docker exec -it myapp-backend /bin/sh
docker exec -it myapp-frontend /bin/sh

# 컨테이너 리소스 확인
docker stats myapp-backend myapp-frontend

# 미사용 리소스 정리
docker system prune -a
```

---

## 업데이트

### 코드 업데이트

```bash
cd /volume1/docker/myappstore

# Git 업데이트
git pull origin main

# 컨테이너 재빌드 및 재시작
docker-compose down
docker-compose build
docker-compose up -d

# 마이그레이션 실행
docker exec -it myapp-backend alembic upgrade head
```

---

## 백업 및 복원

### 백업

```bash
# 전체 백업 스크립트
#!/bin/bash
BACKUP_DIR="/volume1/docker/myappstore_backup_$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 데이터베이스 백업
docker exec myapp-db pg_dump -U postgres myappstore > $BACKUP_DIR/database.sql

# 데이터 폴더 백업
cp -r /volume1/docker/myappstore/data $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

### 복원

```bash
# 데이터베이스 복원
docker exec -i myapp-db psql -U postgres myappstore < backup/database.sql

# 데이터 폴더 복원
cp -r backup/data/* /volume1/docker/myappstore/data/
```

---

## 성능 최적화

### 1. Redis 메모리 제한 설정

```yaml
# docker-compose.yml
redis:
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### 2. PostgreSQL 튜닝

```yaml
# docker-compose.yml
db:
  command:
    - "postgres"
    - "-c"
    - "shared_buffers=256MB"
    - "-c"
    - "effective_cache_size=1GB"
```

### 3. 로그 로테이션

```bash
# /volume1/docker/myappstore/docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 보안 권장사항

1. **기본 비밀번호 변경**
   - `.env` 파일의 `SECRET_KEY` 변경
   - PostgreSQL 비밀번호 변경

2. **HTTPS 설정**
   - Synology Reverse Proxy 사용
   - Let's Encrypt 인증서 적용

3. **방화벽 설정**
   - 외부 접속이 필요한 경우만 포트 개방
   - 내부 네트워크 전용 권장

4. **정기 백업**
   - 주간 자동 백업 설정
   - Hyper Backup 활용

---

## 추가 리소스

- **프로젝트 GitHub**: https://github.com/zardkim/my-appstore
- **이슈 리포트**: https://github.com/zardkim/my-appstore/issues
- **CLAUDE.md**: 프로젝트 아키텍처 및 개발 가이드
- **QUICKSTART.md**: 빠른 시작 가이드

---

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
