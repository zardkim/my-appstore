# 내부 IP 주소 로그인 문제 해결 계획서

**작성일**: 2025-12-29
**문제**: 192.168.0.8:5900에서 로그인 페이지는 표시되지만 로그인 실패
**백엔드 상태**: 정상 (health check, setup check 모두 정상 응답)

---

## 1. 현황 분석

### ✅ 정상 작동하는 것
- 백엔드 API 서버: `http://192.168.0.8:8100` 정상 응답
- Health Check: `/health` 엔드포인트 정상
- Setup Check: `/api/auth/check-setup` 정상
- 방화벽 설정: 5900, 8100 포트 허용됨
- CORS 설정: `*` (모든 origin 허용)

### ❌ 문제가 있는 것
- 모바일에서 192.168.0.8:5900 접속 시 로그인 실패
- localhost:5900에서는 정상 로그인 가능

### 🔍 원인 분석

**가능성 1: 프론트엔드 환경 변수 미적용**
- `frontend/.env.local`은 개발 서버 시작 시에만 로드됨
- 코드 변경 (`client.js`, `env.js`) 후 브라우저 캐시 미갱신
- Vite 개발 서버가 변경사항을 HMR(Hot Module Replacement)로 적용했지만 모바일 브라우저에서 캐시 문제

**가능성 2: API URL 동적 생성 로직 미작동**
- `client.js`와 `env.js`의 동적 URL 생성 함수가 제대로 작동하지 않음
- 모바일 브라우저에서 `window.location.hostname`이 예상과 다를 수 있음

**가능성 3: 모바일 브라우저 캐시**
- 이전 빌드의 캐시가 남아있어서 localhost로 요청
- Service Worker가 있다면 오래된 버전 서빙

---

## 2. 단계별 해결 방안

### Phase 1: 즉시 테스트 (5분)

#### Step 1-1: API 상태 페이지 확인
모바일에서 다음 URL 접속:
```
http://192.168.0.8:8100/api-status
```

**확인 사항**:
- [ ] 페이지가 정상 표시되는가?
- [ ] "로그인 테스트" 버튼을 눌러서 성공하는가?
- [ ] 서버 정보가 올바르게 표시되는가?

**결과**:
- ✅ 로그인 테스트 성공 → 백엔드는 정상, 프론트엔드 문제
- ❌ 로그인 테스트 실패 → 백엔드 설정 문제

#### Step 1-2: 모바일 브라우저 캐시 완전 삭제
모바일 브라우저에서:
1. 설정 → 개인정보 → 인터넷 사용 기록 삭제
2. "쿠키 및 사이트 데이터", "캐시된 이미지 및 파일" 체크
3. 삭제 후 브라우저 완전 종료
4. 브라우저 재실행 후 `http://192.168.0.8:5900` 접속
5. 로그인 재시도

---

### Phase 2: 프론트엔드 환경 변수 명시적 설정 (10분)

#### Step 2-1: 환경 변수 파일 직접 수정

**방법 A: 빌드 없이 동적 설정 (권장)**

현재 이미 적용된 상태:
- `frontend/src/api/client.js`: 동적 URL 생성
- `frontend/src/utils/env.js`: 동적 URL 생성

**확인 명령어**:
```bash
cd /home/nuricom/project/myappStore/frontend
grep -A 5 "getApiBaseUrl\|getBackendBaseUrl" src/api/client.js src/utils/env.js
```

**방법 B: 프론트엔드 재시작 (강제 적용)**

```bash
cd /home/nuricom/project/myappStore/frontend

# 프론트엔드 프로세스 종료
pkill -f "vite --host"

# 재시작
npm run dev
```

#### Step 2-2: 빌드 버전으로 테스트

동적 URL이 작동하지 않을 경우를 대비한 정적 빌드:

```bash
cd /home/nuricom/project/myappStore/frontend

# 환경 변수를 상대 경로로 설정 (빌드 시)
cat > .env.production << 'EOF'
VITE_API_BASE_URL=/api
VITE_BACKEND_URL=
VITE_APP_URL=
EOF

# 프로덕션 빌드
npm run build

# Nginx 또는 간단한 HTTP 서버로 dist 서빙
# (이 경우 역방향 프록시 설정 필요)
```

