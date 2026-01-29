# 리버스 프록시 설정 가이드

## 문제 상황

HTTPS 사이트에서 아이콘 및 정적 파일이 404 오류로 표시되지 않는 문제:
```
GET https://app.nuripc.kr/static/icons/1.png 404 (Not Found)
```

## 원인

프론트엔드는 HTTPS로 제공되지만, 백엔드의 정적 파일 경로(`/static`)가 프록시되지 않아 접근 불가

## 해결 방법

### 시놀로지 Reverse Proxy 설정

1. **제어판 → 로그인 포털 → 고급 → 리버스 프록시**로 이동

2. 기존 규칙 편집 또는 새 규칙 생성

#### 프론트엔드 규칙
- **설명**: MyApp Store Frontend
- **소스**:
  - 프로토콜: HTTPS
  - 호스트 이름: app.nuripc.kr
  - 포트: 443
  - HSTS 활성화: ✓
- **대상**:
  - 프로토콜: HTTP
  - 호스트 이름: localhost
  - 포트: 5900

#### 백엔드 API 규칙 (추가 필요)
- **설명**: MyApp Store Backend API
- **소스**:
  - 프로토콜: HTTPS
  - 호스트 이름: app.nuripc.kr
  - 포트: 443
  - 경로: /api
- **대상**:
  - 프로토콜: HTTP
  - 호스트 이름: localhost
  - 포트: 8110
  - 경로: /api

#### 백엔드 정적 파일 규칙 (추가 필요) ⭐ 중요!
- **설명**: MyApp Store Backend Static Files
- **소스**:
  - 프로토콜: HTTPS
  - 호스트 이름: app.nuripc.kr
  - 포트: 443
  - 경로: /static
- **대상**:
  - 프로토콜: HTTP
  - 호스트 이름: localhost
  - 포트: 8110
  - 경로: /static

#### WebSocket 지원 (선택)
각 규칙의 "사용자 정의 헤더" 탭에서:
```
Upgrade: $http_upgrade
Connection: $connection_upgrade
```

### 규칙 우선순위

시놀로지 리버스 프록시는 **위에서 아래로** 매칭되므로 순서가 중요합니다:

1. `/static` (가장 구체적)
2. `/api` (구체적)
3. `/` (가장 일반적, 프론트엔드)

### 테스트

설정 후 브라우저에서 확인:
```
https://app.nuripc.kr/static/icons/1.png
https://app.nuripc.kr/api/version
https://app.nuripc.kr/
```

모두 정상적으로 로드되어야 합니다.

---

## 대체 방법: Nginx 직접 설정

시놀로지 리버스 프록시 대신 커스텀 Nginx 설정을 사용하는 경우:

### nginx.conf 예제

```nginx
server {
    listen 443 ssl http2;
    server_name app.nuripc.kr;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 프론트엔드
    location / {
        proxy_pass http://localhost:5900;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 백엔드 API
    location /api {
        proxy_pass http://localhost:8110;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS (필요시)
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }

    # 백엔드 정적 파일 (아이콘, 스크린샷 등)
    location /static {
        proxy_pass http://localhost:8110;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 캐싱 (선택)
        proxy_cache_valid 200 1d;
        proxy_cache_bypass $http_pragma $http_authorization;
        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

### 설정 적용

```bash
# Nginx 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl reload nginx
```

---

## 확인 사항

### 1. 포트 접근 가능 여부 확인
```bash
# 백엔드 포트 확인
curl http://localhost:8110/api/version

# 프론트엔드 포트 확인
curl http://localhost:5900
```

### 2. 방화벽 설정
- 시놀로지 방화벽에서 443 포트 허용
- Docker 컨테이너 포트 매핑 확인 (5900, 8110)

### 3. 브라우저 캐시 삭제
리버스 프록시 설정 후 브라우저 캐시를 삭제하고 새로고침 (Ctrl+Shift+R)

---

## 트러블슈팅

### 404 오류 지속
1. 리버스 프록시 규칙 순서 확인
2. 백엔드 컨테이너 로그 확인: `docker logs myapp-backend`
3. Nginx 로그 확인: `/var/log/nginx/error.log`

### Mixed Content 경고
- 모든 리소스가 HTTPS로 제공되는지 확인
- 브라우저 개발자 도구 Console 탭에서 오류 확인

### 파일 업로드/다운로드 실패
```nginx
# Nginx에 큰 파일 업로드 허용
client_max_body_size 1G;
proxy_request_buffering off;
```

---

## 참고

- 시놀로지 DSM 리버스 프록시 가이드: https://kb.synology.com/
- Nginx 공식 문서: https://nginx.org/en/docs/
