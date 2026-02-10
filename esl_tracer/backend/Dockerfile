FROM python:3.12-slim
WORKDIR /app
RUN pip install paho-mqtt
COPY backend.py .
CMD ["python", "backend.py"]