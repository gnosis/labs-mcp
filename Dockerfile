FROM ghcr.io/astral-sh/uv:0.6.9-python3.10-bookworm@sha256:f4f319fff1ed098c4a195cdecd372e78cb97d0066faf3318fba4edfd1c7d522e as builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the project into the intermediate image
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
COPY run_server.py /app/run_server.py
COPY app.py /app/app.py

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

#FROM python:3.10-slim
FROM --platform=linux/amd64 python:3.10.14-bookworm AS runtime


# Copy the environment, but not the source code
#COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
CMD ["python","/app/run_server.py"]