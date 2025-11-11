FROM python:3.12-slim

# Lightweight container for running the FastHTML app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime deps, build deps only for installation then remove them
COPY requirements.txt ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential curl python3-distutils python3-setuptools \
       libjpeg-dev zlib1g-dev \
    && pip install --no-cache-dir -r requirements.txt uvicorn[standard] \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the application
COPY . /app

# Expose HTTP port
EXPOSE 8000

# Default command: run with uvicorn for production-ish usage
CMD ["python", "main.py"]
