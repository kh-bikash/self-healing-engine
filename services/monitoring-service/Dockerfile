FROM python:3.9-slim

WORKDIR /app

COPY ./shared /app/shared
COPY ./services/monitoring-service /app/services/monitoring-service

# Install dependencies
RUN pip install sqlalchemy asyncpg redis pydantic pydantic-settings

CMD ["python", "-m", "services.monitoring-service.main"]
