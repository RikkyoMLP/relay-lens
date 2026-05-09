FROM python:3.12-slim AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates unzip && \
    curl -fsSL https://bun.sh/install | bash && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# -- Frontend build --
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY index.html tsconfig.json vite.config.ts ./
COPY src/ src/
RUN bun run build

# -- Python deps --
COPY pyproject.toml uv.lock .python-version README.md ./
COPY hsi-utils/ hsi-utils/

RUN pip install --no-cache-dir uv && \
    uv sync --no-dev

# -- App code --
COPY server/ server/

# Create directories for user uploads
RUN mkdir -p input mask

# HF Spaces default port
EXPOSE 7860
CMD ["uv", "run", "--no-dev", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
