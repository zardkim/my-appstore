#!/bin/bash

# MyApp Store Docker Image Build and Push Script
# This script builds and pushes Docker images to Docker Hub

set -e  # Exit on error

# Configuration
VERSION="1.3.0-beta"
DOCKER_USERNAME="zardkim"
BACKEND_IMAGE="${DOCKER_USERNAME}/myappstore-backend"
FRONTEND_IMAGE="${DOCKER_USERNAME}/myappstore-frontend"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}MyApp Store Image Builder${NC}"
echo -e "${GREEN}Version: ${VERSION}${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if logged in to Docker Hub
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}Warning: You may not be logged in to Docker Hub${NC}"
    echo -e "${YELLOW}Run 'docker login' if push fails${NC}"
    echo ""
fi

# Build Backend Image
echo -e "${GREEN}[1/4] Building Backend Image...${NC}"
cd backend
docker build -t ${BACKEND_IMAGE}:${VERSION} -t ${BACKEND_IMAGE}:latest .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image built successfully${NC}"
else
    echo -e "${RED}✗ Backend image build failed${NC}"
    exit 1
fi
cd ..

# Build Frontend Image
echo -e "${GREEN}[2/4] Building Frontend Image...${NC}"
cd frontend
docker build -t ${FRONTEND_IMAGE}:${VERSION} -t ${FRONTEND_IMAGE}:latest .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image built successfully${NC}"
else
    echo -e "${RED}✗ Frontend image build failed${NC}"
    exit 1
fi
cd ..

echo ""
echo -e "${GREEN}Images built successfully!${NC}"
echo -e "Backend:  ${BACKEND_IMAGE}:${VERSION}"
echo -e "Frontend: ${FRONTEND_IMAGE}:${VERSION}"
echo ""

# Ask for confirmation before pushing
read -p "Push images to Docker Hub? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Push cancelled${NC}"
    exit 0
fi

# Push Backend Image
echo -e "${GREEN}[3/4] Pushing Backend Image...${NC}"
docker push ${BACKEND_IMAGE}:${VERSION}
docker push ${BACKEND_IMAGE}:latest
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image pushed successfully${NC}"
else
    echo -e "${RED}✗ Backend image push failed${NC}"
    exit 1
fi

# Push Frontend Image
echo -e "${GREEN}[4/4] Pushing Frontend Image...${NC}"
docker push ${FRONTEND_IMAGE}:${VERSION}
docker push ${FRONTEND_IMAGE}:latest
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image pushed successfully${NC}"
else
    echo -e "${RED}✗ Frontend image push failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ All images pushed successfully!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Backend Image:"
echo "  ${BACKEND_IMAGE}:${VERSION}"
echo "  ${BACKEND_IMAGE}:latest"
echo ""
echo "Frontend Image:"
echo "  ${FRONTEND_IMAGE}:${VERSION}"
echo "  ${FRONTEND_IMAGE}:latest"
echo ""
echo "Users can now pull these images using:"
echo "  docker-compose pull"
