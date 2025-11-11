FROM python:3.12-slim

# Lightweight container for running the FastHTML app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime deps, build deps only for installation then remove them
COPY requirements.txt ./
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         build-essential curl python3-setuptools python3-dev \
         libjpeg-dev zlib1g-dev \
     && python -m pip install --upgrade pip setuptools wheel \
     && pip install --no-cache-dir -r requirements.txt uvicorn[standard] \
     && apt-get purge -y --auto-remove build-essential \
     && rm -rf /var/lib/apt/lists/*

# Copy the application
COPY . /app

# Expose HTTP port
EXPOSE 5001


CMD ["python", "main.py"]