---

### Phase 3: 네트워크 라우팅 확인 (5분)

#### Step 3-1: 서버에서 내부 IP 확인

```bash
# 실제 내부 IP 주소 확인
hostname -I

# 또는
ip addr show
```

만약 192.168.0.8이 아니라면, 정확한 IP를 확인하고 수정 필요

#### Step 3-2: 동일 네트워크 확인

모바일 기기가 같은 Wi-Fi 네트워크에 연결되어 있는지 확인:
- 서버와 모바일이 같은 공유기에 연결되어 있어야 함
- VPN 사용 중이면 비활성화

---

### Phase 4: 디버깅 정보 수집 (10분)

#### Step 4-1: 프론트엔드 디버깅 페이지 추가

프론트엔드에 디버그 정보를 표시하는 페이지 생성:

**파일**: `frontend/public/debug.html` (생성 예정)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Debug Info</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>디버그 정보</h1>
    <div id="info"></div>
    <script>
        const info = {
            hostname: window.location.hostname,
            protocol: window.location.protocol,
            port: window.location.port,
            href: window.location.href,
            userAgent: navigator.userAgent,
            apiUrl: window.location.protocol + '//' + window.location.hostname + ':8100/api'
        };
        document.getElementById('info').innerHTML =
            '<pre>' + JSON.stringify(info, null, 2) + '</pre>';
    </script>
</body>
</html>
```

모바일에서 `http://192.168.0.8:5900/debug.html` 접속 후 정보 확인

#### Step 4-2: 백엔드 로그 실시간 모니터링

```bash
# 백엔드 로그를 파일로 저장하면서 실시간 확인
cd /home/nuricom/project/myappStore/backend

# 기존 백엔드 종료
pkill -f "uvicorn app.main:app"

# 로그 파일에 저장하면서 실행
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload > /tmp/backend-debug.log 2>&1 &

# 로그 실시간 확인
tail -f /tmp/backend-debug.log
```

모바일에서 로그인 시도 시 로그에 요청이 들어오는지 확인

---

### Phase 5: 근본적인 해결 (30분)

#### Option A: Nginx 역방향 프록시 사용 (권장)

**장점**:
- 프론트엔드와 백엔드가 같은 포트 사용 (CORS 문제 완전 해결)
- 프로덕션 환경에 적합
- HTTPS 설정 가능

**구현**:

1. Nginx 설치 (이미 설치되어 있음)

2. 설정 파일 생성: `/etc/nginx/sites-available/myappstore`

```nginx
server {
    listen 80;
    server_name 192.168.0.8 localhost;

    # 프론트엔드 (개발 서버 프록시)
    location / {
        proxy_pass http://localhost:5900;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 백엔드 API
    location /api/ {
        proxy_pass http://localhost:8100/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 백엔드 정적 파일
    location /static/ {
        proxy_pass http://localhost:8100/static/;
    }

    # API 상태 페이지
    location /api-status {
        proxy_pass http://localhost:8100/api-status;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8100/health;
    }
}
```

3. 심볼릭 링크 생성 및 Nginx 재시작

```bash
sudo ln -s /etc/nginx/sites-available/myappstore /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. 프론트엔드 환경 변수 수정

```bash
# frontend/.env.local
VITE_API_BASE_URL=/api
VITE_BACKEND_URL=
VITE_APP_URL=http://192.168.0.8
```

5. 접속
- `http://192.168.0.8` (포트 80, 생략 가능)

#### Option B: Docker Compose로 통합 (최종 솔루션)

**장점**:
- 배포 간편
- 환경 독립적
- 네트워크 격리

**구현**:

1. `docker-compose.yml` 확인 (이미 있음)

2. `.env` 파일 생성

