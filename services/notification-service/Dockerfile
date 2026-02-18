FROM python:3.9-slim

WORKDIR /app

COPY ./shared /app/shared
COPY ./services/notification-service /app/services/notification-service

# Install dependencies
RUN pip install sqlalchemy asyncpg redis pydantic pydantic-settings

CMD ["python", "-m", "services.notification-service.main"]
