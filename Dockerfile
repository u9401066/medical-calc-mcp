# Medical Calculator MCP Server
# Supports both STDIO (local) and SSE (remote) modes

FROM python:3.11-slim

LABEL maintainer="Medical-Calc-MCP"
LABEL description="Medical Calculator MCP Server for AI Agent Integration"
LABEL version="1.2.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy source code
COPY src/ ./src/

# Install the project
RUN uv sync --frozen

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mcpuser
RUN chown -R mcpuser:mcpuser /app
USER mcpuser

# Environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MCP_MODE=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

# Expose port for SSE mode
EXPOSE 8000

# Health check using /health endpoint (custom endpoint for liveness probes)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -sf http://localhost:${MCP_PORT}/health -o /dev/null -m 5 || exit 1

# Default command: Run in SSE mode
CMD ["python", "-m", "src.main", "--mode", "sse", "--host", "0.0.0.0", "--port", "8000"]
