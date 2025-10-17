# --- Stage 1: Builder ---
# This stage installs dependencies, including those that need to be compiled.
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build-time system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a wheelhouse
WORKDIR /wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# --- Stage 2: Final ---
# This is the final, lightweight image.
FROM python:3.11-slim

# Set the working directory for the entire project
WORKDIR /app

# Copy pre-built wheels from the builder stage and install them
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache --find-links=/wheels -r requirements.txt
RUN rm -rf /wheels

# Create necessary directories
RUN mkdir -p /app/django_app/logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "django_app/manage.py", "runserver", "0.0.0.0:8000"]