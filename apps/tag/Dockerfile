# Minimal Python runtime image.
FROM python:3.12-slim

# App files live here inside container.
WORKDIR /app

# Install MQTT client library used by tag_sim.py.
RUN pip install paho-mqtt

# Copy service source into image.
COPY . .

# Start tag simulator service.
CMD ["python", "tag_sim.py"]