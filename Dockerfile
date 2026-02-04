# custom-metrics/Dockerfile
FROM --platform=linux/arm64/v8 python:3.13-slim-bookworm

WORKDIR /app

# Install system dependencies required for building some Python packages
RUN apt-get update && \
   apt-get install -y --no-install-recommends \
   libusb-1.0-0-dev python3-dev \
   libpango-1.0-0 libpangoft2-1.0-0 \
   libharfbuzz0b libfontconfig1 libfreetype6 \
   libxml2 libxslt1.1 libffi-dev \
   libcairo2 libgdk-pixbuf2.0-0 \
   && \
   rm -rf /var/lib/apt/lists/*

# Create config directory for credentials
RUN mkdir -p /app/config

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY src/ src/
COPY templates/ templates/

# Run the application
CMD ["python", "main.py"]
