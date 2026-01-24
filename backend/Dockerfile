FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create static directory for icons
RUN mkdir -p /app/static/icons

# Copy application code
COPY ./app ./app

# Expose port
EXPOSE 8110

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8110"]
