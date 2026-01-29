# 네트워크 설정 가이드

MyApp Store를 로컬 네트워크(LAN)나 역방향 프록시를 통해 접속하기 위한 설정 가이드입니다.

## 1. 로컬 네트워크(LAN) 접속 설정

### 현재 설정 확인
```bash
# 현재 서버의 IP 주소 확인
ip addr show
# 또는
hostname -I
```

### 백엔드 설정 (docker-compose.yml)

```yaml
backend:
  environment:
    # CORS 설정 - 모든 origin 허용 (내부 네트워크용)
    - CORS_ORIGINS=*

    # 또는 특정 IP만 허용
    # - CORS_ORIGINS=http://192.168.0.8:5900,http://192.168.0.10:5900,http://nas.local:5900

    # 서버는 모든 인터페이스에서 수신
    - HOST=0.0.0.0
    - PORT=8110
```

### 프론트엔드 설정 (frontend/.env.local)

```bash
# 개발 환경 - 실제 IP 주소 사용
VITE_API_BASE_URL=http://192.168.0.8:8110/api
VITE_BACKEND_URL=http://192.168.0.8:8110
VITE_APP_URL=http://192.168.0.8:5900
```

**중요**: 프론트엔드 `.env.local` 파일 수정 후 반드시 재시작해야 합니다.
```bash
cd frontend
npm run dev
```

### 접속 방법
- 같은 네트워크의 다른 기기에서: `http://192.168.0.8:5900`
- 호스트 이름 사용 (설정된 경우): `http://nas.local:5900`

## 2. 역방향 프록시(Reverse Proxy) 설정

### Nginx Proxy Manager (NPM) 사용 시

1. **NPM에서 Proxy Host 추가**
   - Domain Names: `myapp.example.com`
   - Scheme: `http`
   - Forward Hostname/IP: `myapp-frontend` (Docker 컨테이너 이름) 또는 `192.168.0.8`
   - Forward Port: `5900`
   - SSL 인증서 발급 (Let's Encrypt 권장)

2. **백엔드 CORS 설정**
   ```yaml
   backend:
     environment:
       - CORS_ORIGINS=https://myapp.example.com
   ```

3. **프론트엔드 설정 업데이트**
   - 웹 UI의 "설정 > 일반설정 > 네트워크 설정"에서:
     - 프론트엔드 접속 URL: `https://myapp.example.com`
     - 백엔드 API URL: `https://myapp.example.com/api`
     - 추가 허용 도메인: `https://myapp.example.com`

### Synology DSM 역방향 프록시 사용 시

1. **DSM > 제어판 > 응용 프로그램 포털 > 역방향 프록시**

2. **프론트엔드 프록시 규칙 생성**
   - 소스:
     - 프로토콜: HTTPS
     - 호스트 이름: myapp.your-nas.synology.me
     - 포트: 443
   - 대상:
     - 프로토콜: HTTP
     - 호스트 이름: localhost
     - 포트: 5900

3. **백엔드 프록시 규칙 생성** (선택사항)
   - 소스:
     - 프로토콜: HTTPS
     - 호스트 이름: myapp-api.your-nas.synology.me
     - 포트: 443
   - 대상:
     - 프로토콜: HTTP
     - 호스트 이름: localhost
     - 포트: 8110

4. **CORS 설정**
   ```yaml
   backend:
     environment:
       - CORS_ORIGINS=https://myapp.your-nas.synology.me
   ```

## 3. Docker 네트워크 설정

### 포트 바인딩 확인
```yaml
services:
  backend:
    ports:
      - "8110:8110"  # 호스트:컨테이너

  frontend:
    ports:
      - "5900:5900"
```

### 방화벽 설정
```bash
# UFW 사용 시
sudo ufw allow 5900/tcp
sudo ufw allow 8110/tcp

# firewalld 사용 시
sudo firewall-cmd --permanent --add-port=5900/tcp
sudo firewall-cmd --permanent --add-port=8110/tcp
sudo firewall-cmd --reload
```

## 4. 웹 UI에서 설정 관리

**설정 > 일반설정 > 네트워크 설정**에서 다음 항목을 설정할 수 있습니다:

1. **프론트엔드 접속 URL**
   - 예: `http://192.168.0.8:5900`, `https://myapp.example.com`

2. **백엔드 API URL**
   - 예: `http://192.168.0.8:8110`, `https://myapp.example.com/api`

3. **추가 허용 도메인 (CORS)**
   - 역방향 프록시 사용 시 HTTPS URL 추가
   - 한 줄에 하나씩 입력

**참고**: 웹 UI 설정은 참고용이며, 실제 적용을 위해서는 환경 변수 수정 후 서비스 재시작이 필요합니다.

## 5. 문제 해결

### CORS 오류가 발생하는 경우
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**해결 방법**:
1. 백엔드 로그에서 CORS 설정 확인:
   ```bash
   docker logs myapp-backend | grep CORS
   ```

2. `docker-compose.yml`의 `CORS_ORIGINS` 환경 변수에 접속 URL 추가

3. 컨테이너 재시작:
   ```bash
   docker-compose restart backend
   ```

### API 요청이 실패하는 경우

1. **네트워크 연결 확인**:
   ```bash
   curl http://192.168.0.8:8110/health
   ```

2. **프론트엔드 환경 변수 확인**:
   - `frontend/.env.local` 파일에서 `VITE_API_BASE_URL` 확인
   - 프론트엔드 재시작 필요

3. **백엔드 상태 확인**:
   ```bash
   docker-compose ps
   docker logs myapp-backend
   ```

### localhost에서는 되는데 IP 주소로는 안 되는 경우

1. **프론트엔드 `.env.local` 파일 수정**:
   ```bash
   VITE_API_BASE_URL=http://실제IP:8110/api
   ```

2. **백엔드 CORS 설정**:
   ```yaml
   - CORS_ORIGINS=http://실제IP:5900
   ```

3. **서비스 재시작**:
   ```bash
   docker-compose restart
   ```

## 6. 권장 설정

### 개발/테스트 환경
```yaml
backend:
  environment:
    - CORS_ORIGINS=*  # 모든 origin 허용
```

### 프로덕션/내부 NAS 환경
```yaml
backend:
  environment:
    # 구체적인 도메인만 허용
    - CORS_ORIGINS=http://192.168.0.8:5900,http://nas.local:5900,https://myapp.example.com
```

## 7. 체크리스트

- [ ] 서버 IP 주소 확인
- [ ] `docker-compose.yml`의 `CORS_ORIGINS` 설정
- [ ] `frontend/.env.local` 파일 업데이트
- [ ] Docker 컨테이너 재시작
- [ ] 방화벽 포트 허용 (필요한 경우)
- [ ] 역방향 프록시 설정 (HTTPS 사용 시)
- [ ] 웹 UI에서 네트워크 설정 확인
- [ ] 다른 기기에서 접속 테스트

## 8. 참고 자료

- [FastAPI CORS 가이드](https://fastapi.tiangolo.com/tutorial/cors/)
- [Nginx Proxy Manager 문서](https://nginxproxymanager.com/)
- [Synology DSM 역방향 프록시](https://kb.synology.com/en-us/DSM/help/DSM/AdminCenter/application_appportalias)
