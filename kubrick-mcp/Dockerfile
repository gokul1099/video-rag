FROM python:3.11-bookworm

# 1. Setup paths
ENV PYTHONPATH=/app/src
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 2. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. System dependencies
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    ca-certificates \
    curl && \
    update-ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV HF_HUB_ENABLE_HF_TRANSFER=0
# 4. Create user first
RUN groupadd -r pixeltable && useradd -r -g pixeltable -m -d /home/pixeltable pixeltable

WORKDIR /app

# 5. Copy files and fix permissions BEFORE uv sync
COPY . /app
RUN mkdir -p /app/.records /home/pixeltable/.pixeltable && \
    chown -R pixeltable:pixeltable /app /home/pixeltable

# 6. Switch to user BEFORE running uv sync
# This ensures the .venv is created by the user, for the user
USER pixeltable

# 7. Install dependencies as the non-root user
RUN uv sync --frozen --no-cache
RUN uv pip install certifi
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Run the FastMCP CLI
CMD ["python", "src/kubrick_mcp/server.py", "--port", "9090", "--host", "0.0.0.0", "--transport", "streamable-http"]