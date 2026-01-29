# 🏷️ 버전 관리 가이드 (Version Management Guide)

MyApp Store의 버전 관리 시스템 사용 가이드입니다.

## 📋 현재 버전

**v1.0.0** (2025-12-29)

- Frontend: 1.0.0
- Backend: 1.0.0

## 🎯 버전 관리 전략

### Semantic Versioning 2.0.0

이 프로젝트는 [Semantic Versioning](https://semver.org/)을 따릅니다.

**버전 형식**: `MAJOR.MINOR.PATCH` (예: 1.0.0)

- **MAJOR** (1.x.x): 호환되지 않는 API 변경
- **MINOR** (x.1.x): 하위 호환되는 기능 추가
- **PATCH** (x.x.1): 하위 호환되는 버그 수정

### 예시

| 변경 내용 | 버전 증가 | 예시 |
|---------|---------|------|
| 버그 수정 | PATCH | 1.0.0 → 1.0.1 |
| 새로운 기능 추가 | MINOR | 1.0.1 → 1.1.0 |
| API 변경 (호환성 깨짐) | MAJOR | 1.1.0 → 2.0.0 |

## 📝 Conventional Commits

### 커밋 메시지 형식

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 커밋 타입

| Type | 설명 | 버전 증가 | CHANGELOG 표시 |
|------|------|----------|--------------|
| `feat` | 새로운 기능 | MINOR | ✅ Features |
| `fix` | 버그 수정 | PATCH | ✅ Bug Fixes |
| `docs` | 문서 변경 | - | ✅ Documentation |
| `style` | 코드 포맷팅 | - | ❌ 숨김 |
| `refactor` | 리팩토링 | - | ✅ Code Refactoring |
| `perf` | 성능 개선 | PATCH | ✅ Performance |
| `test` | 테스트 추가 | - | ❌ 숨김 |
| `chore` | 빌드/도구 변경 | - | ✅ Maintenance |

### BREAKING CHANGE

호환성이 깨지는 변경의 경우 MAJOR 버전이 증가합니다.

```bash
feat!: migrate to Vue 3

BREAKING CHANGE: Vue 2 is no longer supported
```

또는:

```bash
feat: add new authentication system

BREAKING CHANGE: Old auth API endpoints have been removed
```

### 커밋 메시지 예시

**Good ✅**:
```bash
feat(auth): add OAuth2 login support
fix(ui): resolve mobile menu overflow issue
docs: update installation guide
refactor(api): simplify user query logic
```

**Bad ❌**:
```bash
update code
fix bug
WIP
asdf
```

## 🚀 릴리스 프로세스

### 1. 개발 작업

```bash
# 기능 개발
git checkout -b feature/my-new-feature
# ... 작업 ...
git add .
git commit -m "feat(products): add batch import functionality"

# 버그 수정
git checkout -b fix/login-issue
# ... 작업 ...
git commit -m "fix(auth): resolve token expiration bug"
```

### 2. 메인 브랜치에 머지

```bash
git checkout main
git merge feature/my-new-feature
git push origin main
```

### 3. 버전 릴리스 (자동)

```bash
# 루트 디렉토리에서 실행
npm run release
```

이 명령은 자동으로:
1. ✅ 커밋 로그 분석
2. ✅ 버전 번호 결정 (SemVer 기준)
3. ✅ CHANGELOG.md 생성/업데이트
4. ✅ package.json 버전 업데이트
5. ✅ frontend/package.json 버전 업데이트
6. ✅ backend/app/version.py 버전 업데이트
7. ✅ Git 커밋 생성 (`chore(release): 1.1.0`)
8. ✅ Git 태그 생성 (`v1.1.0`)

### 4. 태그 푸시

```bash
git push --follow-tags origin main
```

### 5. Docker 이미지 빌드 (선택적)

```bash
# 버전 태그로 빌드
docker build -t myappstore:1.1.0 .
docker tag myappstore:1.1.0 myappstore:1.1
docker tag myappstore:1.1.0 myappstore:1
docker tag myappstore:1.1.0 myappstore:latest

# Docker Hub에 푸시 (선택)
docker push myappstore:1.1.0
docker push myappstore:latest
```

## 🔧 수동 버전 제어

### 특정 버전으로 릴리스

```bash
# Patch 버전 증가 (1.0.0 → 1.0.1)
npm run release:patch

# Minor 버전 증가 (1.0.1 → 1.1.0)
npm run release:minor

# Major 버전 증가 (1.1.0 → 2.0.0)
npm run release:major
```

### 첫 릴리스 (태그 없이 버전만 설정)

```bash
npm run release:first
```

### Dry Run (실제 변경 없이 테스트)

```bash
npx standard-version --dry-run
```

## 📂 버전 정보 위치

### 프론트엔드
- `frontend/package.json` - version 필드

### 백엔드
- `backend/app/version.py` - `__version__` 변수
- API 엔드포인트:
  - `GET /api/version` - 기본 버전 정보
  - `GET /api/version/detailed` - 상세 버전 정보
  - `GET /api/health` - 헬스체크 + 버전

### 루트
- `package.json` - 전체 프로젝트 버전
- `CHANGELOG.md` - 버전별 변경사항

## 🐳 Docker 이미지 태깅 전략

### 태그 종류

1. **정확한 버전**: `myappstore:1.0.0`
2. **마이너 버전**: `myappstore:1.0`
3. **메이저 버전**: `myappstore:1`
4. **최신**: `myappstore:latest`

### 사용 예시

```yaml
# docker-compose.yml
services:
  backend:
    image: myappstore:1.0.0  # 정확한 버전 고정
    # 또는
    image: myappstore:1      # 메이저 버전 (자동 업데이트)
    # 또는
    image: myappstore:latest # 항상 최신 (권장하지 않음)
```

## 📋 체크리스트

### 릴리스 전

- [ ] 모든 테스트 통과
- [ ] 문서 업데이트 완료
- [ ] 환경 변수 변경사항 .env.example에 반영
- [ ] BREAKING CHANGE가 있다면 UPGRADE.md 작성

### 릴리스 후

- [ ] GitHub/GitLab에 태그 푸시됨 확인
- [ ] CHANGELOG.md 내용 확인
- [ ] Docker 이미지 빌드 및 테스트
- [ ] 프로덕션 배포
- [ ] Release Notes 작성 (GitHub Releases)

## 🔍 버전 확인 방법

### CLI

```bash
# 프론트엔드 버전
cat frontend/package.json | grep version

# 백엔드 버전
cat backend/app/version.py | grep __version__

# 전체 프로젝트 버전
cat package.json | grep version
```

### API

```bash
# 버전 정보 조회
curl http://localhost:8110/api/version

# 상세 버전 정보
curl http://localhost:8110/api/version/detailed

# 헬스체크 (버전 포함)
curl http://localhost:8110/api/health
```

### UI

Settings > 시스템 정보 섹션에서 확인 가능 (예정)

## 🛠️ 문제 해결

### "No commits since last release" 오류

새로운 커밋이 없으면 버전이 증가하지 않습니다. Conventional Commits 형식의 커밋을 먼저 생성하세요.

### Python 버전 파일이 업데이트되지 않음

`scripts/version-updater.js`가 올바르게 설정되었는지 확인하세요.

```bash
# 수동 확인
npx standard-version --dry-run
```

### Git 태그 충돌

```bash
# 로컬 태그 삭제
git tag -d v1.0.0

# 원격 태그 삭제 (주의!)
git push origin :refs/tags/v1.0.0
```

## 📚 참고 자료

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [standard-version](https://github.com/conventional-changelog/standard-version)
- [Keep a Changelog](https://keepachangelog.com/)

## 🤝 기여 가이드

버전 관리 시스템을 사용하여 프로젝트에 기여하려면:

1. Conventional Commits 형식으로 커밋
2. Pull Request 생성
3. 리뷰 및 머지 후 메인테이너가 릴리스 수행

---

**현재 버전**: v1.0.0
**마지막 업데이트**: 2025-12-29
