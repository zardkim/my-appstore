FROM python:3.11-slim

WORKDIR /app

# Build arguments for image metadata
ARG VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# OCI standard labels (Synology Container Manager uses these for update detection)
LABEL org.opencontainers.image.title="MyAppStore Backend"
LABEL org.opencontainers.image.description="NAS-based personal software library management system"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.source="https://github.com/zardkim/my-appstore"
LABEL org.opencontainers.image.url="https://hub.docker.com/r/zardkim/myappstore-backend"
LABEL maintainer="zardkim"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create static directory for icons
RUN mkdir -p /app/static/icons

# Copy application code
COPY ./app ./app

# Copy Alembic migrations
# 이것이 없으면 컨테이너 안에서 alembic 명령이 동작하지 않는다
# ("No config file 'alembic.ini' found"). Dockerfile.prod 에는 있었으나
# CI 가 빌드하는 이 파일에는 빠져 있어서, 배포 환경에서는 마이그레이션을
# 실행할 수 없었고 entrypoint.sh 가 DDL 을 직접 짜 넣고 있었다.
COPY alembic.ini ./alembic.ini
COPY ./alembic ./alembic

# Expose port
EXPOSE 8110

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run the application
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8110"]
