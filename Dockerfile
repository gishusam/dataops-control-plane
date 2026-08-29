FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY requirements.api.txt .

RUN pip install \
    --no-cache-dir \
    -r requirements.api.txt

COPY src ./src
COPY dashboard ./dashboard

EXPOSE 8080

CMD ["sh", "-c", "uvicorn src.control_plane.api:create_app --factory --host 0.0.0.0 --port ${PORT}"]
