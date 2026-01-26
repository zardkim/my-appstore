#!/bin/bash
# MyApp Store 버전 확인 스크립트

echo "=========================================="
echo "MyApp Store - Current Version"
echo "=========================================="
echo ""

# 컨테이너가 실행 중인지 확인
if ! docker ps | grep -q myapp-backend; then
    echo "❌ Backend container is not running"
    echo ""
    echo "Start containers with:"
    echo "  docker-compose up -d"
    exit 1
fi

echo "📦 Running Containers:"
echo ""

# Backend 버전
BACKEND_IMAGE=$(docker inspect myapp-backend --format='{{.Config.Image}}')
BACKEND_CREATED=$(docker inspect myapp-backend --format='{{.Created}}' | cut -d'T' -f1)
echo "Backend:   $BACKEND_IMAGE"
echo "Created:   $BACKEND_CREATED"
echo ""

# Frontend 버전
FRONTEND_IMAGE=$(docker inspect myapp-frontend --format='{{.Config.Image}}')
FRONTEND_CREATED=$(docker inspect myapp-frontend --format='{{.Created}}' | cut -d'T' -f1)
echo "Frontend:  $FRONTEND_IMAGE"
echo "Created:   $FRONTEND_CREATED"
echo ""

# Database 버전
DB_IMAGE=$(docker inspect myapp-db --format='{{.Config.Image}}')
echo "Database:  $DB_IMAGE"
echo ""

echo "=========================================="
echo ""
echo "💡 Check for updates on Docker Hub:"
echo "   https://hub.docker.com/r/zardkim/myappstore-backend/tags"
echo "   https://hub.docker.com/r/zardkim/myappstore-frontend/tags"
echo ""
echo "🔄 Update to latest version:"
echo "   docker-compose pull"
echo "   docker-compose up -d"
echo ""
echo "=========================================="
