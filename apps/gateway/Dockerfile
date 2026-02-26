# Minimal Python runtime image.
FROM python:3.12-slim

# App files live here inside container.
WORKDIR /app

# Install MQTT client library used by gateway.py.
RUN pip install paho-mqtt

# Copy service source into image.
COPY gateway.py .

# Start gateway service.
CMD ["python", "gateway.py"]