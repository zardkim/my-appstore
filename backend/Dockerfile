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

# Expose port
EXPOSE 8110

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run the application
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8110"]
