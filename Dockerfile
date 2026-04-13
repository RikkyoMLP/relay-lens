FROM python:3.12-slim AS base

# Install Node.js 24 for frontend build
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g pnpm@10 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# -- Frontend build --
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY index.html tsconfig.json vite.config.ts ./
COPY src/ src/
RUN pnpm build

# -- Python deps --
COPY pyproject.toml uv.lock .python-version ./
COPY hsi-utils/ hsi-utils/

RUN pip install --no-cache-dir uv && \
    uv sync --no-dev --no-editable

# -- App code --
COPY server/ server/

# Create directories for user uploads
RUN mkdir -p input mask

# HF Spaces default port
EXPOSE 7860
CMD ["uv", "run", "--no-dev", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
