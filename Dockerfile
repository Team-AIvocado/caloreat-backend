# ---- Builder Stage ----
FROM python:3.12-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ---- Final Stage ----
FROM python:3.12-slim-bookworm AS final

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and set up app directory
RUN useradd -m app_user && mkdir -p /home/app_user/app && chown -R app_user:app_user /home/app_user

# Switch to the non-root user
USER app_user
WORKDIR /home/app_user/app

# Copy built wheels and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Add user's local bin to PATH
ENV PATH="/home/app_user/.local/bin:${PATH}"

# Copy application code
COPY --chown=app_user:app_user ./app ./app
COPY --chown=app_user:app_user main.py .
COPY --chown=app_user:app_user alembic.ini .
COPY --chown=app_user:app_user ./alembic ./alembic
# Expose the port the app runs on
EXPOSE 8000

# Run the application via CMD (can be overridden)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]