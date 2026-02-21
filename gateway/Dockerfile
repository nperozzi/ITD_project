FROM python:3.12-slim
WORKDIR /app
RUN pip install paho-mqtt
COPY gateway.py .
CMD ["python", "gateway.py"]