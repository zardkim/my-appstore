#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME="zardkim"
BACKEND_IMAGE="myappstore-backend"
FRONTEND_IMAGE="myappstore-frontend"

# Get version from argument or prompt
if [ -z "$1" ]; then
  echo -e "${YELLOW}No version provided.${NC}"
  read -p "Enter version (e.g., 1.5.3): " VERSION
  if [ -z "$VERSION" ]; then
    echo -e "${RED}Error: Version is required${NC}"
    exit 1
  fi
else
  VERSION=$1
fi

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo -e "${RED}Error: Invalid version format. Must be X.Y.Z (e.g., 1.5.3)${NC}"
  exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}MyApp Store Build & Deploy${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Version: ${GREEN}${VERSION}${NC}"
echo ""

# Step 1: Update version files
echo -e "${YELLOW}[1/6] Updating version files...${NC}"
bash scripts/update-version.sh "$VERSION"
echo ""

# Step 2: Build backend Docker image
echo -e "${YELLOW}[2/6] Building backend Docker image...${NC}"
docker build \
  --no-cache \
  -t "${DOCKER_USERNAME}/${BACKEND_IMAGE}:v${VERSION}" \
  -t "${DOCKER_USERNAME}/${BACKEND_IMAGE}:latest" \
  -f backend/Dockerfile.prod \
  backend/
echo -e "${GREEN}✓ Backend image built${NC}"
echo ""

# Step 3: Build frontend Docker image
echo -e "${YELLOW}[3/6] Building frontend Docker image...${NC}"
docker build \
  --no-cache \
  -t "${DOCKER_USERNAME}/${FRONTEND_IMAGE}:v${VERSION}" \
  -t "${DOCKER_USERNAME}/${FRONTEND_IMAGE}:latest" \
  -f frontend/Dockerfile.prod \
  frontend/
echo -e "${GREEN}✓ Frontend image built${NC}"
echo ""

# Step 4: Push images to Docker Hub
echo -e "${YELLOW}[4/6] Pushing images to Docker Hub...${NC}"
docker push "${DOCKER_USERNAME}/${BACKEND_IMAGE}:v${VERSION}"
docker push "${DOCKER_USERNAME}/${BACKEND_IMAGE}:latest"
echo -e "${GREEN}✓ Backend images pushed${NC}"

docker push "${DOCKER_USERNAME}/${FRONTEND_IMAGE}:v${VERSION}"
docker push "${DOCKER_USERNAME}/${FRONTEND_IMAGE}:latest"
echo -e "${GREEN}✓ Frontend images pushed${NC}"
echo ""

# Step 5: Git commit
echo -e "${YELLOW}[5/6] Creating git commit...${NC}"
git add \
  frontend/package.json \
  frontend/src/version.js \
  backend/app/version.py \
  frontend/src/components/layout/Footer.vue \
  frontend/src/components/layout/MainLayout.vue \
  frontend/src/views/Settings.vue \
  frontend/src/locales/ko.js \
  frontend/src/locales/en.js \
  frontend/vite.config.js

git commit -m "chore: Release v${VERSION}

- Update version to ${VERSION}
- Add automatic version injection from package.json
- Fix mobile UI: reduce menu height and add search icon
- Update all version files automatically

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

echo -e "${GREEN}✓ Git commit created${NC}"
echo ""

# Step 6: Create git tag
echo -e "${YELLOW}[6/6] Creating git tag and pushing...${NC}"
git tag -a "v${VERSION}" -m "Release v${VERSION}

Features:
- Automatic version management from package.json
- Mobile UI improvements (menu height, search icon)
- Korean language metadata support
- Dual-language image search

Docker Images:
- ${DOCKER_USERNAME}/${BACKEND_IMAGE}:v${VERSION}
- ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:v${VERSION}"

git push origin main
git push origin "v${VERSION}"
echo -e "${GREEN}✓ Git tag created and pushed${NC}"
echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Build & Deploy Completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Version: ${GREEN}v${VERSION}${NC}"
echo ""
echo "Docker Images:"
echo "  Backend:  ${DOCKER_USERNAME}/${BACKEND_IMAGE}:v${VERSION}"
echo "  Frontend: ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:v${VERSION}"
echo ""
echo "GitHub:"
echo "  Repository: https://github.com/zardkim/my-appstore"
echo "  Tag: https://github.com/zardkim/my-appstore/releases/tag/v${VERSION}"
echo ""
echo "Docker Hub:"
echo "  Backend:  https://hub.docker.com/r/${DOCKER_USERNAME}/${BACKEND_IMAGE}"
echo "  Frontend: https://hub.docker.com/r/${DOCKER_USERNAME}/${FRONTEND_IMAGE}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Update deployment: docker-compose pull && docker-compose up -d"
echo "  2. Create GitHub release with release notes"
