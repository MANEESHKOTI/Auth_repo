# --- Stage 1: Builder ---
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.11-slim
WORKDIR /app
ENV TZ=UTC

# Install cron and timezone tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Configure Timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy python dependencies
COPY --from=builder /install /usr/local

# Copy application code (includes scripts/ and api.py)
COPY . .

# Setup Cron Job
# We copy the file from your local 'cron' folder to the system location
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

# Start Cron and API
CMD ["sh", "-c", "cron && uvicorn api:app --host 0.0.0.0 --port 8080"]