FROM python:3.9-slim

WORKDIR /app

COPY ./shared /app/shared
COPY ./services/task-worker /app/services/task-worker

# Install dependencies
RUN pip install sqlalchemy asyncpg redis pydantic pydantic-settings

CMD ["python", "-m", "services.task-worker.main"]
