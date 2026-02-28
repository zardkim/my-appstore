#!/bin/bash
# MyApp Store - Build & Release Script
# 사용법: ./build.sh [patch|minor|major] [--no-push] [--no-commit]
# 예시:
#   ./build.sh           # patch 버전 자동 증가 + 빌드 + 커밋 + 푸시
#   ./build.sh minor     # minor 버전 증가
#   ./build.sh --no-push # 푸시 없이 빌드+커밋만
#   ./build.sh --no-commit --no-push  # 빌드만

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
VERSION_FILE="$BACKEND_DIR/app/version.py"
PACKAGE_JSON="$FRONTEND_DIR/package.json"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.prod.yml"
DOCKER_USER="zardkim"

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

# 버전 파싱
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# 버전 증가
case $BUMP_TYPE in
  major)
    MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
  minor)
    MINOR=$((MINOR + 1)); PATCH=0 ;;
  patch)
    PATCH=$((PATCH + 1)) ;;
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
# (docker-compose.prod.yml은 :latest 태그 고정 — 시놀로지 업데이트 감지용)

# Git 커밋 해시 가져오기 (커밋 전이므로 현재 HEAD)
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "")

# 백엔드 Docker 빌드
echo ""
echo "=== 백엔드 빌드 중... ==="
docker build \
  --build-arg VERSION="$NEW_VERSION" \
  --build-arg BUILD_DATE="$BUILD_DATE" \
  --build-arg VCS_REF="$GIT_COMMIT" \
  -t "${DOCKER_USER}/myappstore-backend:${NEW_VERSION}" \
  -t "${DOCKER_USER}/myappstore-backend:latest" \
  "$BACKEND_DIR"
echo "백엔드 빌드 완료"

# 프론트엔드 Docker 빌드
echo ""
echo "=== 프론트엔드 빌드 중... ==="
docker build \
  --build-arg VERSION="$NEW_VERSION" \
  --build-arg BUILD_DATE="$BUILD_DATE" \
  --build-arg VCS_REF="$GIT_COMMIT" \
  -t "${DOCKER_USER}/myappstore-frontend:${NEW_VERSION}" \
  -t "${DOCKER_USER}/myappstore-frontend:latest" \
  "$FRONTEND_DIR"
echo "프론트엔드 빌드 완료"

# Git 커밋 + 태그
if [ "$DO_COMMIT" = true ]; then
  echo ""
  echo "=== Git 커밋 중... ==="
  cd "$SCRIPT_DIR"
  git add -A
  git commit -m "release: v${NEW_VERSION}

- Version bump to ${NEW_VERSION}
- Build date: ${BUILD_DATE}
- Docker images: backend:${NEW_VERSION}, frontend:${NEW_VERSION} (latest 태그 동시 푸시)"
  echo "Git 커밋 완료"

  # 태그 생성
  git tag "v${NEW_VERSION}"
  echo "Git 태그 생성: v${NEW_VERSION}"
fi

# Docker Hub 푸시 + GitHub 푸시
if [ "$DO_PUSH" = true ]; then
  echo ""
  echo "=== Docker Hub 푸시 중... ==="
  docker push "${DOCKER_USER}/myappstore-backend:${NEW_VERSION}"
  docker push "${DOCKER_USER}/myappstore-backend:latest"
  docker push "${DOCKER_USER}/myappstore-frontend:${NEW_VERSION}"
  docker push "${DOCKER_USER}/myappstore-frontend:latest"
  echo "Docker Hub 푸시 완료"

  # GitHub 커밋 + 태그 푸시
  echo ""
  echo "=== GitHub 푸시 중... ==="
  git push origin main
  echo "GitHub 커밋 푸시 완료: main"
  git push origin "v${NEW_VERSION}"
  echo "GitHub 태그 푸시 완료: v${NEW_VERSION}"
fi

echo ""
echo "=== 완료! ==="
echo "버전: $NEW_VERSION"
echo "이미지:"
echo "  - ${DOCKER_USER}/myappstore-backend:${NEW_VERSION}"
echo "  - ${DOCKER_USER}/myappstore-frontend:${NEW_VERSION}"
if [ "$DO_PUSH" = true ]; then
  echo "Docker Hub에 푸시됨 (latest + $NEW_VERSION 태그)"
fi
echo ""
echo "시놀로지 Container Manager:"
echo "  docker-compose.prod.yml은 :latest 태그를 사용합니다."
echo "  Container Manager → 프로젝트 → 업데이트 버튼 클릭 시"
echo "  로컬 :latest digest vs Docker Hub :latest digest 비교로 업데이트 감지됩니다."
