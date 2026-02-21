FROM python:3.12-slim
WORKDIR /app
RUN pip install paho-mqtt
COPY tag_sim.py .
CMD ["python", "tag_sim.py"]