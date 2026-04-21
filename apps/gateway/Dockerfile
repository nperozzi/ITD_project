FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    paho-mqtt==2.1.0 \
    "bleak==0.22.3" \
    pydantic==2.9.2 \
    pydantic-settings==2.6.1 \
    SQLAlchemy==2.0.38 \
    alembic==1.14.1

COPY src ./src
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations

ENV PYTHONPATH=/app/src
CMD ["python", "-m", "main"]
