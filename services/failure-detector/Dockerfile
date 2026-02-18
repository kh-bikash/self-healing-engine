FROM python:3.9-slim

WORKDIR /app

COPY ./shared /app/shared
COPY ./services/failure-detector /app/services/failure-detector

# Install dependencies
RUN pip install sqlalchemy asyncpg redis pydantic pydantic-settings

CMD ["python", "-m", "services.failure-detector.main"]
