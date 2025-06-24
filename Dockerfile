# Multi-stage Dockerfile: Build React UI + Flask Backend

# Stage 1: Build React UI
FROM node:18-alpine AS ui-builder

WORKDIR /app/ui

# Copy package files for dependency installation
COPY ui/package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy UI source code
COPY ui/ .

# Build the React application
RUN npm run build

# Stage 2: Flask Application with Built UI
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=api/app.py \
    FLASK_ENV=production \
    PORT=5000

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy built UI from first stage
COPY --from=ui-builder /app/ui/dist /app/dist

# Copy the Flask application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose the port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/ramayanam/kandas/1')" || exit 1

# Run the application with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "api.app:app"]