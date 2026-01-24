# GitHub Actions 자동 빌드 설정 가이드

MyApp Store는 GitHub Actions를 사용하여 Docker 이미지를 자동으로 빌드하고 Docker Hub에 푸시합니다.

## 📋 사전 요구사항

- ✅ GitHub 저장소
- ✅ Docker Hub 계정 (https://hub.docker.com/)

---

## 🔐 1단계: Docker Hub 크레덴셜 생성

### 1.1 Docker Hub 접속

1. https://hub.docker.com/ 접속
2. 로그인

### 1.2 Access Token 생성

1. 우측 상단 프로필 클릭 → **Account Settings**
2. 좌측 메뉴에서 **Security** 클릭
3. **New Access Token** 클릭

**토큰 설정:**
- **Description**: `GitHub Actions MyApp Store`
- **Access permissions**: `Read, Write, Delete`

4. **Generate** 클릭
5. 생성된 토큰을 **복사** (한 번만 표시됨!)

---

## 🔑 2단계: GitHub Secrets 설정

### 2.1 GitHub 저장소 Settings 이동

1. GitHub 저장소 페이지 접속
2. **Settings** 탭 클릭
3. 좌측 메뉴에서 **Secrets and variables** → **Actions** 클릭

### 2.2 Secrets 추가

**1. DOCKER_USERNAME 추가**

1. **New repository secret** 클릭
2. **Name**: `DOCKER_USERNAME`
3. **Secret**: `zardkim` (Docker Hub 사용자명)
4. **Add secret** 클릭

**2. DOCKER_PASSWORD 추가**

1. **New repository secret** 클릭
2. **Name**: `DOCKER_PASSWORD`
3. **Secret**: 1단계에서 복사한 Access Token 붙여넣기
4. **Add secret** 클릭

### 2.3 설정 확인

**Secrets and variables** → **Actions**에 다음 항목이 있어야 합니다:
- ✅ `DOCKER_USERNAME`
- ✅ `DOCKER_PASSWORD`

---

## 🚀 3단계: GitHub Actions 워크플로우 실행

워크플로우는 다음 경우에 자동으로 실행됩니다:

### 자동 트리거

1. **main 브랜치에 푸시할 때**
   ```bash
   git push origin main
   ```
   → 버전 `1.3.0-beta`와 `latest` 태그로 빌드

2. **버전 태그를 푸시할 때**
   ```bash
   git tag v1.3.0-beta
   git push origin v1.3.0-beta
   ```
   → 태그 버전과 `latest` 태그로 빌드

### 수동 트리거

1. GitHub 저장소 → **Actions** 탭
2. 좌측에서 **Build and Push Docker Images** 워크플로우 선택
3. **Run workflow** 클릭
4. (선택사항) 버전 입력 (예: `1.3.0-beta`)
5. **Run workflow** 클릭

---

## 📊 4단계: 빌드 상태 확인

### GitHub Actions 로그 확인

1. GitHub 저장소 → **Actions** 탭
2. 최신 워크플로우 실행 클릭
3. 진행 상황 확인:
   - ✅ Checkout code
   - ✅ Set up Docker Buildx
   - ✅ Log in to Docker Hub
   - ✅ Build and push Backend image
   - ✅ Build and push Frontend image

### Docker Hub 확인

1. https://hub.docker.com/ 접속
2. **Repositories** 확인:
   - `zardkim/myappstore-backend`
   - `zardkim/myappstore-frontend`
3. 각 저장소의 **Tags** 탭에서 이미지 태그 확인:
   - `1.3.0-beta`
   - `latest`

---

## 🔧 워크플로우 상세 정보

### 워크플로우 파일 위치

```
.github/workflows/docker-build.yml
```

### 빌드되는 이미지

| 이미지 | Docker Hub 태그 |
|--------|----------------|
| Backend | `zardkim/myappstore-backend:1.3.0-beta` |
| Backend | `zardkim/myappstore-backend:latest` |
| Frontend | `zardkim/myappstore-frontend:1.3.0-beta` |
| Frontend | `zardkim/myappstore-frontend:latest` |

### 환경 변수

워크플로우에서 사용하는 환경 변수:

```yaml
env:
  DOCKER_USERNAME: zardkim
  BACKEND_IMAGE: zardkim/myappstore-backend
  FRONTEND_IMAGE: zardkim/myappstore-frontend
```

---

## 🎯 버전 업데이트 방법

새 버전을 배포하려면:

### 방법 1: 태그 푸시 (권장)

```bash
# 새 버전 태그 생성
git tag v1.4.0
git push origin v1.4.0

# 자동으로 다음 이미지가 빌드됩니다:
# - zardkim/myappstore-backend:1.4.0
# - zardkim/myappstore-frontend:1.4.0
# - latest 태그도 함께 업데이트
```

### 방법 2: 수동 실행

1. GitHub → **Actions** → **Build and Push Docker Images**
2. **Run workflow** 클릭
3. Version 입력: `1.4.0`
4. **Run workflow** 클릭

### 방법 3: 코드 변경 후 푸시

```bash
# 워크플로우 파일의 기본 버전 수정
# .github/workflows/docker-build.yml 파일에서:
echo "version=1.4.0" >> $GITHUB_OUTPUT

# main 브랜치에 푸시
git add .
git commit -m "chore: Update version to 1.4.0"
git push origin main
```

---

## 🛠️ 문제 해결

### 빌드 실패 시

1. **Actions 탭에서 에러 로그 확인**
   - 빨간색으로 표시된 단계 클릭
   - 에러 메시지 확인

2. **일반적인 에러**

   **Docker Hub 로그인 실패:**
   ```
   Error: unauthorized: incorrect username or password
   ```
   → GitHub Secrets의 `DOCKER_USERNAME`, `DOCKER_PASSWORD` 확인

   **이미지 푸시 권한 없음:**
   ```
   Error: denied: requested access to the resource is denied
   ```
   → Docker Hub에서 저장소가 생성되어 있는지 확인
   → Access Token 권한이 `Read, Write, Delete`인지 확인

   **Dockerfile 에러:**
   ```
   Error: failed to solve: failed to read dockerfile
   ```
   → backend/Dockerfile, frontend/Dockerfile 파일 존재 확인

### 빌드는 성공했지만 이미지가 안 보일 때

1. Docker Hub 새로고침
2. 저장소가 Private으로 설정되어 있는지 확인
3. 태그 탭에서 최신 태그 확인

---

## 🔒 보안 주의사항

### GitHub Secrets 관리

- ✅ Docker Hub Access Token은 **절대 코드에 포함하지 마세요**
- ✅ Access Token은 GitHub Secrets에만 저장
- ✅ 주기적으로 Access Token 갱신 (6개월마다 권장)
- ✅ 불필요한 권한은 부여하지 않기

### Access Token 갱신

1. Docker Hub → Account Settings → Security
2. 기존 토큰 **Delete**
3. 새 토큰 **Generate**
4. GitHub Secrets의 `DOCKER_PASSWORD` 업데이트

---

## 📈 빌드 통계

GitHub Actions는 다음 정보를 제공합니다:

- ✅ 빌드 시간
- ✅ 이미지 크기
- ✅ 캐시 사용률
- ✅ 성공/실패 이력

**Actions** 탭에서 확인 가능합니다.

---

## 🎉 완료!

이제 GitHub에 코드를 푸시하면 자동으로 Docker 이미지가 빌드되고 Docker Hub에 배포됩니다!

**다음 단계:**
- 사용자들은 `docker-compose up -d` 명령으로 최신 이미지를 바로 사용할 수 있습니다
- 새 버전 배포 시 태그만 푸시하면 자동 빌드됩니다

---

## 📞 지원

문제가 발생하면:
- **GitHub Issues**: https://github.com/zardkim/my-appstore/issues
- **Actions 로그**: GitHub → Actions 탭에서 에러 로그 확인
