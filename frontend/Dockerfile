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

# 빌드된 파일 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 노출
EXPOSE 5900

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
