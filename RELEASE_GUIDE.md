# 🚀 빠른 릴리스 가이드

## 일상적인 개발 워크플로우

### 1. 작업 시작

```bash
git checkout -b feature/my-feature
```

### 2. 코드 작성 및 커밋

```bash
# Conventional Commits 형식 사용
git add .
git commit -m "feat(products): add export to CSV functionality"

# 또는
git commit -m "fix(auth): resolve session timeout issue"
```

### 3. 메인 브랜치에 머지

```bash
git checkout main
git merge feature/my-feature
git push origin main
```

## 릴리스 만들기

### 자동 릴리스 (권장)

```bash
# 루트 디렉토리에서
npm run release
```

이 명령은 자동으로:
- 📋 커밋 분석
- 🔢 버전 결정
- 📝 CHANGELOG 업데이트
- 📦 모든 버전 파일 업데이트
- 🏷️ Git 태그 생성

### 태그 푸시

```bash
git push --follow-tags origin main
```

### Docker 이미지 빌드

```bash
# 현재 버전 확인
cat package.json | grep version

# 이미지 빌드 (예: 1.1.0)
docker-compose build
docker tag myappstore:latest myappstore:1.1.0
```

## 커밋 타입 치트시트

| 작업 | 커밋 타입 | 예시 |
|------|----------|------|
| 새 기능 | `feat` | `feat(ui): add dark mode` |
| 버그 수정 | `fix` | `fix(api): resolve CORS issue` |
| 문서 | `docs` | `docs: update README` |
| 리팩토링 | `refactor` | `refactor(db): optimize query` |
| 성능 | `perf` | `perf(scanner): improve speed` |
| 테스트 | `test` | `test(auth): add login tests` |
| 빌드 | `chore` | `chore: update dependencies` |

## 주요 명령어

```bash
# 일반 릴리스 (자동 버전 결정)
npm run release

# Patch 릴리스 (1.0.0 → 1.0.1)
npm run release:patch

# Minor 릴리스 (1.0.1 → 1.1.0)
npm run release:minor

# Major 릴리스 (1.1.0 → 2.0.0)
npm run release:major

# Dry run (테스트)
npx standard-version --dry-run
```

## 버전 확인

```bash
# API로 확인
curl http://localhost:8100/api/version

# 파일로 확인
cat package.json | grep version
cat backend/app/version.py | grep __version__
```

## 문제 해결

**"No commits since last release"**
- Conventional Commits 형식의 커밋이 없습니다
- feat, fix 등의 타입을 사용하세요

**버전이 증가하지 않음**
- 커밋 메시지 형식 확인
- `npx standard-version --dry-run`으로 테스트

---

더 자세한 내용은 `VERSION_MANAGEMENT.md`를 참조하세요.
