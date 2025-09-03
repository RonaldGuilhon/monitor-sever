# Server Monitor - Dockerfile
# Multi-stage build for optimized container size

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    MONITOR_CONFIG_DIR="/app/config" \
    MONITOR_DATA_DIR="/app/data" \
    MONITOR_LOGS_DIR="/app/logs"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r monitor \
    && useradd -r -g monitor -d /app -s /bin/bash monitor

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p config data logs && \
    chown -R monitor:monitor /app

# Copy application code
COPY --chown=monitor:monitor src/ ./src/
COPY --chown=monitor:monitor run.py .
COPY --chown=monitor:monitor setup.py .
COPY --chown=monitor:monitor README.md .

# Copy default configuration files
COPY --chown=monitor:monitor .env.example .env

# Install the application
RUN pip install -e .

# Switch to non-root user
USER monitor

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/src'); from monitor_server.core.monitor import ServerMonitor; print('OK')" || exit 1

# Expose port for web interface (if implemented in future)
EXPOSE 8080

# Default command
CMD ["python", "run.py", "--mode", "console"]

# Labels for metadata
LABEL maintainer="Server Monitor Team <admin@example.com>" \
      version="1.0.0" \
      description="Server Monitor - Network and Service Monitoring Tool" \
      org.opencontainers.image.title="Server Monitor" \
      org.opencontainers.image.description="A comprehensive server monitoring application" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="Server Monitor Team" \
      org.opencontainers.image.licenses="MIT"