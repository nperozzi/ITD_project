# Minimal Python base image.
FROM python:3.12-slim

# Directory where backend source code runs.
WORKDIR /src

# Copy dependency list first to improve Docker layer caching.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Start backend app when container starts.
ENTRYPOINT ["python", "backend.py"]