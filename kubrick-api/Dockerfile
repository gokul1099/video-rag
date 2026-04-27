FROM python:3.13-slim

ENV PYTHONPATH=/app/src
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && \
    apt-get install -y ffmpeg libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only dependency files for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (cached until lock file changes)
RUN uv sync --frozen

# Copy source code (changes frequently)
COPY . .

# Install package in editable mode
RUN uv pip install -e .

CMD ["/app/.venv/bin/python", "src/kubrick_api/api.py", "--port", "8080", "--host", "0.0.0.0"]
