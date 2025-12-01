# =============================================================================
# Multi-Agent Tour Guide System - Production Dockerfile
# =============================================================================
# Multi-stage build for minimal image size and security
#
# Build: docker build -t tour-guide:latest .
# Run:   docker run -it --rm --env-file .env tour-guide:latest
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------------
FROM python:3.14-slim AS builder

# Install UV for fast dependency resolution
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files first (Docker layer caching)
# Include README.md as it's referenced in pyproject.toml
COPY pyproject.toml uv.lock README.md ./

# Copy source code needed for package build
COPY src/ ./src/

# Install dependencies into a virtual environment
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv sync --frozen --no-dev

# -----------------------------------------------------------------------------
# Stage 2: Runtime
# -----------------------------------------------------------------------------
FROM python:3.14-slim AS runtime

# Security: Create non-root user
RUN groupadd --gid 1000 tourguide && \
    useradd --uid 1000 --gid tourguide --shell /bin/bash --create-home tourguide

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=tourguide:tourguide . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    # Application defaults
    LOG_LEVEL=INFO \
    LLM_PROVIDER=anthropic

# Create data directories
RUN mkdir -p /app/data/cache /app/data/logs && \
    chown -R tourguide:tourguide /app/data

# Switch to non-root user
USER tourguide

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port (for API mode)
EXPOSE 8000

# Default command: CLI demo
CMD ["python", "main.py", "--demo", "--mode", "queue"]

# -----------------------------------------------------------------------------
# Labels (OCI standard)
# -----------------------------------------------------------------------------
LABEL org.opencontainers.image.title="Multi-Agent Tour Guide" \
      org.opencontainers.image.description="AI-powered personalized tour guide system" \
      org.opencontainers.image.version="2.0.0" \
      org.opencontainers.image.vendor="Tour Guide Team" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/yourusername/multi-agent-tour-guide"

