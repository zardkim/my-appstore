#!/bin/bash
# MyApp Store - Release Script
#
# 버전을 올리고 커밋 + 태그를 만든다. **이미지 빌드와 푸시는 하지 않는다.**
#
# 이미지는 GitHub Actions 가 만든다(.github/workflows/docker-build.yml).
# `v*` 태그가 push 되면 트리거되어 schema-check -> build-and-push 순으로 돌고
# Docker Hub 에 {버전}과 latest 로 푸시한다.
#
# 예전에는 이 스크립트도 로컬에서 빌드해 Docker Hub 에 푸시했다. 그러면 tag push 가
# CI 를 트리거해 **같은 태그를 다시 빌드해 덮어쓰기** 때문에, 같은 버전인데 서로 다른
# 바이너리가 도는 상태가 된다(1.4.69 에서 실제로 발생). 빌드는 CI 한 곳에서만 한다.
#
# 사용법: ./build.sh [patch|minor|major] [--no-push] [--no-commit]
#   ./build.sh                        patch 증가 + 커밋 + 태그 + push (CI 트리거)
#   ./build.sh minor                  minor 증가
#   ./build.sh --no-push              커밋/태그만, push 안 함 (CI 안 돎)
#   ./build.sh --no-commit --no-push   버전 파일만 수정

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
VERSION_FILE="$BACKEND_DIR/app/version.py"
PACKAGE_JSON="$FRONTEND_DIR/package.json"

# 인자 파싱
BUMP_TYPE="patch"
DO_PUSH=true
DO_COMMIT=true

for arg in "$@"; do
  case $arg in
    patch|minor|major) BUMP_TYPE="$arg" ;;
    --no-push)   DO_PUSH=false ;;
    --no-commit) DO_COMMIT=false ;;
  esac
done

# 현재 버전 읽기
CURRENT_VERSION=$(grep '__version__ = ' "$VERSION_FILE" | sed 's/__version__ = "\(.*\)"/\1/')
echo "현재 버전: $CURRENT_VERSION"

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

case $BUMP_TYPE in
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
  minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
  patch) PATCH=$((PATCH + 1)) ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
BUILD_DATE=$(date +%Y-%m-%d)
echo "새 버전: $NEW_VERSION"
echo "빌드 날짜: $BUILD_DATE"

# backend/app/version.py 업데이트
sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" "$VERSION_FILE"
sed -i "s/__version_info__ = (.*)/`printf '__version_info__ = (%d, %d, %d)' $MAJOR $MINOR $PATCH`/" "$VERSION_FILE"
sed -i "s/__build_date__ = \".*\"/__build_date__ = \"$BUILD_DATE\"/" "$VERSION_FILE"
echo "version.py 업데이트 완료"

# frontend/package.json 업데이트
sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" "$PACKAGE_JSON"
echo "package.json 업데이트 완료"
# (docker-compose*.yml 은 :latest 태그 고정 — 시놀로지 업데이트 감지용)

# Git 커밋 + 태그
if [ "$DO_COMMIT" = true ]; then
  echo ""
  echo "=== Git 커밋 중... ==="
  git add -A
  git commit -m "release: v${NEW_VERSION}

- Version bump to ${NEW_VERSION}
- Build date: ${BUILD_DATE}
- 이미지는 GitHub Actions 가 빌드해 Docker Hub 에 푸시한다 (latest 동시 갱신)"
  echo "Git 커밋 완료"

  git tag "v${NEW_VERSION}"
  echo "Git 태그 생성: v${NEW_VERSION}"
fi

# GitHub push (태그 push 가 CI 를 트리거한다)
if [ "$DO_PUSH" = true ]; then
  echo ""
  echo "=== GitHub 푸시 중... ==="
  git push origin main
  echo "커밋 푸시 완료: main"
  git push origin "v${NEW_VERSION}"
  echo "태그 푸시 완료: v${NEW_VERSION}"
  echo ""
  echo "GitHub Actions 가 이미지를 빌드합니다:"
  echo "  gh run watch   또는   https://github.com/zardkim/my-appstore/actions"
fi

echo ""
echo "=== 완료! ==="
echo "버전: $NEW_VERSION"
if [ "$DO_PUSH" = true ]; then
  echo "CI 빌드 완료 후 이미지:"
  echo "  zardkim/myappstore-backend:${NEW_VERSION}  (+ latest)"
  echo "  zardkim/myappstore-frontend:${NEW_VERSION} (+ latest)"
else
  echo "push 하지 않았습니다. 이미지를 만들려면:"
  echo "  git push origin main && git push origin v${NEW_VERSION}"
fi
echo ""
echo "배포: 시놀로지 Container Manager → 프로젝트 → 업데이트"
echo "  docker-compose.prod.yml 은 :latest 를 사용하므로"
echo "  로컬 :latest digest 와 Docker Hub :latest digest 비교로 업데이트가 감지됩니다."