```bash
# .env
VITE_API_BASE_URL=http://192.168.0.8:8100/api
VITE_BACKEND_URL=http://192.168.0.8:8100
VITE_APP_URL=http://192.168.0.8:5900
CORS_ORIGINS=*
```

3. Docker Compose로 실행

```bash
cd /home/nuricom/project/myappStore

# 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f
```

4. 접속
- 프론트엔드: `http://192.168.0.8:5900`
- 백엔드: `http://192.168.0.8:8100`

---

## 3. 체크리스트

### 즉시 확인 사항
- [ ] `http://192.168.0.8:8100/api-status` 접속 확인
- [ ] API 상태 페이지에서 "로그인 테스트" 성공 확인
- [ ] 모바일 브라우저 캐시 완전 삭제
- [ ] 프론트엔드 재시작
- [ ] 모바일에서 로그인 재시도

### 환경 설정 확인
- [ ] `backend/.env`의 `CORS_ORIGINS=*` 확인
- [ ] 방화벽 5900, 8100 포트 허용 확인
- [ ] 서버 내부 IP 주소 확인 (192.168.0.8이 맞는지)
- [ ] 모바일과 서버가 같은 네트워크에 있는지 확인

### 코드 수정 확인
- [ ] `frontend/src/api/client.js` 동적 URL 생성 함수 확인
- [ ] `frontend/src/utils/env.js` 동적 URL 생성 함수 확인

### 장기적 해결 방안
- [ ] Nginx 역방향 프록시 설정 고려
- [ ] Docker Compose로 통합 배포 고려
- [ ] HTTPS 설정 고려 (Let's Encrypt)

---

## 4. 예상 결과

### 시나리오 1: 캐시 문제
**증상**: API 상태 페이지에서는 로그인 성공, 프론트엔드에서는 실패
**해결**: 브라우저 캐시 삭제 → 로그인 성공

### 시나리오 2: 동적 URL 미작동
**증상**: API 요청이 localhost:8100으로 가고 있음
**해결**: 프론트엔드 재시작 또는 빌드 → 로그인 성공

### 시나리오 3: CORS 문제 (가능성 낮음)
**증상**: API 상태 페이지에서도 CORS 오류
**해결**: CORS_ORIGINS 재확인 및 백엔드 재시작

### 시나리오 4: 네트워크 격리
**증상**: 아무것도 안 됨 (health check도 안 됨)
**해결**: 방화벽, VPN, 네트워크 설정 확인

---

## 5. 권장 최종 솔루션

**단기 (개발 환경)**:
1. API 상태 페이지로 백엔드 확인
2. 브라우저 캐시 삭제
3. 프론트엔드 동적 URL 생성 로직 사용 (이미 적용됨)

**중기 (내부 NAS 사용)**:
1. Nginx 역방향 프록시 설정
2. 포트 80으로 통합 접속
3. 환경 변수를 상대 경로로 변경

**장기 (프로덕션)**:
1. Docker Compose로 배포
2. Nginx + Let's Encrypt로 HTTPS 설정
3. Synology 역방향 프록시 또는 NPM 사용

---

## 6. 트러블슈팅 참고

### 로그 위치
- 백엔드: `/tmp/backend-debug.log`
- 프론트엔드: 브라우저 콘솔 (F12)
- Nginx: `/var/log/nginx/error.log`, `/var/log/nginx/access.log`

### 유용한 명령어

```bash
# 백엔드 상태 확인
curl http://192.168.0.8:8100/health

# 프론트엔드 프로세스 확인
ps aux | grep vite

# 방화벽 상태 확인
sudo ufw status

# 포트 리스닝 확인
netstat -tuln | grep -E '5900|8100'

# CORS 설정 확인
curl -s http://192.168.0.8:8100/debug-cors
```

### 연락처 정보
문제가 계속되면 다음 정보를 수집해주세요:
1. API 상태 페이지 스크린샷
2. 모바일 브라우저에서의 오류 메시지
3. 백엔드 로그 마지막 50줄
4. 서버 내부 IP 주소 (`hostname -I` 결과)

---

**다음 단계**: Phase 1 즉시 테스트부터 시작하세요!
