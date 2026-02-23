# Build stage - Node.js에서 빌드
FROM node:20-alpine AS builder

WORKDIR /app

# package.json과 lock 파일 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci

# 소스 코드 복사
COPY . .

# 빌드
RUN npm run build

# Production stage - Nginx에서 서빙
FROM nginx:alpine

# Build arguments for image metadata
ARG VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# OCI standard labels (Synology Container Manager uses these for update detection)
LABEL org.opencontainers.image.title="MyAppStore Frontend"
LABEL org.opencontainers.image.description="NAS-based personal software library management system"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.source="https://github.com/zardkim/my-appstore"
LABEL org.opencontainers.image.url="https://hub.docker.com/r/zardkim/myappstore-frontend"
LABEL maintainer="zardkim"

# 빌드된 파일 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 노출
EXPOSE 5900

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
