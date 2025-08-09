FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies helpful for Pillow/TensorFlow and certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libgl1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the application code (including model file if present)
COPY . .

# Create default uploads directory (can be overridden via env)
RUN mkdir -p /app/uploads

EXPOSE 8000

# Default envs (can be overridden at runtime)
ENV HOST=0.0.0.0 \
    PORT=8000 \
    UPLOAD_DIR=/app/uploads

# Start with uvicorn; honor PORT env if provided by the platform
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]


