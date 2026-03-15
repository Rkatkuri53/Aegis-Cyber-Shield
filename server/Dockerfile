# Aegis Backend Dockerfile (Production-Grade)
FROM python:3.11-slim

WORKDIR /app

# Set standard environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the Cloud Run default port
EXPOSE 8080

# Cloud Run injects the PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
