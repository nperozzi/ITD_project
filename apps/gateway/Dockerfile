# Minimal Python runtime image.
FROM python:3.12-slim

# Prevents Python from creating .pyc files. Keep docker cleaner.
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python to make the `printf()` wait in a buffer.
ENV PYTHONUNBUFFERED=1

# App files live here inside container.
WORKDIR /app

# Install libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       bluez \
       dbus \
       libglib2.0-0 \
       paho-mqtt \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY gateway.py .
COPY ble_adapter.py .

# Start gateway service.
CMD ["python", "gateway.py"]
