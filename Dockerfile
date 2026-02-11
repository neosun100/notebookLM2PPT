# Multi-stage build for smaller image size
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /build
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN pip install --no-cache-dir build && \
    python -m build --wheel && \
    pip wheel --no-cache-dir --wheel-dir /wheels fastapi uvicorn[standard] python-multipart jinja2 fastmcp PyMuPDF

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    pdf2svg \
    inkscape \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages from wheels
COPY --from=builder /build/dist/*.whl /wheels/
COPY --from=builder /wheels /wheels/
RUN pip install --no-cache-dir /wheels/*.whl && \
    rm -rf /wheels

# Create app directory
WORKDIR /app

# Copy application files
COPY src/ ./src/
COPY web/ ./web/
COPY mcp/ ./mcp/

# Create directories for uploads and outputs
RUN mkdir -p /tmp/pdf2ppt/uploads /tmp/pdf2ppt/outputs

# Expose port
EXPOSE 8100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8100/health || exit 1

# Start server
CMD ["python", "-m", "uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8100"]
