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
    curl \
    gosu && \
    update-ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 4. Create user first
RUN groupadd -g 1000 pixeltable && useradd -u 1000 -r -g pixeltable -m -d /home/pixeltable pixeltable

RUN mkdir -p /root/.cache/huggingface /home/pixeltable/.cache/huggingface && \
    chmod -R 777 /root/.cache/huggingface && \
    chown -R pixeltable:pixeltable /home/pixeltable/.cache


WORKDIR /app

# 5. Copy files and fix permissions BEFORE uv sync
COPY . /app
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    mkdir -p /app/.records /home/pixeltable/.pixeltable && \
    chown -R pixeltable:pixeltable /app /home/pixeltable

# 6. Switch to user BEFORE running uv sync
# This ensures the .venv is created by the user, for the user
# Note: We'll switch back to root for ENTRYPOINT, then back to pixeltable in the entrypoint script
USER pixeltable

# 7. Install dependencies as the non-root user
RUN uv sync --frozen --no-cache
RUN uv pip install certifi
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Switch back to root for entrypoint (it will switch to pixeltable user)
USER root

# Set entrypoint to fix permissions
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Run the FastMCP CLI
CMD ["python", "src/kubrick_mcp/server.py", "--port", "9090", "--host", "0.0.0.0", "--transport", "streamable-http"]